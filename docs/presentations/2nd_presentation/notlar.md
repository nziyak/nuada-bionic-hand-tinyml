# 2. Mezuniyet Projesi Sunum Notları (2 Aralık 2026)

Bu dosya, Salı 1 Aralık saat 22:00'ye kadar yüklenecek olan 6 dakikalık 2. Ara Sunum slaytlarını hazırlarken kullanılacak kısa ve net teknik notları içerir.

---

## 1. Sunum Formatı ve Kısıtları
* **Toplam Süre:** 6 dakika (3 dk Nuri Ziya Kırtepe + 3 dk Evrim Doğa Solmaz).
* **Şablon:** GTU resmi şablonu kullanılacak ([GTU_graduate_project_presentation_template.pptx](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/docs/presentations/GTU_graduate_project_presentation_template.pptx)).
* **Kural:** Yapay zeka ile otomatik sunum üretmek yasaktır; öğrencilerin kendi emeğini ve açık görev dağılımını yansıtmalıdır.
* **Teslim:** 1 Aralık Salı 22:00'ye kadar Teams üzerinden yükleme.

---

## 2. Denek Sayısı ve Literatür Doğrulaması
* **Literatür Standardı:** sEMG tabanlı biyomekanik ve protez çalışmalarında standart denek sayısı **8 ila 15 kişidir**.
  * Hudgins et al. (1993, IEEE TBME): 5 denek.
  * Fougner et al. (2011, IEEE TNSRE - Kol açısı ve IMU füzyonu): 10 denek.
  * Hargrove et al. (2007, IEEE TBME): 12 denek.
  * Tenore et al. (2009, IEEE TBME - Tekil parmak çözümü): 6 denek.
* **Neden 50 Kişi Değil?:** sEMG'de sorun veri sayısı değil, bireyler arası **biyomekanik alan kaymasıdır (domain shift)**. Yağ dokusu kalınlığı, kas anatomisi ve elektrotun 5 mm kayması sinyali tamamen değiştirir. 50 kişi toplamak bu biyolojik farkı çözmez.
* **Dünyanın En Büyük Açık sEMG Veri Seti:**
  * **NinaPro Benchmark (DB2):** 40 denek, 40 hareket, 2 kHz örnekleme.
  * Veri Seti Portalı: [https://ninapro.hevs.ch](https://ninapro.hevs.ch)
  * Nature Scientific Data Makalesi: [https://doi.org/10.1038/sdata.2014.43](https://doi.org/10.1038/sdata.2014.43)

---

## 3. Model Doğrulama: LOSO (Leave-One-Subject-Out) Cross-Validation
* Cross-validation için **LOSO** kullanacağız.
* 15 subject'ten 1'ini çıkarıp kalanıyla (14 kişiyle) modeli eğiteceğiz, sonra dışarıda bıraktığımız o 1 kişiyle test edeceğiz.
* Bu işlemi 15 denek için 15 kez tekrarlayıp ortalama genelleme başarımını raporlayacağız.
* Bu yöntem, modelin hiç görmediği yeni bir kullanıcıdaki gerçek dünya başarımını dürüstçe ölçmenin akademik altın standardıdır.

---

## 4. Kullanıcı Genellemesi: Plug-and-Play & Few-Shot Adaptation
* **Hedef:** Biyonik el bandını yeni birine takınca doğrudan doğru sınıflandırma yapması (Plug-and-play).
* **Zorluk:** Sıfır kalibrasyonlu (zero-shot) genel modellerde doğruluk biyolojik farklar nedeniyle %60 - %70 seviyelerine düşer.
* **Çözüm (Few-Shot Domain Adaptation):**
  * Yeni kullanıcı kol bandını taktığında her hareketten sadece 1 kez (3 saniye) yapar (toplam 12-15 saniyelik tek seferlik süreç).
  * Önceden 15 kişiyle eğitilmiş temel model, bu 15 saniyelik veriyle son sınıflandırma katmanını kalibre eder (transfer learning).
  * Böylece yeni kullanıcıda doğruluk anında %90+ seviyesine çıkar.

---

## 5. Sinyal Tipi ve 19-Öznitelikli Evrensel Vektör
* **Zarf (Envelope) Sensör Farkı:** Yeni aldığımız TL084 tabanlı sensör donanımsal doğrultma ve filtreleme yaparak 0 - 3.3 V pozitif DC zarf üretir; sinyal sıfırın altına inmez.
* **ZC Düzeltmesi:** Sinyal sıfırı kesmediği için klasik Hudgins ZC (Zero Crossing) daima 0 çıkar. ZC yerine türev/eğim ölçen **MFD (Mean First Difference)** kullanıyoruz.
* **19 Elemanlı Vektör Yapısı:**
  * 4 EMG Kanalı x 4 Öznitelik = 16 Öznitelik (MAV, RMS, VAR, MFD).
  * 3 IMU Ekseni = 3 Öznitelik (Ortalama ax, ay, az - kolun yerçekimine göre uzamsal açısı).
* **Avantajı:** Hem açık veri setlerindeki ham AC sinyallerde hem de kendi donanımımızın DC zarf sinyallerinde kod değiştirmeden çalışır.

---

## 6. Görev Dağılımı ve Sunum Konuları

### Nuri Ziya Kırtepe (TinyML, Hard RTOS & Yüksek Hızlı Örnekleme):
* **Zaman Serisi & Pencereleme:** 100 Hz örneklemede 200 ms kayan pencere (20 örnek) ve 50 ms kayma adımı (%75 örtüşme).
* **Model Mimarileri:** 1D-CNN (zamansal evrişim) ve Derin MLP (19 öznitelikli).
* **Model Kuantalama:** TensorFlow Lite INT8 Post-Training Quantization (PTQ) ile model boyutunu 4 kat küçültme.
* **Gömülü Sistem Başarımı:** ESP32-S3 Core 1 üzerinde `vTaskTinyMLInference` hard real-time task; ESP-NN vektör hızlandırması ile < 15 ms çıkarım süresi, < 25 KB Tensor Arena RAM.
* **Veri Toplama:** Continuous DMA ADC sürücüsü ve `record_live_emg.py` otomatik kayıt aracı.

### Evrim Doğa Solmaz (Donanım, Gömülü DSP, Kinematik & Simülasyon):
* **Donanım & Dağıtım Kartı:** Pertinaks üzerine 4-kanallı TL084 sEMG sensör dağıtımı, dirençli gerilim bölücüler ve MPU-6050 montajı.
* **Gömülü C++ DSP:** 20 - 450 Hz IIR bant geçiren filtre ve 50 Hz çentik (notch) filtre basamakları.
* **IMU Kinematik Füzyon:** MPU-6050 Complementary / Madgwick filtresiyle kolun uzamsal açısının (pitch/roll) gerçek zamanlı takibi.
* **Kablosuz Telemetri & Dijital İkiz:** FreeRTOS Core 0 soft real-time task'ları (LwIP UDP) ve Three.js 3D sanal biyonik el simülasyonu.

---

## 7. Güç ve Pil Gereksinimi Notu
* **Laboratuvar / Test Aşaması:** Çift çıkışlı DC güç kaynağı ile simetrik ±5.0 V besleme (K+ = +5V, K0 = GND/0V, K- = -5V).
* **Pil ile Çalışma Kuralı:**
  * Tekli 3.7 V LiPo veya 2 x 3.7 V (±3.7 V) **kullanılamaz** (TL084 op-amp'leri ±4.5V altında düzgün çalışmaz, sinyal kırpılır).
  * **En Pratik Çözüm:** 2 adet 9V pil seri bağlanarak simetrik **±9.0 V** elde edilir.
  * **Direnç Güvenliği:** ±9V pilde çıkış 7 - 7.5V'a kadar çıkabileceğinden gerilim bölücüde 20 kΩ yerine **4.7 kΩ** (veya 10k üst, 4.7k alt) direnç takılarak ESP32 girişi maksimum 2.4V seviyesinde korunur.

---

## 8. Donanımsız Doğrulama: Açık Veri Setleri (Public Benchmark) Stratejisi
* **Donanım Beklenirken Yapılanlar:** Donanım lehimleme ve montaj sürecindeyken TinyML boru hattı durmadı; internetteki açık veri setleri üzerinde uçtan uca test ediliyor.
* **Kullanılan Açık Veri Setleri:**
  * **UCI EMG Data for Gestures:** 36 denek, ön kol 8 kanal sEMG, CSV formatında açık veri -> [https://archive.ics.uci.edu/dataset/612/emg+data+for+gestures](https://archive.ics.uci.edu/dataset/612/emg+data+for+gestures).
  * **NinaPro Benchmark (DB2):** 40 denek, el/bilek hareketleri referans veritabanı -> [https://ninapro.hevs.ch](https://ninapro.hevs.ch).
* **Doğrulama Amacı:** 19 elemanlı evrensel öznitelik formülasyonunun ve INT8 PTQ kuantalamanın gerçek denek verilerinde çalıştığını kanıtlamak, eğitim/doğruluk eğrilerini ve Confusion Matrix'i sunuma eklemek.
* **Hemen Dağıtım Avantajı:** ESP32 kartı Evrim'den teslim alındığı an sıfırdan model geliştirmeye gerek kalmadan, üretilen `model_data.h` C başlığı doğrudan firmware'e yüklenip ilk saniyeden çalıştırılabilecek.
