#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Nuada TinyML - End-to-End Training & INT8 Quantization Pipeline
Author: Nuri Ziya Kırtepe
Project: Nuada Bionic Hand Movement Estimation via TinyML

Bu script:
1. Veri setini yükler (CSV formatında gerçek kayıtlar veya --mock bayrağıyla sentetik veriler).
2. 200 ms kayan pencereleme ve 19 öznitelikli evrensel öznitelik çıkarımını uygular.
3. 1D-CNN veya Derin MLP modelini eğitir.
4. Test seti üzerinde Doğruluk (Accuracy) ve Sınıflandırma Metriklerini hesaplar.
5. Modeli TFLite INT8 Post-Training Quantization (PTQ) ile 8-bit tam sayıya sıkıştırır.
6. ESP32-S3 C/C++ firmware için doğrudan kullanılabilir 'model_data.h' C başlık dosyasını üretir.

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
    2: "OPEN (El Acik - ED)",
    3: "PINCH (Cimbiz - FPL)",
    4: "POINT (Isaret - ED+EPL)"
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
    return x_emg, x_imu, y


def load_csv_dataset(dataset_dir: str) -> Tuple[Any, Any, Any]:
    """
    data/ klasöründeki CSV kayıtlarını okur ve pencerelere ayırır.
    """
    if not HAS_NUMPY:
        raise RuntimeError("NumPy kütüphanesi gereklidir.")

    import glob
    import pandas as pd

    csv_files = glob.glob(os.path.join(dataset_dir, "**/*.csv"), recursive=True)
    if not csv_files:
        raise FileNotFoundError(f"'{dataset_dir}' dizininde hiçbir .csv dosyası bulunamadı!")

    print(f"[DATA] {len(csv_files)} adet CSV dosyası bulundu, okunuyor...")
    all_emg_windows = []
    all_imu_windows = []
    all_labels = []

    for fpath in csv_files:
        df = pd.read_csv(fpath)
        # Sütun kontrolü (emg1..emg4, ax, ay, az, label)
        emg_cols = [c for c in df.columns if "emg" in c.lower() or "ch" in c.lower()][:4]
        imu_cols = [c for c in df.columns if any(k in c.lower() for k in ["ax", "ay", "az", "acc"])][:3]
        label_col = [c for c in df.columns if "label" in c.lower() or "class" in c.lower()]

        if not emg_cols or not label_col:
            continue

        raw_emg = df[emg_cols].values
        raw_imu = df[imu_cols].values if len(imu_cols) == 3 else np.zeros((len(df), 3))
        raw_labels = df[label_col[0]].values

        # Kayan pencereleme (20 örnek pencere, 5 örnek adım)
        for i in range(0, len(df) - 20, 5):
            emg_win = raw_emg[i:i+20]
            imu_win = raw_imu[i:i+20]
            lbl = int(raw_labels[i+10])  # Ortanca etiketi al
            all_emg_windows.append(emg_win)
            all_imu_windows.append(imu_win)
            all_labels.append(lbl)

    return np.array(all_emg_windows, dtype=np.float32), np.array(all_imu_windows, dtype=np.float32), np.array(all_labels, dtype=np.int32)


# ==============================================================================
# 2. INT8 KUANTALAMA VE C BAŞLIĞI ÜRETİMİ
# ==============================================================================

def export_c_header(tflite_bytes: bytes, output_path: str, model_name: str = "nuada_model"):
    """
    .tflite ikili model baytlarını C/C++ uyumlu 'model_data.h' başlık dosyasına dönüştürür.
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
    print(f"[OK] C baslik dosyasi basariyla olusturuldu: {output_path} ({len(tflite_bytes)} bayt)")


# ==============================================================================
# 3. ANA EĞİTİM VE ÇALIŞTIRMA BORU HATTI
# ==============================================================================

def run_pipeline(args):
    if not HAS_TF or not HAS_NUMPY:
        print("\n" + "="*70)
        print("  [BILGI] Gerekli Python kutuphaneleri (numpy, tensorflow) henuz yuklu degil!")
        print("="*70)
        print("  train_tinyml.py derin ogrenme modelini egitmek ve INT8 kuantalama")
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
    print("      NUADA TINYML MODEL EĞİTİM & INT8 KUANTALAMA HATTI          ")
    print("==================================================================")
    print(f"Model Tipi     : {args.model_type.upper()}")
    print(f"Epok Sayısı    : {args.epochs}")
    print(f"Paket Boyutu   : {args.batch_size}")
    print(f"Kuantalama     : {'Açık (INT8 PTQ)' if args.quantize else 'Kapalı (Float32)'}")

    # 1. Veri Yükleme
    if args.mock or not args.dataset_dir:
        x_emg, x_imu, y = generate_mock_dataset(num_samples_per_class=args.samples_per_class)
    else:
        x_emg, x_imu, y = load_csv_dataset(args.dataset_dir)

    print(f"[VERI] Toplam Pencere Sayısı: {len(y)}, Sınıf Sayısı: {len(set(y))}")

    # 2. Model Tipine Göre Giriş Matrisi Hazırlığı
    if args.model_type == "mlp":
        print("[ISLEM] 19 elemanlı evrensel öznitelik vektörleri çıkarılıyor...")
        feat_list = []
        for i in range(len(x_emg)):
            feats = extract_window_features(x_emg[i], x_imu[i])
            feat_list.append(feats)
        X = np.array(feat_list, dtype=np.float32)
        print(f"[ISLEM] MLP Giriş Boyutu: {X.shape}")
        model = build_deep_mlp(input_dim=19, num_classes=5)
    else:  # cnn
        X = x_emg  # (N, 20, 4)
        print(f"[ISLEM] 1D-CNN Giriş Boyutu: {X.shape}")
        model = build_1d_cnn(input_shape=(20, 4), num_classes=5)

    # 3. Train / Test Ayrımı (%80 Eğitim, %20 Doğrulama)
    indices = np.arange(len(y))
    np.random.seed(42)
    np.random.shuffle(indices)
    split_idx = int(0.8 * len(y))

    train_idx, test_idx = indices[:split_idx], indices[split_idx:]
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

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

    # 5. Doğruluk Değerlendirmesi
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print("\n==================================================================")
    print(f"EĞİTİM TAMAMLANDI -> Test Doğruluğu: %{test_acc * 100:.2f} | Test Kaybı: {test_loss:.4f}")
    print("==================================================================")

    # 6. Sınıflandırma ve Karışıklık Matrisi
    y_pred_probs = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)

    try:
        from sklearn.metrics import classification_report, confusion_matrix
        target_names = [GESTURE_CLASSES[i] for i in range(5)]
        print("\nSınıflandırma Raporu (Precision / Recall / F1-Score):")
        print(classification_report(y_test, y_pred, target_names=target_names))
        print("Karışıklık Matrisi (Confusion Matrix):")
        print(confusion_matrix(y_test, y_pred))
    except ImportError:
        pass

    # 7. TFLite & INT8 Kuantalama
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
        print(f"[OK] Kuantalanmış INT8 TFLite Modeli Kaydedildi: {tflite_path} ({len(tflite_model)} bayt)")

        # C Başlığı Yazma
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
    parser = argparse.ArgumentParser(description="Nuada TinyML Eğitimi ve Kuantalama Scripti")
    parser.add_argument("--model_type", type=str, choices=["mlp", "cnn"], default="mlp",
                        help="Model mimarisi: 'mlp' (19 öznitelikli) veya 'cnn' (1D-CNN zaman serisi)")
    parser.add_argument("--dataset_dir", type=str, default="",
                        help="CSV veri setinin bulunduğu klasör yolu")
    parser.add_argument("--epochs", type=int, default=25,
                        help="Eğitim epok sayısı")
    parser.add_argument("--batch_size", type=int, default=32,
                        help="Toplu veri boyutu")
    parser.add_argument("--quantize", action="store_true", default=True,
                        help="INT8 Post-Training Quantization uygula")
    parser.add_argument("--output_header", type=str, default="model_data.h",
                        help="Üretilecek C başlık dosyasının yolu")
    parser.add_argument("--mock", action="store_true", default=False,
                        help="Gerçek veri yoksa sentetik fizyolojik veri üret")
    parser.add_argument("--samples_per_class", type=int, default=150,
                        help="Mock modunda sınıf başına üretilecek pencere sayısı")

    cli_args = parser.parse_args()
    run_pipeline(cli_args)
