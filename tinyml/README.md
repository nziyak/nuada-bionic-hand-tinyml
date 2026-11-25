# Nuri Ziya Kırtepe - Deep TinyML & Hard Real-Time OS Guide

Bu klasör, Nuada Biyonik El projesinde **Nuri Ziya Kırtepe**'nin resmi görev tanımı kapsamındaki tüm Deep TinyML (1D-CNN / MLP), INT8 Post-Training Quantization (PTQ), C array ihracı (`model_data.h`), ESP32-S3 Core 1 Hard Real-Time FreeRTOS task'ları ve Continuous DMA ADC veri toplama hattını içerir.

---

## 1. Görev Dağılımı ve Sorumluluk Sınırları (Division of Labor)

Resmi proje şartnamesi ve onaylanan görev dağılımı ([anatomy_and_signal_acquisition.md](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/docs/protocols/anatomy_and_signal_acquisition.md#L204-L212)) uyarınca iki araştırmacının çalışma alanları kesin teknik sınırlarla ayrılmıştır:

| Araştırma Boyutu (Research Dimension) | Nuri Ziya Kırtepe (BU KLASÖR / ZİYA'NIN KAPSAMI)<br>**High-Speed Sampling, Hard Real-Time OS & Deep TinyML** | Evrim Doğa Solmaz (KARIŞTIRILMAYACAK AYRI ALAN)<br>**Real-Time DSP, Soft Real-Time OS & Kinematic Fusion** |
|---|---|---|
| **FreeRTOS & Embedded OS Architecture** | • **Hard Real-Time Task Design (Core 1):** En yüksek öncelikli `vTaskEMGSampling` ve `vTaskTinyMLInference` hard real-time FreeRTOS task'larını Core 1 üzerinde tasarlar ve mimarisini kurar.<br>• **ISR & OS Synchronization:** DMA buffer-ready hardware interrupt'ları tetiklendiğinde `xTaskNotifyFromISR` ve binary semaphore'lar ile zero-latency task wakeup mekanizmasını kurar.<br>• **Cross-Core IPC & Queues:** Core 1 ile Core 0 arasında zero priority inversion prensibiyle raw multi-channel window'ları aktaran FreeRTOS Queue ve Mutex mimarisini co-engineer eder. | • **Soft Real-Time Task Design (Core 0):** Deterministik 100 Hz timer task'ı olarak `vTaskDelayUntil` kullanan `vTaskIMUSampling` ve `vTaskTelemetry` soft real-time task'larını Core 0 üzerinde tasarlar.<br>• **Network RTOS Stack (LwIP):** Non-blocking Wi-Fi UDP ve BLE transmission için FreeRTOS socket task'larını yapılandırır.<br>• **Cross-Core Consumer Tasks:** Inter-core queue üzerinden gelen verileri okuyup real-time DSP filter pipeline'ına besleyen consumer task'ları yazar. |
| **Core Embedded Driver Architecture (C/C++)** | • **Continuous DMA ADC Driver:** ESP32-S3 dahili ADC1 çevre birimini 2000 Hz 4-channel continuous sampling ile circular ping-pong memory buffer'larına aktaran low-level C/C++ driver'ı geliştirir.<br>• **Hardware Fallback Driver:** MCP3008 harici ADC için yüksek hızlı SPI2 master driver'ı kodlar. | • **Embedded DSP Filtering:** C++ ile gerçek zamanlı fixed/floating-point IIR bandpass (20 - 450 Hz) ve 50 Hz notch filter cascade'lerini kodlar.<br>• **IMU I2C Driver & Kinematics:** MPU-6050 I2C driver'ını yazar ve kolun pitch/roll elevation takibi için real-time Complementary / Madgwick orientation filter uygular. |
| **Edge AI & On-Device Deployment** | • Quantized 1D-CNN ve Deep MLP mimarilerini **TensorFlow Lite for Microcontrollers (TFLM)** kullanarak ESP32-S3 Core 1 üzerinde deploy eder.<br>• Matris çarpımlarını Espressif **ESP-NN vector acceleration instructions** (SIMD) ile optimize eder.<br>• Donanım üzerinde hardware inference latency, Tensor Arena dynamic heap/RAM kullanımı ve Flash footprint benchmark'larını gerçekleştirir. | • Real-time Hudgins feature extractor (MAV, RMS, WL, ZC) ve Support Vector Machine (SVM) inference motorunu hafif C kütüphanesi (`emlearn`) ile deploy eder.<br>• Gesture classification çıktısı ile spatial arm orientation bilgisini birleştiren embedded state machine yapısını kurar. |
| **Offline Modeling & Signal Analysis (Python)** | • Raw time-series waveform preprocessing, temporal spectrogram analizi, 1D-CNN ve Deep MLP mimari tasarımı yapar.<br>• INT8 Post-Training Quantization (PTQ), hyperparameter search ve Loss/Accuracy/F1 curve optimizasyonunu yürütür. | • Time-domain feature space formülasyonu, dimensionality reduction ve feature importance analizi yapar.<br>• Klasik makine öğrenmesi (SVM, Random Forest) ve shallow MLP modellerini eğitir, cross-validation ve F1-score değerlendirmelerini yapar. |
| **Hardware Routing & Telemetry** | • Multi-channel dry electrode analog signal routing ve analog ground plane shielding tasarımını yapar.<br>• Automated data collection GUI / CLI ve real-time labeling protokolünü (`record_live_emg.py`) geliştirir. | • 3D digital-twin hand simülasyonuna real-time wireless telemetry packet formatlamasını (UDP üzerinden JSON/Protobuf) yapar.<br>• Hybrid kinematic gesture state machine entegrasyonunu tamamlar ve pertinaks lehimleme/montajını üstlenir. |

> [!IMPORTANT]
> **Ziya'nın Odak Noktası:** Donanım lehimleme, IIR dijital filtreleme, MPU6050 Madgwick açı hesabı ve Three.js 3D web simülasyonu Evrim'in görevleridir. Ziya doğrudan **Derin TinyML modelleri (1D-CNN, MLP), TFLite INT8 Post-Training Quantization (PTQ), C array ihracı (`model_data.h`), Core 1 TFLM on-device inference ve continuous DMA ADC veri toplama hattı** üzerine yoğunlaşacaktır.

---

## 2. Sinyal Tipi Uyarlaması: Zarf (Envelope) ve Ham AC EMG için Evrensel Öznitelik Mühendisliği

Açık veri setleri (open datasets) ile kendi donanımımız arasında sinyal tipi farkı bulunmaktadır:

1. **Open Datasets (Raw AC Signal):**
   Sinyal referans hattı (0V) etrafında hem pozitif (+) hem negatif (-) salınım yapar. Bu nedenle klasik Hudgins özniteliklerindeki **Zero Crossing (ZC)** anlamlı bilgi üretir.
2. **Custom Hardware (TL084 Envelope Signal):**
   Sensör üzerindeki full-wave rectifier ve low-pass filter devresi sinyali doğrultup düzleştirerek `0 - 3.3 V` aralığında pozitif bir DC envelope üretir. Sinyal sıfır çizgisini kesmediği için **ZC değeri daima 0 çıkar**.
3. **Universal 19-Feature Vector Çözümü:**
   Boru hattında ZC yerine hem raw AC sinyalde hem de DC envelope sinyalinde kararlı çalışan öznitelikler seçilmiştir:
   - **4 EMG Channels x 4 Features = 16 Features:**
     - **MAV (Mean Absolute Value):** Kas kasılma şiddeti genlik ortalaması.
     - **RMS (Root Mean Square):** Sinyalin karesel ortalama karekökü; sinyal gücü ve enerjisi.
     - **VAR (Variance):** Sinyalin varyansı ve güç dağılımı; kas tonusu değişimlerini yakalar.
     - **MFD (Mean First Difference / Slope):** Komşu örnekler arasındaki ortalama mutlak değişim: `Mean(|x[n] - x[n-1]|)`. Sinyalin değişim hızını (frekans karakterini) ZC'ye ihtiyaç duymadan doğrudan yakalar.
   - **3 IMU Axes x 1 Feature = 3 Features:**
     - `Mean(ax)`, `Mean(ay)`, `Mean(az)`: Kolun yerçekimine göre uzamsal duruşu (gravity vector).
   - **Total Feature Vector Size = 19 Değer.**

Bu 19 elemanlı feature vector sayesinde, open dataset'ler üzerinde eğitilen boru hattı kod değişikliği gerektirmeden doğrudan kendi custom sensor verilerimizle çalıştırılabilir.

---

## 3. TinyML & Edge AI Adım Adım Eylem Planı (Implementation Roadmap)

Ziya'nın adım adım izleyeceği teknik yol haritası:

### Adım 1: Sampling & Sliding Window
- **Sampling Rate:** 100 Hz (veya 1000 Hz'den 100 Hz'e downsampled).
- **Window Size:** 200 ms (100 Hz'de pencere başına 20 örnek).
- **Stride (Hop Size):** 50 ms (her 50 ms'de bir yeni inference, 15 örnek overlap / %75 örtüşme).
- **Gesture Classes (5 Sınıf):**
  - 0: `REST` (Dinlenme / Boşta)
  - 1: `FIST` (Yumruk / Power Grasp - FDS kası)
  - 2: `OPEN` (El Açma - ED kası)
  - 3: `PINCH` (Cımbız Kavrama - FPL kası)
  - 4: `POINT` (İşaret Etme - ED + EPL kası)

### Adım 2: Model Architecture Design (TFLM Kısıtlamaları)
ESP32-S3 üzerinde çalışacak modeller TensorFlow Lite for Microcontrollers (TFLM) tarafından desteklenen operatörlerle sınırlandırılmıştır:
1. **Model A: 1D-CNN (Temporal Convolutional Neural Network):**
   - Input Shape: `(20 samples, 4 channels)`
   - Layers: `Conv1D(16, kernel_size=3, padding='same', activation='relu')` -> `MaxPooling1D(pool_size=2)` -> `Conv1D(32, kernel_size=3, activation='relu')` -> `GlobalAveragePooling1D()` -> `Dense(32, activation='relu')` -> `Dense(5, activation='softmax')`
   - Flash Footprint: ~15 KB
   - Tensor Arena RAM: ~18 - 22 KB
2. **Model B: Deep MLP (Feature-Based Multi-Layer Perceptron):**
   - Input Shape: `(19 features,)`
   - Layers: `Dense(32, activation='relu')` -> `Dropout(0.2)` -> `Dense(16, activation='relu')` -> `Dense(5, activation='softmax')`
   - Flash Footprint: ~6 KB
   - Tensor Arena RAM: ~8 - 10 KB
   - On-Device Latency: < 3 ms

### Adım 3: Offline Training & Validation (Python)
- Loss Function: `SparseCategoricalCrossentropy`
- Optimizer: `Adam(learning_rate=0.001)`
- Regularization: Overfitting'i önlemek için `EarlyStopping(patience=8, restore_best_weights=True)`
- Evaluation Metrics: Test Accuracy, Confusion Matrix, Sınıf bazlı F1-Score.

### Adım 4: INT8 Post-Training Quantization (PTQ)
Float32 model ağırlıkları ve aktivasyonları INT8 formatına dönüştürülür:
```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_data_gen
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8
tflite_quant_model = converter.convert()
```
- Sonuç: Model boyutu 4 kat küçülür, ESP32-S3 üzerinde **ESP-NN SIMD vector acceleration** komutları ile 3 ila 5 kat daha hızlı çalışır.

### Adım 5: C Header Export (`model_data.h`)
Quantized `.tflite` binary dosyası ESP32-S3 C++ firmware'ine bir C byte array olarak aktarılır:
```bash
xxd -i model_quant_int8.tflite > model_data.h
```
Üretilen `model_data.h` dosyası doğrudan `firmware/` altındaki Core 1 TFLM task'ına dahil edilir.

### Adım 6: ESP32-S3 Core 1 TFLM On-Device Deployment
ESP32-S3 Core 1 üzerinde çalışan `vTaskTinyMLInference` task'ı:
1. `tflite::MicroErrorReporter` ve `tflite::MicroMutableOpResolver` başlatır.
2. Static Tensor Arena ayırır:
   ```cpp
   constexpr int kTensorArenaSize = 30 * 1024; // 30 KB SRAM
   uint8_t tensor_arena[kTensorArenaSize];
   ```
3. `tflite::MicroInterpreter` nesnesini oluşturur ve tensörleri allocate eder (`AllocateTensors()`).
4. Input tensor'ı normalize edilmiş INT8 verilerle besler (`input->data.int8[i] = ...`).
5. Inference işlemini koşturur (`interpreter->Invoke()`).
6. Inference latency süresini donanımsal timer (`esp_timer_get_time()`) ile mikrosaniye bazında ölçer (Hedef: < 15 ms).
7. Kazanan sınıfı (`argmax`) belirler ve Core 0 telemetry queue'suna gönderir.

### Adım 7: Çarşamba Günü Sunumu için Hazırlanması Gerekenler (Presentation Deliverables)
Sunumda Ziya'nın sunacağı kısımlar:
1. **TinyML Mimarisi & Optimizasyonu:**
   - 1D-CNN ve MLP katman mimarileri.
   - Float32'den INT8'e dönüşüm ve memory savings tablosu.
2. **Universal Feature Engineering Formülasyonu:**
   - Raw AC sinyali ile Envelope sinyali farkı (ZC yerine MFD seçimi) ve akademik gerekçesi.
3. **Model Başarım Grafikleri:**
   - Loss & Accuracy eğitim eğrileri.
   - 5 sınıflı Confusion Matrix ve F1-Score tablosu.
4. **On-Device Hardware Profiling Metrikleri:**
   - Flash Footprint: < 20 KB.
   - Dynamic Tensor Arena RAM: < 25 KB.
   - Inference Latency: < 15 ms (200 ms pencere süresinin altında deterministik hard real-time çıkarım).

---

## 4. Klasör İçeriği ve Araçlar

| Dosya | Açıklama |
|---|---|
| [features.py](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/features.py) | Hem raw AC hem envelope sinyalleri için MAV, RMS, VAR, MFD ve IMU mean feature extractor modülü. |
| [models.py](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/models.py) | TFLM uyumlu 1D-CNN ve Deep MLP Keras model tanımları. |
| [train_tinyml.py](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/train_tinyml.py) | Data loading, training, F1/Confusion Matrix evaluation, INT8 PTQ ve `model_data.h` C array export pipeline. |
| [benchmark_tflite.py](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/benchmark_tflite.py) | Flash footprint, tensor tipleri, quantization parameters ve Tensor Arena RAM profiler aracı. |
| [requirements.txt](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/requirements.txt) | Python virtual environment için kütüphane bağımlılıkları. |

---

## 5. Hızlı Başlangıç (Quickstart)

### 1. Sanal Ortamı Kurma ve Paketleri Yükleme
```bash
cd /home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Sentetik Pilot Veriyle Pipeline'ı Test Etme (Mock Mode)
```bash
python3 train_tinyml.py --mock --model_type cnn --epochs 15 --quantize
```

### 3. CSV Verileriyle Model Eğitme ve C Header Üretme
```bash
python3 train_tinyml.py --dataset_dir ../data/deneme/ --model_type mlp --epochs 30 --quantize --output_header model_data.h
```

### 4. TFLite Modelini ve Bellek Tüketimini Profilleme
```bash
python3 benchmark_tflite.py --model_path nuada_mlp_int8.tflite
```
