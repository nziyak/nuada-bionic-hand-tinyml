#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Nuada TinyML - End-to-End Training & INT8 Quantization Pipeline
Author: Nuri Ziya Kırtepe
Project: Nuada Bionic Hand Movement Estimation via TinyML

Bu script:
1. Veri setini yükler (CSV formatında gerçek kayıtlar veya --mock bayrağıyla sentetik veriler).
2. 200 ms sliding window ve 19 feature'lı evrensel vektör çıkarımını uygular.
3. 1D-CNN veya Deep MLP modelini eğitir.
4. Test seti üzerinde Accuracy ve Sınıflandırma Metriklerini hesaplar.
5. Modeli TFLite INT8 Post-Training Quantization (PTQ) ile sıkıştırır.
6. ESP32-S3 C/C++ firmware için doğrudan kullanılabilir 'model_data.h' C header dosyasını üretir.

Kullanım Örnekleri:
    # Sentetik veri ile test ve C başlığı üretme:
    python3 train_tinyml.py --mock --model_type mlp --epochs 25 --quantize --output_header model_data.h

    # Gerçek veri klasörü ile eğitme:
    python3 train_tinyml.py --dataset_dir ../data/deneme/ --model_type cnn --epochs 40 --quantize
"""

import os
import sys
import math
import random
import argparse
from typing import List, Tuple, Any

# Nuada modülleri
from features import extract_window_features, generate_sliding_windows

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import tensorflow as tf
    from models import build_1d_cnn, build_deep_mlp
    HAS_TF = True
except ImportError:
    HAS_TF = False
    tf = None


GESTURE_CLASSES = {
    0: "REST (Dinlenme)",
    1: "FIST (Yumruk - FDS)",
    2: "PINCH/FLEX (Cimbiz - FPL)",
    3: "OPEN/EXT (El Acik - ED)",
    4: "POINT/DEV (Isaret - EPL)"
}


# ==============================================================================
# 1. SENTETİK (MOCK) VE GERÇEK VERİ YÜKLEYİCİ
# ==============================================================================

def generate_mock_dataset(num_samples_per_class: int = 150) -> Tuple[Any, Any, Any]:
    """
    Donanım hazır olmadan veya test amacıyla fizyolojik kas aktivasyonlarına
    uygun sentetik 4-kanallı EMG ve 3-eksenli IMU verisi üretir.

    Fizyolojik Kas Dağılımı:
    - Kanal 1: FDS (Flexor Digitorum Superficialis - Yumruk / Parmak Bükme)
    - Kanal 2: ED  (Extensor Digitorum - El Açma)
    - Kanal 3: FPL (Flexor Pollicis Longus - Başparmak / Cımbız)
    - Kanal 4: EPL (Extensor Pollicis Longus - İşaret / Başparmak Açma)
    """
    if not HAS_NUMPY:
        raise RuntimeError("NumPy kütüphanesi yüklü olmalıdır.")

    print(f"[MOCK] 5 sınıf için toplam {num_samples_per_class * 5} sentetik pencere üretiliyor...")
    x_emg_list = []
    x_imu_list = []
    y_list = []

    # 100 Hz'de 200 ms = 20 örnek
    window_len = 20

    for label in range(5):
        for _ in range(num_samples_per_class):
            emg_window = np.zeros((window_len, 4), dtype=np.float32)
            # Taban gürültüsü (0.05 - 0.15 V zarf seviyesi)
            emg_window += np.random.uniform(0.05, 0.15, (window_len, 4))

            # IMU baz değerleri (Yatay kol: ax~0.0, ay~0.0, az~1.0)
            imu_window = np.zeros((window_len, 3), dtype=np.float32)
            imu_window[:, 0] = np.random.normal(0.0, 0.05, window_len)
            imu_window[:, 1] = np.random.normal(0.0, 0.05, window_len)
            imu_window[:, 2] = np.random.normal(0.98, 0.03, window_len)

            if label == 0:  # REST
                pass
            elif label == 1:  # FIST -> CH1 (FDS) ve CH3 (FPL) yüksek
                emg_window[:, 0] += np.random.uniform(1.2, 2.5, window_len)
                emg_window[:, 2] += np.random.uniform(0.6, 1.4, window_len)
            elif label == 2:  # OPEN -> CH2 (ED) yüksek
                emg_window[:, 1] += np.random.uniform(1.3, 2.6, window_len)
                emg_window[:, 3] += np.random.uniform(0.4, 0.9, window_len)
            elif label == 3:  # PINCH -> CH3 (FPL) baskın, CH1 orta
                emg_window[:, 2] += np.random.uniform(1.4, 2.4, window_len)
                emg_window[:, 0] += np.random.uniform(0.3, 0.8, window_len)
            elif label == 4:  # POINT -> CH2 (ED) ve CH4 (EPL) yüksek
                emg_window[:, 1] += np.random.uniform(0.8, 1.8, window_len)
                emg_window[:, 3] += np.random.uniform(1.2, 2.2, window_len)

            x_emg_list.append(emg_window)
            x_imu_list.append(imu_window)
            y_list.append(label)

    x_emg = np.array(x_emg_list, dtype=np.float32)
    x_imu = np.array(x_imu_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    subjects = np.array(["mock"] * len(y))
    return x_emg, x_imu, y, subjects


def load_csv_dataset(dataset_dir: str, max_files: int = 16) -> Tuple[Any, Any, Any, Any]:
    """
    data/ klasöründeki CSV veya TXT (UCI formatı) kayıtlarını okur ve pencerelere ayırır.
    """
    if not HAS_NUMPY:
        raise RuntimeError("NumPy kütüphanesi gereklidir.")

    import glob
    import pandas as pd

    # Hem .csv hem .txt dosyalarını ara ve alfabetik sırala
    all_files = sorted(glob.glob(os.path.join(dataset_dir, "**/*.csv"), recursive=True) + \
                       glob.glob(os.path.join(dataset_dir, "**/*.txt"), recursive=True))
    # temp_repo veya README gibi gereksiz dosyaları hariç tut
    files = [f for f in all_files if "temp_repo" not in f and "readme" not in f.lower()][:max_files]

    if not files:
        raise FileNotFoundError(f"'{dataset_dir}' dizininde hiçbir .csv veya .txt veri dosyası bulunamadı!")

    print(f"[DATA] {len(files)} adet veri dosyası işleniyor (Hızlı eğitim için sınır: {max_files})...")
    all_emg_windows = []
    all_imu_windows = []
    all_labels = []
    all_subjects = []

    for fpath in files:
        try:
            # Hem virgülle hem tab/boşlukla ayrılmış dosyaları otomatik tanı
            df = pd.read_csv(fpath, sep=r'[\s,]+', engine='python')
        except Exception as e:
            continue

        subject_id = os.path.basename(os.path.dirname(fpath))

        # Sütun kontrolü (emg1..emg4, channel1..channel4, ax, ay, az, label/class)
        emg_cols = [c for c in df.columns if any(k in c.lower() for k in ["emg", "ch", "channel"])][:4]
        imu_cols = [c for c in df.columns if any(k in c.lower() for k in ["ax", "ay", "az", "acc"])][:3]
        label_cols = [c for c in df.columns if any(k in c.lower() for k in ["label", "class", "target"])]

        if not emg_cols or not label_cols:
            continue

        raw_emg = df[emg_cols].values
        # Otomatik voltaj ölçekleme: Eğer veriler ham V/mikrovolt seviyesindeyse (< 0.05 V), 1000 ile çarparak mV yap
        if np.max(np.abs(raw_emg)) < 0.05:
            raw_emg = raw_emg * 1000.0

        raw_imu = df[imu_cols].values if len(imu_cols) == 3 else np.zeros((len(df), 3), dtype=np.float32)
        raw_labels = df[label_cols[0]].values

        # UCI sEMG Benchmark tespiti ve doğru sınıf eşlemesi:
        # UCI formatında: 0=İşaretsiz/geçiş, 1=Dinlenme, 2=Yumruk, 3=Bilek Flexion, 4=Bilek Extension, 5=Radyal Sapma
        unique_lbls = set(np.unique(raw_labels))
        is_uci = (unique_lbls.intersection({5, 6, 7}) != set()) or (0 in unique_lbls and 1 in unique_lbls and 2 in unique_lbls and len(df) > 10000)

        if is_uci:
            # UCI verisi 1000 Hz'dir. 5'te 1 oranında alt-örnekleme (downsampling) ile 200 Hz'e indirilir.
            raw_emg = raw_emg[::5]
            raw_labels = raw_labels[::5]
            raw_imu = raw_imu[::5]
            uci_map = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}

            # 20 örnek pencere (100 ms @ 200 Hz), 8 örnek kayma adımı (40 ms)
            for i in range(0, len(raw_emg) - 20, 8):
                c = int(raw_labels[i + 10])
                if c in uci_map:
                    all_emg_windows.append(raw_emg[i:i + 20])
                    all_imu_windows.append(raw_imu[i:i + 20])
                    all_labels.append(uci_map[c])
                    all_subjects.append(subject_id)
        else:
            # Standart Nuada 100 Hz kayıt formatı (20 örnek = 200 ms)
            for i in range(0, len(raw_emg) - 20, 10):
                lbl = int(raw_labels[i + 10])
                if lbl in [0, 1, 2, 3, 4]:
                    all_emg_windows.append(raw_emg[i:i + 20])
                    all_imu_windows.append(raw_imu[i:i + 20])
                    all_labels.append(lbl)
                    all_subjects.append(subject_id)

    if not all_emg_windows:
        raise ValueError(f"'{dataset_dir}' içindeki dosyalardan geçerli veri penceresi çıkarılamadı!")

    return np.array(all_emg_windows, dtype=np.float32), np.array(all_imu_windows, dtype=np.float32), np.array(all_labels, dtype=np.int32), np.array(all_subjects)


# ==============================================================================
# 2. INT8 QUANTIZATION VE C HEADER ÜRETİMİ
# ==============================================================================

def export_c_header(tflite_bytes: bytes, output_path: str, model_name: str = "nuada_model"):
    """
    .tflite ikili model baytlarını C/C++ uyumlu 'model_data.h' header dosyasına dönüştürür.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    hex_lines = []
    line_bytes = []
    for i, byte in enumerate(tflite_bytes):
        line_bytes.append(f"0x{byte:02x}")
        if (i + 1) % 12 == 0:
            hex_lines.append("  " + ", ".join(line_bytes) + ",")
            line_bytes = []
    if line_bytes:
        hex_lines.append("  " + ", ".join(line_bytes))

    header_content = f"""// Bu dosya train_tinyml.py tarafindan otomatik olarak uretilmistir.
// Model: {model_name}
// Boyut: {len(tflite_bytes)} bayt

#ifndef {model_name.upper()}_DATA_H_
#define {model_name.upper()}_DATA_H_

#include <stdint.h>

#ifdef __cplusplus
extern "C" {{
#endif

alignas(16) const unsigned char g_{model_name}_data[] = {{
{chr(10).join(hex_lines)}
}};

const unsigned int g_{model_name}_len = {len(tflite_bytes)};

#ifdef __cplusplus
}}
#endif

#endif  // {model_name.upper()}_DATA_H_
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header_content)
    print(f"[OK] C header dosyasi basariyla olusturuldu: {output_path} ({len(tflite_bytes)} bayt)")


# ==============================================================================
# 3. ANA EĞİTİM VE ÇALIŞTIRMA BORU HATTI
# ==============================================================================

def run_pipeline(args):
    if not HAS_TF or not HAS_NUMPY:
        print("\n" + "="*70)
        print("  [BILGI] Gerekli Python kutuphaneleri (numpy, tensorflow) henuz yuklu degil!")
        print("="*70)
        print("  train_tinyml.py model eğitimi ve INT8 quantization")
        print("  yapmak icin TensorFlow ve NumPy kutuphanelerine ihtiyac duyar.")
        print("\n  Cozum (Sanal ortami kurun veya aktif edin):")
        print("    cd /home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml")
        print("    python3 -m venv venv")
        print("    source venv/bin/activate")
        print("    pip install -r requirements.txt")
        print("    python3 train_tinyml.py --mock --model_type mlp --epochs 15 --quantize --output_header model_data.h")
        print("="*70 + "\n")
        sys.exit(1)

    print("==================================================================")
    print("      NUADA TINYML MODEL EĞİTİM & INT8 QUANTIZATION HATTI         ")
    print("==================================================================")
    print(f"Model Tipi     : {args.model_type.upper()}")
    print(f"Epok Sayısı    : {args.epochs}")
    print(f"Batch Boyutu   : {args.batch_size}")
    print(f"Quantization   : {'Aktif (INT8 PTQ)' if args.quantize else 'Devre Dışı (Float32)'}")

    # 1. Veri Yükleme
    if args.mock or not args.dataset_dir:
        x_emg, x_imu, y, subjects = generate_mock_dataset(num_samples_per_class=args.samples_per_class)
    else:
        x_emg, x_imu, y, subjects = load_csv_dataset(args.dataset_dir)

    unique, counts = np.unique(y, return_counts=True)
    dist_str = ", ".join([f"{GESTURE_CLASSES.get(u, str(u)).split(' ')[0]}: {c}" for u, c in zip(unique, counts)])
    print(f"[VERI] Toplam Pencere Sayısı: {len(y)} ({dist_str})")

    # 2. Model Tipine Göre Giriş Matrisi Hazırlığı
    if args.model_type == "mlp":
        print("[ISLEM] 19 elemanlı evrensel feature vektörleri çıkarılıyor...")
        feat_list = []
        for i in range(len(x_emg)):
            feats = extract_window_features(x_emg[i], x_imu[i])
            feat_list.append(feats)
        X = np.array(feat_list, dtype=np.float32)
        # Z-score Normalizasyonu: Farklı sensör ve voltaj seviyelerini standart aralığa çeker
        X_mean = np.mean(X, axis=0)
        X_std = np.std(X, axis=0) + 1e-7
        X = (X - X_mean) / X_std
        print(f"[ISLEM] MLP Giriş Boyutu: {X.shape} (Z-Score normalize edildi)")
        model = build_deep_mlp(input_dim=19, num_classes=5)
    else:  # cnn
        X = x_emg  # (N, 20, 4)
        print(f"[ISLEM] 1D-CNN Giriş Boyutu: {X.shape}")
        model = build_1d_cnn(input_shape=(20, 4), num_classes=5)

    # 3. Train / Test Ayrımı
    if args.split_strategy == "loso":
        target_subj = str(args.test_subject).zfill(2)
        test_idx = np.where(subjects == target_subj)[0]
        train_idx = np.where(subjects != target_subj)[0]

        if len(test_idx) == 0:
            print(f"[UYARI] '{target_subj}' denek ID'si yüklenen verilerde bulunamadı (Mevcut denekler: {list(set(subjects))}). Rastgele %80/%20 ayrımına dönülüyor.")
            indices = np.arange(len(y))
            np.random.seed(42)
            np.random.shuffle(indices)
            split_idx = int(0.8 * len(y))
            train_idx, test_idx = indices[:split_idx], indices[split_idx:]
        else:
            print(f"[SPLIT] LOSO (Leave-One-Subject-Out) Çapraz Doğrulama:")
            print(f"        -> Test Deneği (Dışarıda Bırakılan) : Subject {target_subj} ({len(test_idx)} test penceresi)")
            print(f"        -> Eğitim Denekleri                  : {len(set(subjects[train_idx]))} denek ({len(train_idx)} eğitim penceresi)")
    else:
        # Rastgele pencere bazlı %80 Eğitim, %20 Test
        indices = np.arange(len(y))
        np.random.seed(42)
        np.random.shuffle(indices)
        split_idx = int(0.8 * len(y))
        train_idx, test_idx = indices[:split_idx], indices[split_idx:]
        print(f"[SPLIT] Rastgele Ayrım: %80 Eğitim ({len(train_idx)} pencere) / %20 Test ({len(test_idx)} pencere)")

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    # Veri Çoğaltma ve Gürültü Enjeksiyonu (Data Augmentation / Noise Robustness):
    # Gerçek dünya elektrot temassızlığı ve termal gürültüye karşı modeli dayanıklı kılmak için
    # sadece eğitim setine kontrollü Gauss beyaz gürültüsü eklenir (test seti saf bırakılır):
    if args.add_noise:
        noise = np.random.normal(0.0, args.noise_level, X_train.shape).astype(np.float32)
        X_train = X_train + noise
        print(f"[AUGMENT] Egitim setine yapay Gauss gurultusu eklendi (Noise robustness / data augmentation, std: {args.noise_level})")

    # 4. Eğitim
    print("\n--- Model Eğitimi Başlıyor ---")
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=8,
            restore_best_weights=True
        )
    ]
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
        verbose=1
    )

    # 5. Evaluation
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print("\n==================================================================")
    print(f"EĞİTİM TAMAMLANDI -> Test Accuracy: %{test_acc * 100:.2f} | Test Loss: {test_loss:.4f}")
    print("==================================================================")

    # 6. Classification Report & Confusion Matrix
    y_pred_probs = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)

    try:
        from sklearn.metrics import classification_report, confusion_matrix
        target_names = [GESTURE_CLASSES[i] for i in range(5)]
        print("\nClassification Report (Precision / Recall / F1-Score):")
        print(classification_report(y_test, y_pred, target_names=target_names))
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
    except ImportError:
        pass

    # 7. TFLite & INT8 Quantization
    if args.quantize:
        print("\n--- INT8 Post-Training Quantization (PTQ) Uygulanıyor ---")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        def representative_data_gen():
            for i in range(min(100, len(X_train))):
                sample = np.expand_dims(X_train[i], axis=0).astype(np.float32)
                yield [sample]

        converter.representative_dataset = representative_data_gen
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.int8
        converter.inference_output_type = tf.int8

        tflite_model = converter.convert()
        tflite_path = f"nuada_{args.model_type}_int8.tflite"
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        print(f"[OK] Quantized INT8 TFLite Modeli Kaydedildi: {tflite_path} ({len(tflite_model)} bayt)")

        # C Header Yazma
        if args.output_header:
            export_c_header(tflite_model, args.output_header, model_name=f"nuada_{args.model_type}")
    else:
        # Standart Float32 TFLite
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()
        tflite_path = f"nuada_{args.model_type}_fp32.tflite"
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        print(f"[OK] Standart Float32 TFLite Modeli Kaydedildi: {tflite_path} ({len(tflite_model)} bayt)")
        if args.output_header:
            export_c_header(tflite_model, args.output_header, model_name=f"nuada_{args.model_type}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Nuada TinyML Training & INT8 Quantization Pipeline",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=32),
    )
    parser.add_argument("--model_type", type=str, choices=["mlp", "cnn"], default="mlp", metavar="TYPE",
                        help="Model mimarisi: 'mlp' (19 feature) veya 'cnn' (1D-CNN)")
    parser.add_argument("--dataset_dir", type=str, default="", metavar="DIR",
                        help="CSV veri setinin bulunduğu klasör yolu")
    parser.add_argument("--epochs", type=int, default=25, metavar="N",
                        help="Eğitim epok sayısı")
    parser.add_argument("--batch_size", type=int, default=32, metavar="N",
                        help="Batch boyutu")
    parser.add_argument("--quantize", action="store_true", default=True,
                        help="INT8 Post-Training Quantization uygula")
    parser.add_argument("--output_header", type=str, default="model_data.h", metavar="FILE",
                        help="Üretilecek C header dosyasının yolu")
    parser.add_argument("--mock", action="store_true", default=False,
                        help="Gerçek veri yoksa sentetik fizyolojik veri üret")
    parser.add_argument("--samples_per_class", type=int, default=150, metavar="N",
                        help="Mock modunda sınıf başına pencere sayısı")
    parser.add_argument("--split_strategy", type=str, choices=["random", "loso"], default="random", metavar="STRAT",
                        help="Veri ayırma: 'random' (%%80/%%20) veya 'loso' (LOSO)")
    parser.add_argument("--test_subject", type=str, default="01", metavar="ID",
                        help="LOSO için test denek ID'si (ör. '01', '02')")
    parser.add_argument("--add_noise", action="store_true", default=False,
                        help="Eğitim setine Gauss gürültüsü ekle (Noise Robustness)")
    parser.add_argument("--noise_level", type=float, default=0.05, metavar="STD",
                        help="Eklenen gürültünün standart sapması (varsayılan: 0.05)")

    cli_args = parser.parse_args()
    run_pipeline(cli_args)
