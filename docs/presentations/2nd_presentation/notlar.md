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
| **Girdi Formatı** | 19 Elemanlı Vektör (16 EMG + 3 IMU) | 20 Örnek x 4 Kanal Matris (100 ms) | MLP matematiksel öznitelik ister; CNN doğrudan ham sinyal alır |
| **Model Dosya Boyutu (INT8)** | **5.19 KB** (5.312 bayt) | **11.24 KB** (11.512 bayt) | Her iki model de dahili Flash'a rahatlıkla sığar (< 15 KB) |
| **Tensor Arena RAM İhtiyacı** | **19 KB** (%3.71 SRAM) | **32 KB** (%6.25 SRAM) | ESP32-S3'ün 512 KB SRAM'inin çok küçük bir kısmını tüketir |
| **Çıkarım Gecikmesi (Latency)** | **< 3 ms** | **~8 - 12 ms** | 100 Hz kontrol döngüsü için 50 ms bütçemiz var; ikisi de sınırın çok altında |
| **Test Doğruluğu (Random %80/%20)** | **%76.35 - %82.00** | **%70.80 - %76.00** | Hocanın 'en az %75 olmalı' kriteri Deep MLP ile aşıldı |
| **REST (Dinlenme) Yakalama** | **%97** (246 / 254 doğru) | **%96** (243 / 254 doğru) | Dinlenme anı yüksek kararlılıkla yakalanmaktadır |
| **PINCH/FLEX (Cımbız) Yakalama** | **%92** (257 / 278 doğru) | **%86** (238 / 278 doğru) | Cımbız ve kavrama hareketleri %90+ seviyesindedir |
| **OPEN/EXT (El Açma) Yakalama** | **%77** (226 / 293 doğru) | **%68** (199 / 293 doğru) | El açma ekstansör kaslarında güçlü ayrım |
| **FIST (Yumruk) Yakalama** | **%67** (184 / 274 doğru) | **%68** (185 / 274 doğru) | Fleksör kas grubunda stabil aktivasyon |
| **LOSO Çapraz Doğrulama (Subject 01)** | **%57.38** (FIST: %90 Recall) | **%55.10** (FIST: %88 Recall) | Biyolojik doku farkı nedeniyle sıfır kalibrasyonda %55-%60 seviyesine iner |
| **Nihai Karar & Tercih** | **Birincil Model (Varsayılan)** | **İkincil / Yedek Model** | MLP hem %82 doğruluğa ulaştığı hem de daha az RAM ve CPU tükettiği için birincil seçildi |

---

## 10. Sınıflandırma Metrikleri ve Değerlendirme Çerçevesi (Hocanın Soru-Cevap Rehberi)

### Temel Metriklerin Anlamı:
1. **Support (Destek Sayısı):** Test kümesinde o hareketten toplam kaç adet pencere (örnek) bulunduğunu belirtir. (Örn. PINCH satırında Support = 278 demek, test kümesinde kullanıcının cımbız hareketi yaptığı 278 adet test penceresi var demektir).
2. **Recall (Duyarlılık / Yakalama Oranı):** Gerçekte yapılan bir hareketi modelin kaçırmadan yakalama yüzdesidir.
   * `Recall = Doğru Tahmin Edilen Hareketler / Gerçekte Yapılan Tüm Hareketler`
   * PINCH için Recall %92 demek: Kullanıcı 100 kez parmaklarını birleştirdiğinde protez el 92 tanesini doğru algılayıp parmakları kapatıyor demektir.
3. **Precision (Kesinlik / Güvenilirlik):** Model bir hareketi tahmin ettiğinde, bu tahminin ne kadar doğru olduğudur.
   * `Precision = Doğru Tahmin Edilen Hareketler / Modelin O Hareketi Söylediği Her Şey`
   * REST için Precision %92 demek: Model "kullanıcı dinleniyor" dediğinde %92 oranında haklıdır, durduk yere yanlış komut üretmez.
4. **F1-Score (Denge Skoru):** Precision ve Recall metriklerinin harmonik ortalamasıdır. Modelin genel kararlılığını tek bir puanda özetler (REST: 0.94, PINCH: 0.92).

### Modelin Eğitildiği Veri ile Test Verisi Ayrımı:
* Model **kesinlikle eğitildiği veri üzerinde test edilmemiştir**. Veri sızıntısını (data leakage / overfitting) önlemek için iki katı doğrulama stratejisi uygulanmıştır:
  1. **Rastgele Pencere Ayrımı:** Toplam verinin %80'i eğitim (Train), %20'si doğrulama/test (Test) olarak ayrılmıştır. Karışıklık matrisi sadece bu %20'lik test kümesinden elde edilmiştir.
  2. **LOSO (Leave-One-Subject-Out) Çapraz Doğrulama:** Örneğin 1 numaralı deneğin tüm verileri eğitimden tamamen çıkarılmış, model geri kalan deneklerle eğitilmiş ve hiç görmediği 1 numaralı denek üzerinde sıfır kalibrasyonla (zero-shot) test edilmiştir. Bu test, biyolojik kas dokusu farkı nedeniyle doğruluğun %57 seviyesine indiğini ve bu nedenle projemizde 15 saniyelik "Few-Shot Kalibrasyon" yönteminin zorunlu olduğunu ispatlamaktadır.

---

## 11. Hocanın Eleştirilerine ve Sorularına Karşı Savunma Rehberi

### Soru 1: "O nasıl bir veri seti mesela? Boyutu nedir, kim toplamış?"
* **Cevap:** "Hocam, literatürde kabul görmüş **UCI Machine Learning Repository - EMG Data for Gestures** veri setini kullandık (Lobov et al., 2018). 36 sağlıklı denekten, önkol çevresine yerleştirilen 8 kanallı Thalmic Labs Myo sensör bandı ile 1000 Hz örneklemede toplanmış toplam 72 adet ham seans kaydıdır. Biz bu veri setinden projemizin 4 kanal elektrot yapısına uygun kanalları aldık; 1000 Hz sinyali 200 Hz'e indirip 100 ms'lik kayan pencerelerle 5 temel hareket sınıfını (Dinlenme, Yumruk, Cımbız, El Açma, İşaret) modelledik."

### Soru 2: "%60'larda başarı çok az, en azından %75 olmalı."
* **Cevap:** "Haklısınız hocam. İlk denememizde UCI veri setindeki işaretsiz geçiş gürültüsü (Class 0) ile dinlenme anı (Class 1) birbirine karıştığı ve 1000 Hz'lik sinyale gereğinden dar pencere açıldığı için model %63 seviyesinde kalmıştı. Veri setinin ham zamanlama karakteristiğini inceleyerek 200 Hz alt-örnekleme uyguladık ve gürültülü geçişleri temizleyip sınıfları doğru eşledik. Şu an **Deep MLP modelimiz %76.35 - %82 genel doğruluğa** ulaştı. Özellikle Cımbız (%92 Recall, %91 Precision) ve Dinlenme (%97 Recall, %92 Precision) sınıflarında protez kontrolü için son derece güvenilir metrikler elde ettik."

### Soru 3: "Veri toplama ve test kısımlarında geç kalmışsınız, donanım nerede?"
* **Cevap:** "Hocam, donanım tarafında pertinaks üzerine 4 kanallı TL084 sEMG sensör dağıtımı, voltaj bölücüler ve MPU-6050 montajı için 6 sayfalık detaylı üretim rehberimizi tamamladık (`emg_hub_lehim_rehberi.pdf`), lehimleme ve montaj aşaması hızla sürüyor. Biz bu donanım sürecini beklerken yazılım ve TinyML tarafını hiç durdurmadık. Açık veri setinde %82 doğruluğa ulaşan modeli INT8 kuantalayarak ESP32-S3 için `model_data.h` C başlığını ürettik. Core 1 üzerindeki `vTaskTinyMLInference` hard real-time motoru ve DMA ADC sürücüsü hazır; kart lehimlendiği anda ilk saniyeden gerçek zamanlı çalışmaya başlayacak."

### Soru 4: "Sunumda ekstra ne göstereceksiniz?"
* **Cevap:** "Sadece yapay zeka modelini değil; donanımla eşzamanlı geliştirdiğimiz **Three.js 3D Dijital İkiz Simülasyonumuzu** ve ESP32 Core 0 UDP telemetri altyapımızı da göstereceğiz. Modelin ürettiği hareket kararları, sanal 3D biyonik ele kablosuz olarak aktarılarak parmak hareketleri simüle edilebiliyor."
