# Nuada - Çoklu Denek ve Çoklu Açı (0°, 45°, 90°) Canlı Veri Toplama Kılavuzu

Bu belge; birden fazla denekten **4 kanal analog sEMG** ve **MPU-6050 (6 eksen IMU)** verilerini; biyomekanik kol açısı değişimlerini (**0°, 45° ve 90°**) kapsayacak, etiketleme gürültüsünü sıfırlayacak ve makine öğrenimi modellerinde aşırı öğrenmeyi (overfitting) önleyecek şekilde toplamak için hazırlanmış operasyonel rehberdir.

---

## 1. Donanım ve Devre Bağlantı Tablosu

Sistem harici simetrik güç kaynağından (UNI-T) ve ESP32-S3'ün dahili hatlarından beslenir.

### A. Besleme Dağıtımı (UNI-T Güç Kaynağı → Breadboard)
1. UNI-T CH1 ve CH2 bağımsız modda **5.00 V / 0.200 A** olarak ayarlanır.
2. **CH1 Siyah (-)** ile **CH2 Kırmızı (+)** birbirine bağlanarak ortak **GND (0V)** yapılır.
3. Breadboard üzerine 3 besleme hattı çekilir:
   * **+5V Hattı (+Vs):** CH1 Kırmızı (+)
   * **GND Hattı (0V):** Ortak GND köprüsü
   * **-5V Hattı (-Vs):** CH2 Siyah (-)
4. **KRİTİK ADIM (Ortak Toprak):** ESP32-S3'ün bir **GND** pini breadboard'un mavi **GND (0V)** rayına bağlanır.

### B. Pin Bağlantı Şeması

| Modül / Sensör | Modül Pini | Bağlanacağı Yer | Fonksiyon / Protokol |
| :--- | :--- | :--- | :--- |
| **EMG CH1** (FDS - Parmak Bükücü) | `+Vs`, `GND`, `-Vs` | Breadboard +5V, GND, -5V | Güç Beslemesi |
| **EMG CH1** | `SIG` | **ESP32 GPIO 1** | ADC1_CH0 (0.0 V - 3.3 V Ham Analog) |
| **EMG CH2** (FPL - Başparmak Bükücü) | `+Vs`, `GND`, `-Vs` | Breadboard +5V, GND, -5V | Güç Beslemesi |
| **EMG CH2** | `SIG` | **ESP32 GPIO 2** | ADC1_CH1 (0.0 V - 3.3 V Ham Analog) |
| **EMG CH3** (ED - Parmak Açıcı) | `+Vs`, `GND`, `-Vs` | Breadboard +5V, GND, -5V | Güç Beslemesi |
| **EMG CH3** | `SIG` | **ESP32 GPIO 3** | ADC1_CH2 (0.0 V - 3.3 V Ham Analog) |
| **EMG CH4** (FCU / EI - Bilek/İşaret) | `+Vs`, `GND`, `-Vs` | Breadboard +5V, GND, -5V | Güç Beslemesi |
| **EMG CH4** | `SIG` | **ESP32 GPIO 4** | ADC1_CH3 (0.0 V - 3.3 V Ham Analog) |
| **MPU-6050** | `VCC` | **ESP32 3V3** | 3.3V Regüle Güç |
| **MPU-6050** | `GND` | **ESP32 GND** | Ortak Toprak |
| **MPU-6050** | `SDA` | **ESP32 GPIO 8** | I2C Data (400 kHz Fast-Mode) |
| **MPU-6050** | `SCL` | **ESP32 GPIO 9** | I2C Clock (400 kHz Fast-Mode) |

### C. Referans Elektrot Ortaklama Kuralı
* Sensör kartlarının 3.5 mm jakındaki referans hattı (Sleeve), kartın GND pinine doğrudan bağlıdır.
* 4 kartın GND pinleri breadboard üzerinde birleştiği için referanslar elektriksel olarak zaten ortaktır.
* **Uygulama:** Kola yalnızca **1 adet referans elektrodu** (Ulna kemiği üzerine) yapıştırılır ve buna **sadece 1. sensörün yeşil/siyah kablosu** takılır. Kalan 3 sensörün referans kabloları boşta bırakılır (bantlanır).
* Böylece toplam elektrot sayısı 12 yerine **9 adettir** (8 aktif sinyal + 1 ortak referans).

---

## 2. Firmware ve ESP32-S3 Ham (Raw) Veri Akışı

Yazılım [main.cpp](file:///home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/firmware/esp32s3_ad8232_test/main.cpp) dosyasındadır.

### A. ESP32 Ham (Raw) Veri Prensibi
* ESP32 kesinlikle dijital filtreleme, yumuşatma, DC offset çıkarma veya normalizasyon **yapmaz**.
* 100 Hz frekansta (her 10 ms'de bir) saf ham veriyi basar:
  `DATA,time_ms,emg1_raw,emg2_raw,emg3_raw,emg4_raw,ax,ay,az,gx,gy,gz`
  * `emg1-4`: 0 ile 4095 arası saf 12-bit ADC tamsayısı.
  * `ax-gz`: -32768 ile +32767 arası saf 16-bit IMU tamsayısı.

### B. Tek Satırlık Flash Komutu
ESP32'yi Type-C ile bilgisayara bağlayıp terminalde çalıştırın:
```bash
/home/zia/.platformio/penv/bin/pio run -d /home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/firmware/esp32s3_ad8232_test -t upload
```
* **Doğrulama:** Yükleme bittiğinde terminalde `[SUCCESS]` yazar; ESP32 RGB LED'i MPU6050 başarıyla algılandığında **Yeşil**, algılanmazsa **Sarı** yanar.

---

## 3. Kol Açıları (0°, 45°, 90°) ve Biyomekanik Gereklilik

Biyonik el kontrolünde en büyük zorluk **"Limb Position Effect" (Uzuv Pozisyonu Etkisi)** problemidir:
1. Kol açısı değiştikçe deri altındaki kas göbekleri elektrotların altına göre hafifçe kayar.
2. Kolun yerçekimine karşı duruşu, kasların bazal tonusunu ve kasılma şiddetini değiştirir.
3. MPU-6050 yerçekimi vektörünü (1.0 g) farklı eksenlerde okur.

Bu nedenle **her hareket istisnasız 3 farklı kol açısında** kaydedilmelidir:

```
               [ 90° Dikey Pozisyon ]
               (Dirsekten dik yukarı)
                         ▲
                        /
                       /  [ 45° Yarı Eğik Pozisyon ]
                      /  (Öne/yukarı 45 derece eğimli)
                     /
  ═══════════════════►  [ 0° Yatay Pozisyon ]
  (Ön kol masada yatay / yere paralel)
```

* **0° (Yatay Pozisyon):** Ön kol masada yatay, yere paralel uzatılmış. Yerçekimi vektörü çoğunlukla `az` eksenine biner.
* **45° (Yarı Eğik Pozisyon):** Ön kol dirsekten 45 derece yukarı eğimli tutulur. Yerçekimi `ay` ve `az` arasında paylaşılır (~0.7 g, ~0.7 g).
* **90° (Dikey Pozisyon):** Ön kol dirsekten 90 derece bükülü, el tavana doğru dik tutulur. Yerçekimi vektörü `ay` veya `ax` eksenine dik biner.

---

## 4. Hareket Sınıfları, Süreler ve Overfitting Önleme

### A. 5 Temel Hareket
1. **`rest` (Dinlenme):** El ve parmaklar tamamen gevşek, sıfır gerilim.
2. **`fist` (Yumruk):** Tüm parmaklar kuvvetlice sıkılı (FDS kası).
3. **`open_hand` (El Açma):** Tüm parmaklar sonuna kadar gergin açık (ED kası).
4. **`pinch` (Kıstırma):** Başparmak ve işaret parmağı uçları birbirine bastırılır (FPL + FDS).
5. **`point` (İşaret Etme):** İşaret parmağı ileri uzatılmış, diğerleri bükülü (EI kası).

### B. Süreler ve Dinlenme Aralığı
* **3 Saniye Kasılma / Sabit Tutuş:** Hareket yapılıp 3 saniye boyunca sabit gerilimde tutulur.
* **3 Saniye Dinlenme (Rest):** İki hareket arasında denek elini tamamen serbest bırakır. Kas yorgunluğunu (fatigue) önler.

### C. Sıralama Neden Rastgele (Shuffled) Olmalıdır?
* Her denek hareketleri aynı sırayla (örneğin hep Rest -> Fist -> Pinch -> Point) yaparsa:
  * Kas yorgunluğu hep son hareketlerde birikir (genlik düşer). Model parmak hareketini değil, yorgunluk profilini öğrenir.
  * Model önceki hareketin kas gevşeme kalıntısını sonraki hareketin karakteristiği sanabilir.
* **Çözüm:** Rest hareketi temel referans olarak başta alınır; diğer aktif hareketlerin sırası her açıda ve her turda **bilgisayar tarafından rastgele karıştırılır**.

### D. Neden Tek Parça Kayıt Değil, Ayrı CSV Dosyaları?
* Uzun tek kayıt alıp sonradan elle parçalamak hem çok zaman alır hem de geçiş anlarında saniyenin onda biri kadar bile olsa etiket kaymasına (label noise) neden olur.
* Otomasyon scriptimiz her hareketi **3 saniyelik temiz, etiketli CSV'ler** halinde doğrudan ilgili klasöre kaydeder:
  ```
  data/
    ├── s01/
    │    ├── rest/
    │    │    ├── rest_deg0_trial1_20261113.csv
    │    │    ├── rest_deg45_trial1_20261113.csv
    │    │    └── rest_deg90_trial1_20261113.csv
    │    ├── fist/
    │    │    ├── fist_deg0_trial1_20261113.csv
    │    │    ├── fist_deg45_trial1_20261113.csv
    │    │    └── fist_deg90_trial1_20261113.csv
    │    ├── open_hand/
    │    ├── pinch/
    │    └── point/
    └── s02/
  ```

---

## 5. Çoklu Denek Veri Toplama Hızlı Checklist

- [ ] **1. Cilt Temizliği:** Deneğin ön kolunu alkollü mendille silip kurutun.
- [ ] **2. Ped & Jel:** 9 elektrot pedinin ortasına birer mercimek tanesi jel sürün (8 tanesi kas göbeklerine, 1 tanesi dirsek/ulna kemiğine ortak referans).
- [ ] **3. Canlı Sinyal Testi (15 sn):**
  ```bash
  python3 nuada-bionic-hand-tinyml/scripts/record_live_emg.py
  ```
  Deneğe yumruk sıktırıp barların oynadığını teyit edin (`Ctrl + C` ile kapatın).
- [ ] **4. Rehberli Oturumu Başlatın:**
  ```bash
  python3 nuada-bionic-hand-tinyml/scripts/record_live_emg.py --guided --subject s01
  ```
  * Script sırasıyla **0°, 45° ve 90°** bloklarını açar.
  * Her açı öncesi deneğin kolunu ayarlamanız için bekler (`Enter`'a basınca başlar).
  * 3 sn geri sayım verir (3.. 2.. 1..), hareketi 3 sn kaydeder, 3 sn dinlendirir.
  * Sıralamalar overfit'e karşı otomatik karıştırılır.
  * Tüm verileri `data/s01/<hareket>/` klasörlerine ham (raw) CSV olarak kaydeder.
- [ ] **5. Tamamlama:** Pedleri sökün, deneğin kolunu temizleyin. Klasördeki 30 dosyayı doğrulayın (3 açı x 2 tekrar x 5 hareket).

---

## 6. Manuel / Tekli Kayıt Komutları (İhtiyaç Halinde)

```bash
# Örnek: s01 deneği, fist hareketi, 0 derece açı, 3 saniye süre, trial 1
python3 nuada-bionic-hand-tinyml/scripts/record_live_emg.py -s s01 -g fist -a 0 -t 1 -d 3.0

# Örnek: s01 deneği, fist hareketi, 45 derece açı, 3 saniye süre, trial 1
python3 nuada-bionic-hand-tinyml/scripts/record_live_emg.py -s s01 -g fist -a 45 -t 1 -d 3.0

# Örnek: s01 deneği, fist hareketi, 90 derece açı, 3 saniye süre, trial 1
python3 nuada-bionic-hand-tinyml/scripts/record_live_emg.py -s s01 -g fist -a 90 -t 1 -d 3.0
```

---

## 7. CSV Dosya Formatı (100% Ham Veri)

Oluşturulan CSV dosyalarının her satırı mikrodenetleyiciden gelen saf veridir:

```csv
timestamp_iso,elapsed_sec,esp_time_ms,emg1_raw,emg2_raw,emg3_raw,emg4_raw,emg1_v,emg2_v,emg3_v,emg4_v,ax_raw,ay_raw,az_raw,gx_raw,gy_raw,gz_raw,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,gesture_label,angle_deg,posture,subject,trial
```

* `emg1_raw - emg4_raw`: 12-bit ADC ham değerleri (0 - 4095).
* `ax_raw - gz_raw`: 16-bit IMU ham değerleri (-32768 - +32767).
* `angle_deg`: Kol açısı (0, 45 veya 90).
* `emg_v` ve `g/dps`: Kontrol ve görselleştirme için çevrilmiş referans sütunlarıdır; model eğitiminde ham (`_raw`) sütunlar doğrudan kullanılır.
