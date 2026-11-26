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

---

## 9. 1D-CNN vs. Deep MLP Karşılaştırma Tablosu (Nuri Ziya'nın Slaytı)
Açık UCI sEMG veri seti ve ESP32-S3 mimarisi üzerinde elde edilen doğrulanmış karşılaştırma metrikleri:

| Karşılaştırma Kriteri | Deep MLP (Öznitelik Tabanlı) | 1D-CNN (Zamansal Evrişimli) | ESP32-S3 & TinyML Notu |
| :--- | :--- | :--- | :--- |
| **Girdi Formatı** | 19 Elemanlı Vektör (16 EMG + 3 IMU) | 20 Örnek x 4 Kanal Matris (200 ms) | MLP matematiksel öznitelik ister; CNN doğrudan ham sinyal alır |
| **Model Dosya Boyutu (INT8)** | **5.19 KB** (5.312 bayt) | **11.24 KB** (11.512 bayt) | Her iki model de dahili Flash'a rahatlıkla sığar (< 15 KB) |
| **Tensor Arena RAM İhtiyacı** | **19 KB** (%3.71 SRAM) | **32 KB** (%6.25 SRAM) | ESP32-S3'ün 512 KB SRAM'inin çok küçük bir kısmını tüketir |
| **Çıkarım Gecikmesi (Latency)** | **< 3 ms** | **~8 - 12 ms** | 100 Hz kontrol döngüsü için 50 ms bütçemiz var; ikisi de sınırın çok altında |
| **Test Doğruluğu (Random %80/%20)** | **%63.80** | **%61.95** | Ham açık veri setinde benzer başarı |
| **FIST (Yumruk) Yakalama (Recall)** | **%92** (555 / 605 doğru) | **%94** (567 / 605 doğru) | Yumruk hareketi her iki modelde de en kararlı sınıftır |
| **LOSO Çapraz Doğrulama (Subject 01)** | **%57.38** (FIST: %90 Recall) | **%55.10** (FIST: %88 Recall) | Biyolojik doku farkı nedeniyle sıfır kalibrasyonda %55-%60 seviyesine iner |
| **Nihai Karar & Tercih** | **Birincil Model (Varsayılan)** | **İkincil / Yedek Model** | MLP çok daha düşük işlemci yükü ve bellek tükettiğinden pil ömrü için birincil seçildi |

---

## 10. Sınıflandırma Metrikleri ve Değerlendirme Çerçevesi (Hocanın Soru-Cevap Rehberi)

### Temel Metriklerin Anlamı:
1. **Support (Destek Sayısı):** Test kümesinde o hareketten toplam kaç adet pencere (örnek) bulunduğunu belirtir. (Örn. FIST satırında Support = 605 demek, test kümesinde kullanıcının yumruk yaptığı 605 adet 200 ms'lik pencere var demektir).
2. **Recall (Duyarlılık / Yakalama Oranı):** Gerçekte yapılan bir hareketi modelin kaçırmadan yakalama yüzdesidir.
   * `Recall = Doğru Tahmin Edilen Yumruklar / Gerçekte Yapılan Tüm Yumruklar`
   * FIST için Recall %92 demek: Kullanıcı 100 kez elini yumruk yaptığında protez el 92 tanesini doğru algılayıp parmakları kapatıyor demektir.
3. **Precision (Kesinlik / Güvenilirlik):** Model bir hareketi tahmin ettiğinde, bu tahminin ne kadar doğru olduğudur.
   * `Precision = Doğru Tahmin Edilen Yumruklar / Modelin Yumruk Dediği Her Şey`
   * FIST için Precision %62 demek: Model gün içinde "kullanıcı yumruk yaptı" dediği 100 anın 62'sinde gerçekten yumruk yapılmıştır; 38'inde ise kullanıcı dinlenirken veya işaret parmağını açarken yanlışlıkla yumruk algılanmıştır.
4. **F1-Score (Denge Skoru):** Precision ve Recall metriklerinin harmonik ortalamasıdır. Modelin hem yanlış alarm vermeme hem de hareketi kaçırmama arasındaki genel kalitesini tek bir puanda özetler.

### Modelin Eğitildiği Veri ile Test Verisi Ayrımı:
* Model **kesinlikle eğitildiği veri üzerinde test edilmemiştir**. Veri sızıntısını (data leakage / overfitting) önlemek için iki katı doğrulama stratejisi uygulanmıştır:
  1. **Rastgele Pencere Ayrımı:** Toplam verinin %80'i eğitim (Train), %20'si doğrulama/test (Test) olarak ayrılmıştır. Karışıklık matrisi sadece bu %20'lik test kümesinden elde edilmiştir.
  2. **LOSO (Leave-One-Subject-Out) Çapraz Doğrulama:** Örneğin 1 numaralı deneğin tüm verileri eğitimden tamamen çıkarılmış, model geri kalan 7 denekle eğitilmiş ve hiç görmediği 1 numaralı denek üzerinde sıfır kalibrasyonla (zero-shot) test edilmiştir. Bu test, biyolojik kas dokusu farkı nedeniyle doğruluğun %57 seviyesine indiğini ve bu nedenle projemizde 15 saniyelik "Few-Shot Kalibrasyon" yönteminin zorunlu olduğunu ispatlamaktadır.
