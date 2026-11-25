# Nuri Ziya Kırtepe - Deep TinyML & Hard Real-Time OS Guide

Bu klasör, Nuada Biyonik El projesinde **Nuri Ziya Kırtepe**'nin resmi görev dağılımı kapsamındaki tüm Deep TinyML (1D-CNN / MLP), INT8 Post-Training Quantization (PTQ), C array ihracı (`model_data.h`), ESP32-S3 Core 1 Hard Real-Time FreeRTOS görevleri ve Continuous DMA ADC veri toplama hattını içerir.

---

## 1. Division of Labor & Scope Boundaries

Resmi proje şartnamesi ve onaylanan görev dağılımı ([anatomy_and_signal_acquisition.md](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/docs/protocols/anatomy_and_signal_acquisition.md#L204-L212)) uyarınca iki araştırmacının çalışma alanları kesin teknik sınırlarla ayrılmıştır:

| Research Dimension | Nuri Ziya Kırtepe (THIS FOLDER / ZİYA'S SCOPE)<br>**High-Speed Sampling, Hard Real-Time OS & Deep TinyML** | Evrim Doğa Solmaz (SEPARATE DOMAIN)<br>**Real-Time DSP, Soft Real-Time OS & Kinematic Fusion** |
|---|---|---|
| **FreeRTOS & Embedded OS Architecture** | • **Hard Real-Time Task Design (Core 1):** Architects the high-priority `vTaskEMGSampling` and `vTaskTinyMLInference` tasks.<br>• **ISR & OS Synchronization:** Implements direct-to-task notifications (`xTaskNotifyFromISR`) and binary semaphores triggered by DMA buffer-ready hardware interrupts.<br>• **Cross-Core IPC & Queues:** Co-engineers the FreeRTOS Queue and Mutex architecture that transfers raw multi-channel windows between Core 1 and Core 0 with zero priority inversion. | • **Soft Real-Time Task Design (Core 0):** Architects `vTaskIMUSampling` (deterministic 100 Hz timer task via `vTaskDelayUntil`) and `vTaskTelemetry`.<br>• **Network RTOS Stack (LwIP):** Configures FreeRTOS socket tasks for non-blocking Wi-Fi UDP / BLE data transmission.<br>• **Cross-Core Consumer Tasks:** Implements consumer tasks reading from the inter-core queue to feed the real-time DSP filter pipeline. |
| **Core Embedded Driver Architecture (C/C++)** | • **Continuous DMA ADC Driver:** Develops low-level ESP32-S3 ADC1 driver streaming 2000 Hz 4-channel data into circular ping-pong memory buffers.<br>• **Hardware Fallback Driver:** Implements high-speed SPI2 master driver for MCP3008 ADC. | • **Embedded DSP Filtering:** Writes real-time fixed/floating-point IIR bandpass (20 - 450 Hz) and 50 Hz notch filter cascades in C++.<br>• **IMU I2C Driver & Kinematics:** Implements MPU-6050 driver and real-time Complementary / Madgwick orientation filter for arm elevation. |
| **Edge AI & On-Device Deployment** | • Deploys quantized 1D-CNN and MLP architectures to ESP32-S3 Core 1 using **TensorFlow Lite for Microcontrollers (TFLM)**.<br>• Optimizes matrix multiplications with Espressif **ESP-NN vector acceleration instructions**.<br>• Benchmarks hardware inference latency, Tensor Arena dynamic heap/RAM usage, and Flash footprint. | • Deploys real-time Hudgins feature extractor (MAV, RMS, WL, ZC) and Support Vector Machine (SVM) inference engine via lightweight C (`emlearn`).<br>• Implements embedded state machine combining gesture classification with spatial arm orientation. |
| **Offline Modeling & Signal Analysis (Python)** | • Raw time-series waveform preprocessing, temporal spectrogram analysis, 1D-CNN and Deep MLP architecture design.<br>• INT8 post-training quantization (PTQ), hyperparameter search, Loss/Accuracy/F1 curve optimization. | • Time-domain feature space formulation, dimensionality reduction, feature importance analysis.<br>• Classical ML (SVM, Random Forest) and shallow MLP model training, cross-validation, and F1-score evaluation. |
| **Hardware Routing & Telemetry** | • Multi-channel dry electrode hardware routing, analog ground plane shielding.<br>• Automated data collection GUI and real-time labeling protocol (`record_live_emg.py`). | • Real-time wireless telemetry packet formatting (JSON/Protobuf over UDP) to 3D hand digital-twin simulation.<br>• Hybrid kinematic gesture state machine integration. |

> [!IMPORTANT]
> **Ziya'nın Odak Noktası:** Donanım lehimleme, IIR dijital filtreleme, MPU6050 Madgwick açı hesabı ve Three.js 3D web simülasyonu Evrim'in görevleridir. Ziya doğrudan **Derin TinyML modelleri (1D-CNN, MLP), TFLite INT8 Post-Training Quantization (PTQ), C array ihracı (`model_data.h`), Core 1 TFLM on-device inference ve continuous DMA ADC veri toplama hattı** üzerine yoğunlaşacaktır.

---

## 2. Signal Type Adaptation: Envelope vs. Raw AC EMG Universal Feature Engineering

Açık veri setleri ile kendi donanımımız arasında sinyal tipi farkı bulunmaktadır:

1. **Open Datasets (Raw AC Signal):**
   Sinyal referans hattı (0V) etrafında hem pozitif (+) hem negatif (-) salınım yapar. Bu nedenle klasik Hudgins özniteliklerindeki **Zero Crossing (ZC)** anlamlı bilgi üretir.
2. **Custom Hardware (TL084 Envelope Signal):**
   Sensör üzerindeki full-wave rectifier ve low-pass filter devresi sinyali doğrultup düzleştirerek `0 - 3.3 V` pozitif DC envelope üretir. Sinyal sıfır çizgisini kesmediği için **ZC değeri daima 0 çıkar**.
3. **Universal 19-Feature Vector Çözümü:**
   Boru hattında ZC yerine hem Raw AC sinyalde hem de DC Envelope sinyalinde kararlı çalışan öznitelikler seçilmiştir:
   - **4 EMG Channels x 4 Features = 16 Features:**
     - **MAV (Mean Absolute Value):** Kas kasılma şiddeti.
     - **RMS (Root Mean Square):** Sinyal enerjisi ve gücü.
     - **VAR (Variance):** Sinyalin varyansı ve güç dağılımı.
     - **MFD (Mean First Difference / Slope):** Komşu örnekler arası mutlak değişim ortalaması: `Mean(|x[n] - x[n-1]|)`. Sinyalin değişim hızını (frekans karakterini) ZC'ye ihtiyaç duymadan yakalar.
   - **3 IMU Axes x 1 Feature = 3 Features:**
     - `Mean(ax)`, `Mean(ay)`, `Mean(az)`: Kolun yerçekimine göre uzamsal duruşu (gravity vector).
   - **Total Feature Vector Size = 19 Values.**

Bu 19 elemanlı feature vector sayesinde, açık veri setleriyle eğitilen boru hattı kod değişikliği gerektirmeden doğrudan kendi sensör verilerimizle çalıştırılabilir.

---

## 3. TinyML & Edge AI Implementation Roadmap

Ziya'nın adım adım izleyeceği teknik yol haritası:

### Step 1: Sampling & Sliding Window
- **Sampling Rate:** 100 Hz (veya 1000 Hz'den 100 Hz'e downsampled).
- **Window Size:** 200 ms (100 Hz'de pencere başına 20 örnek).
- **Stride (Hop Size):** 50 ms (her 50 ms'de yeni inference, 15 örnek overlap / %75 örtüşme).
- **Gesture Classes (5 Sınıf):**
  - 0: `REST` (Dinlenme / Boşta)
  - 1: `FIST` (Yumruk / Power Grasp - FDS kası)
  - 2: `OPEN` (El Açma - ED kası)
  - 3: `PINCH` (Cımbız Kavrama - FPL kası)
  - 4: `POINT` (İşaret Etme - ED + EPL kası)

### Step 2: Model Architecture Design (TFLM Constraints)
ESP32-S3 üzerinde çalışacak modeller TFLite Micro tarafından desteklenen operatörlerle sınırlandırılmıştır:
1. **Model A: 1D-CNN (Temporal Convolutional Neural Network):**
   - Input: `(20 samples, 4 channels)`
   - Layers: `Conv1D(16, kernel_size=3, padding='same', activation='relu')` -> `MaxPooling1D(pool_size=2)` -> `Conv1D(32, kernel_size=3, activation='relu')` -> `GlobalAveragePooling1D()` -> `Dense(32, activation='relu')` -> `Dense(5, activation='softmax')`
   - Flash Footprint: ~15 KB
   - Tensor Arena RAM: ~18 - 22 KB
2. **Model B: Deep MLP (Feature-Based Multi-Layer Perceptron):**
   - Input: `(19 features,)`
   - Layers: `Dense(32, activation='relu')` -> `Dropout(0.2)` -> `Dense(16, activation='relu')` -> `Dense(5, activation='softmax')`
   - Flash Footprint: ~6 KB
   - Tensor Arena RAM: ~8 - 10 KB
   - On-Device Latency: < 3 ms

### Step 3: Offline Training & Validation (Python)
- Loss Function: `SparseCategoricalCrossentropy`
- Optimizer: `Adam(learning_rate=0.001)`
- Regularization: Overfitting'i önlemek için `EarlyStopping(patience=8, restore_best_weights=True)`
- Evaluation Metrics: Test Accuracy, Confusion Matrix, Class-based F1-Score.

### Step 4: INT8 Post-Training Quantization (PTQ)
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
- Sonuç: Model boyutu 4 kat küçülür, ESP32-S3 üzerinde **ESP-NN SIMD vector acceleration** komutları ile 3-5 kat daha hızlı çalışır.

### Step 5: C Header Export (`model_data.h`)
Kuantalanmış `.tflite` binary dosyası ESP32-S3 C++ koduna C byte array olarak aktarılır:
```bash
xxd -i model_quant_int8.tflite > model_data.h
```
Üretilen `model_data.h` dosyası doğrudan `firmware/` altındaki Core 1 TFLM görevine dahil edilir.

### Step 6: ESP32-S3 Core 1 TFLM On-Device Deployment
ESP32-S3 Core 1 üzerinde çalışan `vTaskTinyMLInference` görevi:
1. `tflite::MicroErrorReporter` ve `tflite::MicroMutableOpResolver` başlatır.
2. Statik Tensor Arena ayırır:
   ```cpp
   constexpr int kTensorArenaSize = 30 * 1024; // 30 KB SRAM
   uint8_t tensor_arena[kTensorArenaSize];
   ```
3. `tflite::MicroInterpreter` nesnesini oluşturur ve tensörleri ayrıştırır (`AllocateTensors()`).
4. Input tensor'ı normalize edilmiş INT8 verilerle besler (`input->data.int8[i] = ...`).
5. Çıkarımı koşturur (`interpreter->Invoke()`).
6. Çıkarım süresini donanımsal timer (`esp_timer_get_time()`) ile mikrosaniye bazında ölçer (Hedef: < 15 ms).
7. Kazanan sınıfı (`argmax`) belirler ve Core 0 telemetri kuyruğuna aktarır.

### Step 7: Presentation Deliverables (Sunum Çıktıları)
Sunumda Ziya'nın sunacağı kısımlar:
1. **TinyML Mimarisi & Optimizasyonu:**
   - 1D-CNN ve MLP katman mimarileri.
   - Float32'den INT8'e dönüşüm ve bellek kazanım tablosu.
2. **Universal Feature Engineering Formülasyonu:**
   - Raw AC sinyali ile Envelope sinyali farkı (ZC yerine MFD seçimi) ve akademik gerekçesi.
3. **Model Başarım Grafikleri:**
   - Loss & Accuracy eğitim eğrileri.
   - 5 sınıflı Confusion Matrix ve F1-Score tablosu.
4. **On-Device Hardware Profiling Metrikleri:**
   - Flash Footprint: < 20 KB.
   - Dynamic Tensor Arena RAM: < 25 KB.
   - Inference Latency: < 15 ms (200 ms pencere süresinin altında deterministik sert gerçek zamanlı çıkarım).

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
