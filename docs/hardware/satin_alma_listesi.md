# Nuada: Biyonik El Projesi — Malzeme ve Satın Alma Rehberi (Çoklu Denek & Ekonomik Model)

Bu rehber, projemizin **çok sayıda farklı insandan (multi-subject)** veri toplama hedefine ve danışman hocamızın **"araya ekstra devre kurmayın, modülleri olduğu gibi kullanın"** direktifine göre optimize edilmiş nihai malzeme listesini, parça detaylarını ve veri toplama protokolünü içerir.

---

## 🎯 Neden Tek Kullanımlık Ped Değil de "Tüp Jel + Çıtçıtlı Kol Bandı"?

İlk başta düşünülen tek kullanımlık yapışkanlı pedler (50'li paket), her ölçümde 9 elektrot (4 kanal x 2 + 1 referans) kullanıldığı için **yalnızca 5 kişide tükenmektedir**. Çok sayıda insandan veri toplayacağımız için bu hem ciddi bir maliyet hem de israf yaratır.

Bunun yerine biyomedikal laboratuvarlarında kullanılan en akıllıca yöntemi uyguluyoruz:
* **Elastik Kol Bandı:** Çıtçıtları kola sımsıkı bastırarak **mekanik olarak sabitler (kaymayı önler)**.
* **Tüp İletken Jel:** Her ölçüm öncesi metal çıtçıtların üzerine birer mercimek tanesi kadar sürülür; cilt direncini sıfıra indirir ve sinyali cam gibi temiz yapar.
* **Sonsuz Kullanım:** Ölçüm bitince çıtçıtlar ıslak mendille silinir; aynı kol bandı tek kuruş harcanmadan 100 farklı kişide binlerce kez tekrar kullanılır!

---

## 🛒 1. Hızlı Satın Alma Özeti (BOM Listesi)

| Sıra | Malzeme Adı | Adet | Sitelerde Ne Diye Aratacaksınız? | Tahmini Fiyat |
|:---:|---|:---:|---|:---:|
| **1** | **ESP32-S3 Geliştirme Kartı** | 1 Adet | `ESP32-S3-DevKitC-1 N16R8 Çift Type-C` *(WROOM-1 Dahili Antenli)* | ~250 - 300 TL |
| **2** | **AD8232 Sensör Modülü** | 4 Adet | `AD8232 EKG Nabız Sensörü Modülü (Kablolu Set)` | 4 x ~110 = 440 TL |
| **3** | **MPU-6050 IMU Modülü** | 1 Adet | `GY-521 MPU-6050 6 Eksen İvme ve Jiroskop Modülü` | ~70 - 90 TL |
| **4** | **İletken EKG / Ultrason Jeli (Tüp)** | 1 Adet (250 ml) | `Medikal İletken EKG / Ultrason Jeli 250 ml` | ~35 - 50 TL |
| **5** | **Paslanmaz Çelik Çıtçıt Buton Seti** | 1 Paket | `Paslanmaz Çelik Çıtçıt Düğme Seti (Metal / 10-12 mm)` *(Tuhafiyeden/Trendyol'dan)* | ~30 - 40 TL |
| **6** | **Elastik Cırt Cırtlı Kol Bandı** | 1 Adet | `Elastik Cırt Cırtlı Bandaj / Neopren Bileklik` *(Eczaneden/Spor mağazasından)* | ~40 - 60 TL |
| **7** | **Jumper Kablo Seti** | 1 Paket | `40'lı Dişi-Dişi Jumper Kablo (20 cm)` | ~40 TL |
| **8** | **Type-C Data Kablosu** | 1 Adet | `Type-C USB Data Kablosu` *(Evde varsa gerek yok)* | ~0 - 50 TL |
| **TOPLAM** | **Tüm Sistem Donanımı** | — | **Sınırsız Kişiden Veri Toplayabilen Eksiksiz Sistem** | **~900 - 1030 TL ($26 - $30)** |

*(Not: AD8232 modüllerinin kutusundan çıkan 3'er adet örnek yapışkanlı ped, ilk gün masada yapacağınız ilk hızlı sinyal testleri için fazlasıyla yeterlidir; ayrıca 50'li ped paketi almanıza gerek yoktur).*

---

## 💡 Jel ve Çıtçıt Mekaniği Nasıl Çalışır?

1. **Jel Yapıştırıcı Değildir:** İletken jel krem/jöle kıvamındadır, yapışkan özelliği yoktur. Elektrotu cilde yapıştırmaz, tam tersine kayganlaştırır.
2. **Sabitlemeyi Kol Bandı Yapar:** Paslanmaz çelik çıtçıtlar elastik kol bandına perçinlenir. Kol bandını cırt cırtıyla kola sıktığınızda, metal çıtçıtlar cilde baskı yaparak mekanik olarak kilitlenir.
3. **Jelin Görevi Direnci Düşürmektir:** Çıtçıtın metal yüzeyine sürülen 1 damla jel, deri ile metal arasındaki mikroskobik hava boşluklarını doldurarak elektriksel teması kusursuzlaştırır.

---

## 🔍 2. Malzemelerin Detayları ve Satın Alma İpuçları

---

### 1. ESP32-S3 Geliştirme Kartı (1 Adet)
* **Görevi:** Sistemin ana beyni. 4 kanal kas verisini DMA ile okur, TinyML modelini çalıştırır ve Wi-Fi ile simülasyona aktarır.
* **Arama Terimi:** `ESP32-S3-DevKitC-1 N16R8` veya `ESP32-S3 N16R8 Çift Type-C`
* **Satın Alırken Dikkat Edilecekler:**
  * **N16R8 Kodu:** Kartın üzerindeki metal kapakta mutlaka **N16R8** (16 MB Flash + 8 MB PSRAM) yazdığından emin olun.
  * **WROOM-1 (Dahili Anten):** Metal kalkanın üzerinde **ESP32-S3-WROOM-1** yazmalıdır. Kartın ucunda zik-zak dalgalı PCB anteni olmalıdır.
  * ❌ *Neyi Almamalısınız:* Üzerinde **WROOM-1U** yazan veya ucunda küçük altın yuvarlak anten soketi olan modeli almayın (harici anten gerektirir).
  * **Çift Type-C:** Kartın üzerinde 2 adet Type-C soketi bulunmalıdır.

---

### 2. AD8232 Biyopotansiyel Sensör Modülü (4 Adet)
* **Görevi:** 4 farklı kas bölgesinden gelen mikrovolt seviyesindeki kas voltajını 3.3V seviyesine yükseltir.
* **Arama Terimi:** `AD8232 EKG Sensör Modülü` veya `AD8232 Heart Rate Monitor Module`
* **Satın Alırken Dikkat Edilecekler:**
  * Kırmızı renkli standart karttır.
  * İlanın içinde **3.5 mm jaklı 3'lü çıtçıt kablosunun** pakete dahil olduğundan emin olun.
  * 4 farklı kas bölgesini aynı anda okuyacağımız için bu modülden **toplam 4 adet** almanız gerekir.

---

### 3. İletken EKG / Ultrason Jeli (1 Tüp / 250 ml)
* **Görevi:** Metal çıtçıtların üzerine sürülerek cilt direncini düşürür, gürültüyü yok eder.
* **Arama Terimi:** `İletken EKG Jeli 250 ml` veya `Ultrason Jeli 250 ml`
* **Nereden Alınır?:** Medikalciler, eczaneler veya Trendyol / Hepsiburada. 250 ml'lik tek bir tüp tüm proje boyunca yüzlerce ölçüme yeter.

---

### 4. MPU-6050 6 Eksen İvme ve Jiroskop Modülü (1 Adet)
* **Görevi:** Kolu yukarı kaldırma / aşağı indirme açısını (Pitch) ve bilek dönüşünü (Roll) ölçer. Omuza kablo çekme derdini bitirir.
* **Arama Terimi:** `GY-521 MPU-6050 Modülü` veya `MPU-6050 6 Eksen Sensör`
* **Satın Alırken Dikkat Edilecekler:** Mavi renkli standart GY-521 kartıdır.

---

### 5. Paslanmaz Çelik Çıtçıt Buton Seti (1 Paket / Kuru/Jelli Elektrotlar)
* **Görevi:** Kol bandının içine çakılan ve cilde temas eden metal elektrotlarımızdır.
* **Nereden Alınır?:** Tuhafiye, kemerci, terzi malzemecisi veya Trendyol / Hepsiburada.
* **Arama Terimi:** `Paslanmaz Çelik Çıtçıt Düğme Seti 10 mm / 12 mm` veya `Metal Çıtçıt Buton`
* **Satın Alırken Dikkat Edilecekler:** Metal / paslanmaz çelik olmalıdır; plastik olanlar iletken değildir.

---

### 6. Elastik Cırt Cırtlı Kol Bandı (1 Adet)
* **Görevi:** Çıtçıtların sabitlendiği ve kola sıkıca sarılarak elektrotları kaydırmadan tutan neopren/elastik banttır.
* **Nereden Alınır?:** Eczane, medikalci, spor mağazası veya tuhafiye.
* **Arama Terimi:** `Cırt Cırtlı Elastik Bandaj` veya `Neopren Ayarlanabilir Bileklik / Kol Bandı`

---

### 7. Jumper Kablolar (1 Paket)
* **Görevi:** AD8232 ve MPU-6050 modüllerini ESP32-S3 kartına lehim yapmadan tak-çalıştır bağlamak.
* **Arama Terimi:** `40'lı Dişi-Dişi Jumper Kablo 20cm`

---

## 📏 3. Çoklu Denek (Farklı İnsanlardan) Veri Toplama Protokolü

Farklı insanların kol kalınlığı değiştiğinde elektrotların kaymasını önlemek ve veriyi standartlaştırmak için her denekte şu 3 kural uygulanacaktır:

1. **5 cm Yükseklik Kuralı:**  
   Deneğin dirsek kıvrımından aşağıya doğru mezura ile tam 5 cm ölçülür ve tenine nokta konur. Bandın üst kenarı her zaman bu 5 cm çizgisine hizalanır.
2. **1. Kanal Açısal Hizalama Kuralı:**  
   Dirseğin iç tarafındaki kemik çıkıntısı (medial epikondil) bulunur. Bandın 1. kanalı bu kemiğin 5 cm altındaki iç kas hattına denk getirilir ve bant cırt cırtıyla kola sıkıca sarılır.
3. **MVC (Maksimum Kasılma) Normalizasyonu:**  
   Farklı insanların kas gücü farklı olacağı için, kayıt başlamadan önce her deneğe 3 saniye boyunca tüm gücüyle yumruk sıktırılır. Alınan maksimum voltaj değeri kaydedilir ve o kişinin tüm verileri bu değere bölünerek 0-1 arasına normalize edilir. Böylece yapay zeka kol kalınlığına değil, hareketin şekline odaklanır!

---

## 🚫 4. Kesinlikle Satın Alınmayacaklar (İsrafı Önleme Listesi)

1. ❌ **50'lik / 100'lük Tek Kullanımlık Ped Paketleri:** ALMAYIN. (Tüp jel + çıtçıt bant ile sonsuz ölçüm yapacağız, pedler hemen biter).
2. ❌ **Harici ADC Modülü (ADS1115 vb.):** ALMAYIN. (ESP32-S3'ün kendi dahili 12-bit ADC1'i yetiyor).
3. ❌ **Op-Amp Entegreleri (TL074, INA vb.):** ALMAYIN. (Sıfırdan amfi devresi kurmuyoruz, hazır AD8232 kullanıyoruz. Eğer 1 adet AD8232 kartını EMG için modifiye etmek isterseniz gereken 1-2 adet mercimek kondansatörü (102 ve 221) okul atölyesinden temin edebilirsiniz; detaylar için [AD8232 EMG Modifikasyon Rehberi](ad8232_emg_modifikasyon_rehberi.md)'ne bakınız).
4. ❌ **Voltaj Seviye Dönüştürücü:** ALMAYIN. (Tüm modüllerimiz doğrudan 3.3V ile tam uyumludur).
