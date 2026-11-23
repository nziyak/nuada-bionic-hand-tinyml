# Nuri Ziya Kırtepe - Deep TinyML & Hard Real-Time OS Rehberi

Bu klasör, Nuada Biyonik El projesinde **Nuri Ziya Kırtepe**'nin resmi akademik ve mühendislik görev tanımına ait tüm yapay zeka (AI), makine öğrenmesi (ML), derin öğrenme (1D-CNN / MLP), model kuantalama (INT8 PTQ) ve ESP32-S3 Core 1 gömülü çıkarım boru hattını içermektedir.

---

## 1. Görev Dağılımı ve Sorumluluk Sınırları

Proje şartnamesi ve onaylanan görev dağılımı uyarınca iki araştırmacının çalışma alanları kesin sınırlarla ayrılmıştır:

| İnceleme Boyutu | Nuri Ziya Kırtepe (BU KLASÖRÜN KAPSAMI)<br>**Yüksek Hızlı Örnekleme, Sert Gerçek Zamanlı İS ve Derin TinyML** | Evrim Doğa Solmaz (KARIŞTIRILMAYACAK DIŞ KAPSAM)<br>**Gerçek Zamanlı DSP, Yumuşak Gerçek Zamanlı İS ve Kinematik Füzyon** |
|---|---|---|
| **FreeRTOS & Gömülü İS** | • **Core 1 Sert Gerçek Zamanlı Görevler:** En yüksek öncelikli `vTaskEMGSampling` ve `vTaskTinyMLInference` görevleri.<br>• **ISR & Senkronizasyon:** DMA arabellek kesmelerinden doğrudan göreve bildirim (`xTaskNotifyFromISR`) ve ikili semaforlar.<br>• **Çekirdekler Arası IPC:** Core 1 ile Core 0 arasında sıfır öncelik terslenmesiyle çalışan FreeRTOS Kuyruk ve Mutex mimarisi. | • **Core 0 Yumuşak Gerçek Zamanlı Görevler:** `vTaskIMUSampling` (100 Hz periyodik `vTaskDelayUntil`) ve `vTaskTelemetry`.<br>• **Ağ İS Yığını (LwIP):** Bloklamayan Wi-Fi UDP ve BLE soket görevleri.<br>• **Kuyruk Tüketici Görevleri:** Filtreleme boru hattı için çekirdekler arası kuyruktan veri okuma. |
| **Gömülü Sürücüler (C/C++)** | • **Sürekli DMA ADC Sürücüsü:** ESP32-S3 ADC1 çevre birimini 2000 Hz 4 kanal dairesel ping-pong bellek tamponlarına bağlayan düşük seviyeli sürücü.<br>• **Yedek Donanım Sürücüsü:** MCP3008 ADC için yüksek hızlı SPI2 master sürücüsü. | • **Gömülü DSP Filtreleme:** C++ içinde gerçek zamanlı IIR bant geçiren (20 - 450 Hz) ve 50 Hz çentik (notch) filtre basamakları.<br>• **IMU I2C Sürücüsü & Kinematik:** MPU-6050 sürücüsü ve kol açısı için Tamamlayıcı / Madgwick yönelim filtresi. |
| **Uç Yapay Zeka (Edge AI)** | • Kuantalanmış 1D-CNN ve Derin MLP mimarilerini **TensorFlow Lite for Microcontrollers (TFLM)** ile ESP32-S3 Core 1'e gömme.<br>• Matris çarpımlarını Espressif **ESP-NN vektör hızlandırma komutları** ile optimize etme.<br>• Donanım çıkarım gecikmesi (Inference Latency), Tensor Arena dinamik RAM kullanımı ve Flash ayak izi kıyaslaması. | • Gerçek zamanlı Hudgins öznitelik çıkarıcı ve hafif C (`emlearn`) ile Destek Vektör Makineleri (SVM) çıkarım motoru.<br>• Hareket sınıflandırmasını uzamsal kol yönelimiyle birleştiren durum makinesi (State Machine). |
| **Çevrimdışı Modelleme (Python)** | • Zaman serisi dalga formu ön işleme, kayan pencereleme (Sliding Window), 1D-CNN ve Derin MLP mimari tasarımı.<br>• INT8 eğitim sonrası kuantalama (PTQ), hiperparametre optimizasyonu, Kayıp/Doğruluk/F1 analizleri. | • Zaman uzayı öznitelik uzayı formülasyonu, boyut indirgeme, öznitelik önem analizi.<br>• Klasik makine öğrenmesi (SVM, Random Forest) eğitimi ve çapraz doğrulama. |
| **Donanım & Telemetri** | • Çok kanallı kuru elektrot analog sinyal yönlendirmesi, analog toprak ekranlama.<br>• Otomatik veri toplama arayüzü ve gerçek zamanlı etiketleme protokolü (`record_live_emg.py`). | • 3D dijital ikiz el simülasyonuna kablosuz telemetri paketi iletimi (UDP üzerinden JSON/Protobuf).<br>• Hibrit kinematik durum makinesi entegrasyonu ve pertinaks lehimleme. |

> [!IMPORTANT]
> **Ziya'nın Odak Noktası:** Donanım lehimleme, IIR dijital filtreleme, MPU6050 Madgwick açı hesabı ve Three.js 3D web simülasyonu Evrim'in görevleridir. Ziya doğrudan **Derin TinyML modelleri (1D-CNN, MLP), TFLite INT8 kuantalama, C dizisi ihracı (`model_data.h`), Core 1 TFLM çıkarımı ve veri toplama boru hattı** üzerine yoğunlaşmalıdır.

---

## 2. Hakem ve Claude Düzeltmesi: Evrensel Öznitelik Mühendisliği

İnternetteki açık veri setleri ile kendi ürettiğimiz donanım arasında sinyal tipi farkı bulunmaktadır:

1. **Açık Veri Setlerinde (Ham AC Sinyal):**
   Sinyal referans hattı (0V) etrafında hem artı (+) hem eksi (-) yönde salınım yapar. Bu nedenle klasik Hudgins özniteliklerindeki **ZC (Zero Crossing - Sıfır Geçiş Sayısı)** anlamlı bilgi üretir.
2. **Kendi TL084 Zarf (Envelope) Sensörümüzde:**
   Sensör üzerindeki tam dalga doğrultucu ve alçak geçiren filtre devresi sinyali doğrultup düzleştirerek `0 - 3.3 V` aralığında pozitif bir DC gerilim zarfı üretir. Sinyal sıfırın altına hiç inmediği için **ZC değeri her zaman 0 çıkar**.
3. **Çözüm (Evrensel 19 Öznitelik Vektörü):**
   Kendi boru hattımızda ZC yerine hem ham AC veride hem de DC zarf verisinde matematiksel olarak kararlı çalışan öznitelikleri seçtik:
   - **4 EMG Kanalı x 4 Öznitelik = 16 Öznitelik:**
     - **MAV (Mean Absolute Value):** Sinyalin pencere içindeki genlik ortalaması. Kas kasılmasının şiddetini temsil eder.
     - **RMS (Root Mean Square):** Sinyalin karesel ortalamasının karekökü. Sinyal gücünü ve enerjisini gösterir.
     - **VAR (Variance):** Sinyalin varyansı (güç dağılımı). Kas tonusu değişimlerini yakalar.
     - **MFD (Mean First Difference / Slope):** Komşu örnekler arasındaki ortalama mutlak fark `Ortalama(|x[n] - x[n-1]|)`. Sinyalin frekans/değişim hızını temsil eder; sıfırı kesmesine gerek yoktur.
   - **3 IMU Ekseni x 1 Öznitelik = 3 Öznitelik:**
     - `Ortalama(ax)`, `Ortalama(ay)`, `Ortalama(az)`: Kolun yerçekimine göre uzamsal duruşunu verir.
   - **Toplam Vektör Boyutu = 19 Değer.**

Bu 19 elemanlı öznitelik vektörü sayesinde, açık veri setleriyle eğittiğimiz modeli tek bir satır kod değiştirmeden kendi sensör verilerimizle test edebiliriz.

---

## 3. Ziya'nın AI & TinyML Adım Adım Eylem Planı

Aşağıdaki 7 adım, Ziya'nın sunum ve mezuniyet teslimine kadar adım adım izlemesi gereken resmi yol haritasıdır:

### Adım 1: Veri Formatı ve Kayan Pencereleme (Sliding Window)
- **Örnekleme Frekansı:** 100 Hz (veya 1000 Hz'den 100 Hz'e indirgenmiş veri).
- **Pencere Genişliği:** 200 ms (100 Hz'de pencere başına 20 örnek).
- **Adım (Stride / Hop Size):** 50 ms (her 50 ms'de bir yeni çıkarım, 15 örnek örtüşme - overlap).
- **Sınıflar (5 Hareket Sınıfı):**
  - 0: `REST` (Dinlenme / Boşta)
  - 1: `FIST` (Yumruk / Power Grasp - FDS kası)
  - 2: `OPEN` (Eli Açma - ED kası)
  - 3: `PINCH` (Cımbız Kavrama - FPL kası)
  - 4: `POINT` (İşaret Etme - ED + EPL kası)

### Adım 2: Model Mimarilerinin Tasarımı (TFLM Kısıtlamaları)
Mikrodenetleyici (ESP32-S3) üzerinde çalışacak yapay zeka modelleri TFLite Micro kütüphanesinin desteklediği standart katmanları kullanmalıdır:
1. **Model A: 1D-CNN (Zaman Serisi Derin Öğrenme):**
   - Giriş: `(20 örnek, 4 kanal)` veya `(20 örnek, 7 kanal - 4 EMG + 3 IMU)`
   - Katmanlar: `Conv1D(16, kernel_size=3, padding='same', activation='relu')` -> `MaxPooling1D(pool_size=2)` -> `Conv1D(32, kernel_size=3, activation='relu')` -> `GlobalAveragePooling1D()` -> `Dense(32, activation='relu')` -> `Dense(5, activation='softmax')`
   - Flash Boyutu: ~12 - 18 KB
   - Tensor Arena RAM: ~15 - 22 KB
2. **Model B: Derin MLP (Öznitelik Tabanlı Derin Ağ):**
   - Giriş: `(19 öznitelik,)`
   - Katmanlar: `Dense(32, activation='relu')` -> `Dropout(0.2)` -> `Dense(16, activation='relu')` -> `Dense(5, activation='softmax')`
   - Flash Boyutu: ~4 - 8 KB
   - Tensor Arena RAM: ~6 - 10 KB

### Adım 3: Eğitim ve Doğrulama (Python)
- Kayıp Fonksiyonu: `SparseCategoricalCrossentropy` veya `CategoricalCrossentropy`
- Optimizasyon: `Adam(learning_rate=0.001)`
- Erken Durdurma (Early Stopping): Aşırı öğrenmeyi (overfitting) önlemek için `patience=10`.
- Değerlendirme Metrikleri: Doğruluk (Accuracy), Karışıklık Matrisi (Confusion Matrix), Sınıf Bazlı F1-Skoru.

### Adım 4: INT8 Eğitim Sonrası Kuantalama (Post-Training Quantization - PTQ)
Float32 formatındaki ağırlıklar ve aktivasyonlar INT8 (8-bit tam sayı) formatına dönüştürülmelidir.
- TFLite Converter kullanılır.
- Temsili Veri Seti Üreticisi (`representative_dataset_gen`) ile dinamik aralık kalibre edilir:
  ```python
  converter = tf.lite.TFLiteConverter.from_keras_model(model)
  converter.optimizations = [tf.lite.Optimize.DEFAULT]
  converter.representative_dataset = representative_data_gen
  converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
  converter.inference_input_type = tf.int8
  converter.inference_output_type = tf.int8
  tflite_quant_model = converter.convert()
  ```
- Sonuç: Model boyutu 4 kat küçülür, ESP32-S3 üzerinde ESP-NN SIMD komutlarıyla 3 ila 5 kat daha hızlı çalışır.

### Adım 5: C Başlık Dosyası Üretimi (`model_data.h`)
Kuantalanmış `.tflite` ikili dosyası ESP32-S3 C++ koduna bir dizi (byte array) olarak aktarılır:
```bash
xxd -i model_quant_int8.tflite > model_data.h
```
Üretilen `model_data.h` dosyası doğrudan `firmware/` altındaki Core 1 TFLM görevine dahil edilir.

### Adım 6: ESP32-S3 Core 1 TFLM Görevine Entegrasyon
ESP32-S3 Core 1 üzerinde çalışan `vTaskTinyMLInference` görevi:
1. `tflite::MicroErrorReporter` ve `tflite::AllOpsResolver` (veya mikromodeller için `MicroMutableOpResolver`) başlatır.
2. Statik Tensor Arena ayırır:
   ```cpp
   constexpr int kTensorArenaSize = 30 * 1024; // 30 KB SRAM
   uint8_t tensor_arena[kTensorArenaSize];
   ```
3. `tflite::MicroInterpreter` nesnesini oluşturur ve tensörleri ayrıştırır (`AllocateTensors()`).
4. Giriş tensörünü normalize edilmiş INT8 verilerle doldurur (`input->data.int8[i] = ...`).
5. Çıkarımı koşturur (`interpreter->Invoke()`).
6. Çıkarım süresini mikrosaniye çözünürlüğünde (`esp_timer_get_time()`) ölçer (Hedef: < 15 ms).
7. Kazanan sınıfı (`argmax`) belirler ve Core 0 telemetri kuyruğuna gönderir.

### Adım 7: Çarşamba Günü Sunumu için Hazırlanması Gerekenler
Sunumda Ziya'nın sunacağı kısımlar:
1. **TinyML Mimarisi Slaytı:**
   - 1D-CNN ve MLP ağ şeması.
   - Float32'den INT8'e dönüşüm ve bellek kazanımı tablosu.
2. **Evrensel Öznitelik Formülasyonu Slaytı:**
   - Zarf sinyali ile ham sinyal farkı (ZC yerine MFD seçimi) ve akademik gerekçesi.
3. **Model Başarım Grafikleri:**
   - Loss & Accuracy eğitim eğrileri.
   - 5 sınıflı Confusion Matrix (Karışıklık Matrisi).
4. **Gömülü Sistem Performans Metrikleri:**
   - Flash Ayak İzi: < 20 KB.
   - Tensor Arena RAM Kullanımı: < 25 KB.
   - Çıkarım Gecikmesi: < 15 ms (200 ms pencere süresinin oldukça altında).

---

## 4. Klasör İçeriği ve Araçlar

Bu klasörde yer alan hazır araç ve scriptler:

| Dosya | Açıklama |
|---|---|
| [features.py](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/features.py) | Hem ham hem zarf sinyalleri için MAV, RMS, VAR, MFD öznitelik çıkarıcı ve kayan pencereleme motoru. |
| [models.py](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/models.py) | TFLM uyumlu 1D-CNN ve Derin MLP Keras mimari tanımları. |
| [train_tinyml.py](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/train_tinyml.py) | Veri yükleme, eğitim, F1/Confusion Matrix analizi, INT8 kuantalama ve `model_data.h` C başlığı üretim boru hattı. |
| [benchmark_tflite.py](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/benchmark_tflite.py) | Üretilen TFLite modelinin dosya boyutu, katman INT8 tipleri ve Tensor Arena RAM gereksinimini hesaplayan araç. |
| [requirements.txt](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml/requirements.txt) | Python sanal ortamı için kütüphane bağımlılıkları. |

---

## 5. Hızlı Başlangıç (Nasıl Çalıştırılır?)

### 1. Sanal Ortamı Kurma ve Paketleri Yükleme
```bash
cd /home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/tinyml
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Sentetik Pilot Veriyle Boru Hattını Test Etme (Donanım Olmadan)
```bash
python3 train_tinyml.py --mock --model_type cnn --epochs 15 --quantize
```

### 3. Kendi Topladığımız CSV Verileriyle Eğitme
```bash
python3 train_tinyml.py --dataset_dir ../data/deneme/ --model_type mlp --epochs 30 --quantize --output_header model_data.h
```

### 4. TFLite Modelini Analiz Etme
```bash
python3 benchmark_tflite.py --model_path model_quant_int8.tflite
```
