#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nuada TinyML - Neural Network Model Architectures
Author: Nuri Ziya Kırtepe
Project: Nuada Bionic Hand Movement Estimation via TinyML

Bu modül, ESP32-S3 mikrodenetleyicisi ve TensorFlow Lite for Microcontrollers (TFLM)
motoru için özel olarak optimize edilmiş derin yapay zeka modellerini içerir.

Modeller:
1. build_1d_cnn(): 200 ms (20 örnek x 4 kanal) ham/zarf zaman serisi pencerelerini
   doğrudan işleyen zamansal evrişimli (1D-CNN) derin öğrenme ağı.
2. build_deep_mlp(): 19 elemanlı evrensel öznitelik vektörünü (MAV, RMS, VAR, MFD, IMU)
   işleyen çok katmanlı yapay sinir ağı (MLP).

TFLite Micro Uyumluluk Kuralları:
- Sadece TFLM tarafından desteklenen operatörler kullanılır (Conv1D, Relu, MaxPool1D, Dense, Softmax).
- Ağırlık boyutları ESP32-S3 SRAM sınırlarına (< 100 KB) uygun tutulmuştur.
"""

from typing import Tuple

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
    HAS_TF = True
except ImportError:
    HAS_TF = False


def build_1d_cnn(
    input_shape: Tuple[int, int] = (20, 4),
    num_classes: int = 5,
    learning_rate: float = 0.001
):
    """
    ESP32-S3 Core 1 için optimize edilmiş 1D-CNN (Temporal Convolutional Network).

    Giriş: (Pencere Örnek Sayısı, Kanal Sayısı) -> Varsayılan: (20, 4)
    Çıkış: 5 Sınıflı Olasılık Dağılımı (Softmax)
    Hedef Çıkarım Süresi: < 15 ms (ESP-NN hızlandırması ile)
    Tahmini Flash Boyutu: ~15 KB
    """
    if not HAS_TF:
        raise ImportError("TensorFlow kütüphanesi yüklü değil. Lütfen sanal ortamda çalıştırın.")

    model = models.Sequential([
        # 1. Evrişim Bloğu
        layers.Input(shape=input_shape, name="input_emg_window"),
        layers.Conv1D(
            filters=16,
            kernel_size=3,
            padding="same",
            activation="relu",
            name="conv1d_1"
        ),
        layers.MaxPooling1D(pool_size=2, name="maxpool_1"),

        # 2. Evrişim Bloğu
        layers.Conv1D(
            filters=32,
            kernel_size=3,
            padding="same",
            activation="relu",
            name="conv1d_2"
        ),
        layers.GlobalAveragePooling1D(name="gap"),

        # Sınıflandırma Katmanı
        layers.Dense(32, activation="relu", name="dense_hidden"),
        layers.Dense(num_classes, activation="softmax", name="output_gesture")
    ], name="nuada_1d_cnn")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def build_deep_mlp(
    input_dim: int = 19,
    num_classes: int = 5,
    learning_rate: float = 0.001
):
    """
    19 Elemanlı Evrensel Öznitelik Vektörü için Derin Çok Katmanlı Algılayıcı (MLP).

    Giriş: (19,) -> MAV, RMS, VAR, MFD (4 kanal x 4) + IMU (ax, ay, az)
    Çıkış: 5 Sınıflı Olasılık Dağılımı (Softmax)
    Hedef Çıkarım Süresi: < 3 ms
    Tahmini Flash Boyutu: ~6 KB
    Tahmini Tensor Arena RAM: ~8 KB
    """
    if not HAS_TF:
        raise ImportError("TensorFlow kütüphanesi yüklü değil. Lütfen sanal ortamda çalıştırın.")

    model = models.Sequential([
        layers.Input(shape=(input_dim,), name="input_features"),
        layers.Dense(32, activation="relu", name="dense_1"),
        layers.Dropout(0.2, name="dropout_1"),
        layers.Dense(16, activation="relu", name="dense_2"),
        layers.Dense(num_classes, activation="softmax", name="output_gesture")
    ], name="nuada_deep_mlp")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


if __name__ == "__main__":
    if HAS_TF:
        print("=== Nuada Model Mimarileri ===")
        cnn = build_1d_cnn()
        print("\n--- 1D-CNN Modeli Özeti ---")
        cnn.summary()

        mlp = build_deep_mlp()
        print("\n--- Derin MLP Modeli Özeti ---")
        mlp.summary()
    else:
        print("[BILGI] TensorFlow henüz sistemde kurulu değil.")
        print("Sanal ortam oluşturup 'pip install -r requirements.txt' çalıştırıldığında modeller derlenecektir.")
