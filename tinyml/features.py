#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nuada TinyML - Universal Feature Extraction Library
Author: Nuri Ziya Kırtepe
Project: Nuada Bionic Hand Movement Estimation via TinyML

Bu modül, sEMG ve IMU zaman serisi verilerinden 200 ms sliding window
üzerinde hem ham AC sinyallerinde hem de TL084 donanımsal zarf (envelope) DC sinyallerinde
kararlı çalışan 19 elemanlı evrensel feature vektörünü çıkarır.

Feature Seçimi Gerekçesi (Envelope ve Ham Sinyal Uyumluluğu):
- Klasik Hudgins ZC (Zero Crossing) envelope sinyalinde hep 0 çıkar çünkü sinyal 0-3.3V DC arasındadır.
- ZC yerine MFD (Mean First Difference / Slope) seçilmiştir.
- 4 EMG Kanalı x 4 Feature = 16 EMG Feature'ı:
    1. MAV: Mean Absolute Value (Kas kasılma şiddeti)
    2. RMS: Root Mean Square (Sinyal enerjisi ve gücü)
    3. VAR: Variance (Güç dağılımı / varyans)
    4. MFD: Mean First Difference (Sinyal değişim hızı / türev eğimi)
- 3 IMU Ekseni x 1 Feature = 3 IMU Feature'ı:
    1. Mean(ax), Mean(ay), Mean(az) (Kolun yerçekimine göre uzamsal açısı)
- Toplam Boyut: 19 Elemanlı Vektör
"""

import math
from typing import List, Tuple, Union

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ==============================================================================
# 1. TEMEL TEK BOYUTLU ÖZNİTELİK FONKSİYONLARI (Saf Python & NumPy Uyumlu)
# ==============================================================================

def compute_mav(samples: Union[List[float], "np.ndarray"]) -> float:
    """Mean Absolute Value (MAV): Ortalama Mutlak Değer."""
    if len(samples) == 0:
        return 0.0
    if HAS_NUMPY and isinstance(samples, np.ndarray):
        return float(np.mean(np.abs(samples)))
    return float(sum(abs(x) for x in samples) / len(samples))


def compute_rms(samples: Union[List[float], "np.ndarray"]) -> float:
    """Root Mean Square (RMS): Karesel Ortalama Karekökü (Sinyal Gücü)."""
    if len(samples) == 0:
        return 0.0
    if HAS_NUMPY and isinstance(samples, np.ndarray):
        return float(np.sqrt(np.mean(np.square(samples))))
    mean_sq = sum(x * x for x in samples) / len(samples)
    return float(math.sqrt(mean_sq))


def compute_var(samples: Union[List[float], "np.ndarray"]) -> float:
    """Variance (VAR): Varyans (Sinyalin Güç Dağılımı)."""
    n = len(samples)
    if n < 2:
        return 0.0
    if HAS_NUMPY and isinstance(samples, np.ndarray):
        return float(np.var(samples))
    mean = sum(samples) / n
    return float(sum((x - mean) ** 2 for x in samples) / n)


def compute_mfd(samples: Union[List[float], "np.ndarray"]) -> float:
    """
    Mean First Difference (MFD / Slope):
    Komşu örnekler arasındaki ortalama mutlak değişim.
    Sinyalin frekans karakteristiğini ve dalgalanma hızını sıfır geçişine (ZC)
    ihtiyaç duymadan doğrudan yakalar. Hem ham hem DC zarf verisinde stabildir.
    """
    n = len(samples)
    if n < 2:
        return 0.0
    if HAS_NUMPY and isinstance(samples, np.ndarray):
        return float(np.mean(np.abs(np.diff(samples))))
    diffs = [abs(samples[i] - samples[i - 1]) for i in range(1, n)]
    return float(sum(diffs) / len(diffs))


# ==============================================================================
# 2. ÇOK KANALLI PENCERE ÖZNİTELİK ÇIKARICI (19 Elemanlı Evrensel Vektör)
# ==============================================================================

def extract_window_features(
    emg_window: Union[List[List[float]], "np.ndarray"],
    imu_window: Union[List[List[float]], "np.ndarray", None] = None
) -> List[float]:
    """
    200 ms'lik bir veri penceresinden 19 elemanlı feature vektörünü çıkarır.

    Parametreler:
        emg_window: (N, 4) boyutunda 4 kanallı EMG penceresi (N örnek, varsayılan 20).
        imu_window: (N, 3) boyutunda 3 eksenli IMU penceresi (ax, ay, az). None olabilir.

    Dönüş:
        19 elemanlı feature listesi:
        [CH1_MAV, CH1_RMS, CH1_VAR, CH1_MFD,
         CH2_MAV, CH2_RMS, CH2_VAR, CH2_MFD,
         CH3_MAV, CH3_RMS, CH3_VAR, CH3_MFD,
         CH4_MAV, CH4_RMS, CH4_VAR, CH4_MFD,
         IMU_AX_MEAN, IMU_AY_MEAN, IMU_AZ_MEAN]
    """
    features: List[float] = []

    # 4 EMG Kanalı
    num_emg_ch = 4
    if HAS_NUMPY and isinstance(emg_window, np.ndarray):
        for ch in range(num_emg_ch):
            ch_data = emg_window[:, ch] if emg_window.ndim > 1 else emg_window
            features.append(compute_mav(ch_data))
            features.append(compute_rms(ch_data))
            features.append(compute_var(ch_data))
            features.append(compute_mfd(ch_data))
    else:
        # Liste yapısı (N x 4)
        n_samples = len(emg_window)
        for ch in range(num_emg_ch):
            ch_data = [emg_window[i][ch] for i in range(n_samples)]
            features.append(compute_mav(ch_data))
            features.append(compute_rms(ch_data))
            features.append(compute_var(ch_data))
            features.append(compute_mfd(ch_data))

    # 3 IMU Kanalı (Yerçekimi / Duruş Bileşeni)
    if imu_window is not None and len(imu_window) > 0:
        if HAS_NUMPY and isinstance(imu_window, np.ndarray):
            for axis in range(3):
                ax_data = imu_window[:, axis] if imu_window.ndim > 1 else imu_window
                features.append(float(np.mean(ax_data)))
        else:
            n_samples = len(imu_window)
            for axis in range(3):
                ax_data = [imu_window[i][axis] for i in range(n_samples)]
                features.append(float(sum(ax_data) / len(ax_data)))
    else:
        # IMU bağlı değilse 0 ekle (nötr yatay duruş)
        features.extend([0.0, 0.0, 1.0])

    return features


# ==============================================================================
# 3. KAYAN PENCERELEME (SLIDING WINDOW) ÜRETECİ
# ==============================================================================

def generate_sliding_windows(
    data: Union[List[List[float]], "np.ndarray"],
    window_size: int = 20,
    stride: int = 5
) -> List[Union[List[List[float]], "np.ndarray"]]:
    """
    Zaman serisi verisini belirtilen pencere boyutu ve adım ile dilimler.
    100 Hz örneklemede:
        window_size = 20 (200 ms)
        stride = 5 (50 ms)
        overlap = 15 (%75 örtüşme)
    """
    n_samples = len(data)
    windows = []
    start = 0
    while start + window_size <= n_samples:
        end = start + window_size
        windows.append(data[start:end])
        start += stride
    return windows


if __name__ == "__main__":
    print("=== Nuada Universal Feature Extractor Testi ===")
    # 20 örnek, 4 kanal sahte EMG verisi (100 Hz'de 200 ms)
    dummy_emg = [[0.5 * (c + 1) + 0.1 * math.sin(i) for c in range(4)] for i in range(20)]
    dummy_imu = [[0.02, 0.05, 0.98] for _ in range(20)]

    feats = extract_window_features(dummy_emg, dummy_imu)
    print(f"Toplam Çıkarılan Öznitelik Sayısı: {len(feats)} (Beklenen: 19)")
    print("Örnek Öznitelik Vektörü (İlk 8 Eleman - CH1 ve CH2):")
    for idx, f in enumerate(feats[:8]):
        print(f"  F[{idx:02d}]: {f:.4f}")
    print("IMU Yerçekimi Bileşenleri (Son 3 Eleman):")
    for idx, f in enumerate(feats[-3:], start=16):
        print(f"  F[{idx:02d}]: {f:.4f}")
    print("[OK] Öznitelik çıkarıcı testi başarıyla tamamlandı.")
