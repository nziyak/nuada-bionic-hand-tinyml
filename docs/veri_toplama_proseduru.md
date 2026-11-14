# Nuada - Canlı EMG Veri Toplama, Donanım Kurulumu ve Kayıt Prosedürü
## A'dan Z'ye Eksiksiz Uygulama ve Sorun Giderme Rehberi

Bu belge; **Nuada Bionic Hand** projesinde modifiye edilmiş/orijinal AD8232 analog ön uç kartı ve ESP32-S3 mikrodenetleyicisi ile **canlı kas sinyali (sEMG) okuma, terminalde görselleştirme ve CSV olarak kaydetme** süreçlerinin tüm adımlarını (yazılım altyapısı, arka planda yapılan sistem konfigürasyonları ve biyomekanik elektrot yerleşimi dahil) içerir.

---

## 1. Arka Planda Yapılan ve Bilinmesi Gereken Sistem Ayarları

ESP32-S3 ve Python betiklerinin sorunsuz çalışması için arka planda yapılandırılan ve ileride sıfırdan bir bilgisayara geçildiğinde bilinmesi gereken kritik adımlar şunlardır:

### A. ESP32-S3 Çift Type-C ve "USB CDC on Boot" Ayarı
ESP32-S3 kartlarında 2 adet Type-C portu bulunur: Biri dahili USB-to-UART çipine (CH340/CP2102), diğeri ise doğrudan ESP32-S3 işlemcisinin içine (Native USB OTG) bağlıdır.
* Kartın `Serial.print` komutlarının bilgisayara sorunsuz akabilmesi için `platformio.ini` dosyasına şu derleme bayrakları eklenmiştir:
  ```ini
  build_flags = 
      -D ARDUINO_USB_MODE=1
      -D ARDUINO_USB_CDC_ON_BOOT=1
  ```
* Bu ayar olmadan kod yüklense bile terminalde hiçbir veri görünmez.

### B. Linux USB Seri Port Yetkisi (Dialout Grubu)
Linux işletim sistemlerinde `/dev/ttyACM0` veya `/dev/ttyUSB0` portlarına root olmadan erişebilmek için kullanıcının `dialout` grubunda olması gerekir. Eğer "Permission Denied" hatası alırsanız tek seferlik şu komut çalıştırılır:
```bash
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyACM* /dev/ttyUSB*
```
*(Bu işlemden sonra bir kez oturumu kapatıp açmak gerekir).*

### C. Python Kütüphaneleri
Kayıt betiği (`record_live_emg.py`) seri porttan veri okumak için `pyserial` kütüphanesini kullanır:
```bash
pip install pyserial
```

### D. PlatformIO Derleyici Yolu
Sisteminizde PlatformIO sanal ortamda kuruludur:
* Tam yol: `/home/zia/.platformio/penv/bin/pio`
* Terminalde doğrudan `pio` yazabilmek için `~/.bashrc` dosyanıza şu alias eklenebilir:
  ```bash
  echo 'alias pio="/home/zia/.platformio/penv/bin/pio"' >> ~/.bashrc
  source ~/.bashrc
  ```

---

## 2. Donanım ve Devre Bağlantı Şeması (Wiring)

AD8232 ile ESP32-S3 kartını breadboard üzerinde jumper kablolarla bağlayınız:

| AD8232 Pini | ESP32-S3 Pini | Sinyal Tipi | Açıklama |
| :--- | :--- | :--- | :--- |
| **`3.3V`** | **`3V3`** | Güç | Regüle 3.3 Volt Besleme Hattı |
| **`GND`** | **`GND`** | Toprak | Ortak Düşük Gürültülü Toprak Hattı |
| **`OUTPUT` (OUT)** | **`GPIO 1`** | Analog Giriş | ADC1_CH0 (0.0 V - 3.3 V Analog Çıkış) |
| **`LO+`** | *Boşta (NC)* | Dijital | Leads-Off Algılama (Kullanılmıyor) |
| **`LO-`** | *Boşta (NC)* | Dijital | Leads-Off Algılama (Kullanılmıyor) |
| **`SDN`** | *Boşta (NC)* | Dijital | Shutdown Kapatma (Dahili Pull-up devrede) |

> [!IMPORTANT]
> **Neden GPIO 1 (ADC1_CH0)?:**  
> ESP32 serisinde ADC2 birimi Wi-Fi sürücüsüyle donanımsal olarak ortak paylaşılır; Wi-Fi açıkken ADC2 okumaları kilitlenir veya saçmalar. Bu yüzden projemizde tüm sEMG kanalları RF girişiminden bağımsız çalışan **ADC1 (GPIO 1-4)** pinlerine ayrılmıştır.

---

## 3. Elektrotların Hazırlanması ve Kola Takılması (SENIAM Standardı)

Kablonun ucunda 3 adet çıtçıt konnektör bulunur: **Kırmızı (RA)**, **Sarı (LA)**, **Yeşil (RL)**.

### A. Ped ve Jel Hazırlığı
1. 3 adet elektrot pedinin çıtçıtlarını kablonun metal başlıklarına takınız.
2. Pedlerin arkasındaki şeffaf koruyucu naylonu soyup çıkarınız.
3. Pedlerin ortasında bulunan yuvarlak iletken sensör alanına (gri/siyah daire) **küçük bir mercimek tanesi kadar iletken ultrason jeli** sıkınız ve parmağınızla hafifçe daire içine yayınız (dış beyaz yapışkan alana taşırmayınız).

### B. Anatomik Yerleşim (FDS Kası - Parmak Bükme / Yumruk)
1. **Cilt Temizliği:** Ön kolun iç yüzeyini alkollü mendil veya kolonya ile silip kurulayınız (cilt yağını ve empedansı düşürür).
2. **Kırmızı Elektrot (RA - Pozitif Giriş):** 
   * Dirsek kıvrımından aşağıya doğru yaklaşık **5 cm** ininiz.
   * Kolunuzun iç tarafında yumruk sıkınca şişen kasın (**Flexor Digitorum Superficialis - FDS**) tam üzerine yapıştırınız.
3. **Sarı Elektrot (LA - Negatif Giriş):** 
   * Kırmızı elektrodun **2 cm (20 mm - SENIAM standardı) hemen altına**, kas liflerinin doğrultusuna paralel olacak şekilde yapıştırınız.
4. **Yeşil Elektrot (RL - Referans / Toprak):** 
   * **Dirseğinizin arkasındaki sivri kemik çıkıntısına (Olecranon)** yapıştırınız.
   * *Görevi:* Vücudunuzun havadaki 50 Hz şebeke gürültüsünü toprağa aktarmak ve amfinin sanal zeminini sabitlemektir. Yeşil elektrot takılmazsa sinyal tavana yapışır.
5. Kablonun 3.5 mm jakını AD8232 kartındaki siyah jaka takınız.

---

## 4. Firmware'i ESP32-S3'e Yükleme (Flash) Adımları

Yazılım projesi `nuada-bionic-hand-tinyml/firmware/esp32s3_ad8232_test` klasöründedir.

1. ESP32-S3'ü USB veri kablosu ile bilgisayara bağlayınız.
2. Terminali açıp şu tek satırlık komutu çalıştırınız:
   ```bash
   /home/zia/.platformio/penv/bin/pio run -d /home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/firmware/esp32s3_ad8232_test -t upload
   ```
3. **Beklenen Çıktı:** Kod derlenir, serial port otomatik bulunur ve ekranın sonunda `[SUCCESS]` yazar.
4. ESP32 üzerindeki dahili RGB LED başlangıçta **Mavi**, hazır olduğunda **Yeşil** yanacaktır.

---

## 5. Canlı Veri Okuma, Terminalde İzleme ve CSV Kaydetme

Canlı veriyi terminalde renkli bar grafiğiyle izlemek ve eşzamanlı olarak diskteki bir CSV dosyasına kaydetmek için hazırlanan betik kullanılır:

1. Terminalde şu komutu çalıştırınız:
   ```bash
   python3 /home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/scripts/record_live_emg.py
   ```
2. **Ekranda Ne Görünür?**
   * **Kol Dinlenmedeyken:**
     ```text
     Ham ADC: 2048 | Sapma: 6 [                         ]      ( Gevsek / Dinlenme )
     ```
     *(ESP32 üzerindeki dahili LED Yeşil yanar).*
   * **Yumruk Sıkıldığında:**
     ```text
     Ham ADC: 3590 | Sapma: 1542 [=========================]  >>> [ SIKILDI / KASILMA ] <<<
     ```
     *(ESP32 üzerindeki dahili LED Kırmızı yanar).*
   * **Yumruk Bırakıldığında:**
     Modifiye edilmiş kartta sinyal **<20 milisaniyede** anında yeşil `Gevsek` durumuna geri döner (eski modifiyesiz karttaki 1.5 saniyelik takılma yaşanmaz).

3. **Kaydı Tamamlama:**
   * Testi bitirmek istediğinizde klavyeden **`Ctrl + C`** tuşlarına basınız.
   * Betik otomatik olarak toplanan tüm verileri zaman damgalı olarak şu konuma kaydeder:
     `nuada-bionic-hand-tinyml/data/emg_record_YYYYMMDD_HHMMSS.csv`

---

## 6. CSV Veri Dosyası Formatı

Oluşturulan CSV dosyası Python, Pandas veya MATLAB ile model eğitiminde doğrudan kullanılabilir:

```csv
timestamp_iso,elapsed_sec,raw_adc,deviation,status
2026-11-01T12:00:01.123456,0.060,2048,0,"( Gevsek / Dinlenme )"
2026-11-01T12:00:01.183456,0.120,2051,3,"( Gevsek / Dinlenme )"
2026-11-01T12:00:02.450123,1.387,3580,1532,">>> [ SIKILDI / KASILMA ] <<<"
```
* `timestamp_iso`: ISO 8601 standart zaman damgası.
* `elapsed_sec`: Test başlangıcından itibaren geçen süre (saniye cinsinden float).
* `raw_adc`: ESP32 12-bit ADC değeri (0 - 4095 arası, merkez ~2048).
* `deviation`: 2048 bazal çizgisinden anlık sapma mutlak değeri (`|raw_adc - 2048|`).
* `status`: Kasılma veya Dinlenme etiket bilgisi.

---

## 7. Olası Hatalar ve Hızlı Çözüm Tablosu (Troubleshooting)

| Belirti / Hata | Olası Neden | Çözüm |
| :--- | :--- | :--- |
| **`[HATA] Bağlı bir ESP32 bulunamadı`** | 1. Kablo sadece şarj kablosudur (data hattı yoktur).<br>2. ESP32 diğer Type-C portuna takılıdır. | 1. Veri aktaran bir Type-C kablosu kullanınız.<br>2. Kart üzerindeki diğer Type-C portunu deneyiniz.<br>3. `ls /dev/ttyACM* /dev/ttyUSB*` ile portu kontrol ediniz. |
| **`Permission denied: '/dev/ttyACM0'`** | Linux kullanıcı izinleri eksiktir. | Terminalde `sudo chmod 666 /dev/ttyACM0` çalıştırınız veya `sudo usermod -a -G dialout $USER` yapıp oturumu yenileyiniz. |
| **Ham ADC değeri sürekli 4095 veya 0** | 1. Yeşil referans elektrodu dirseğe temas etmiyordur.<br>2. OUTPUT pini GPIO 1 yerine yanlış pine takılmıştır. | 1. Yeşil elektrodun dirsek arkasına jel ile iyi yapıştığından emin olunuz.<br>3. Jumper kabloyu ESP32 üzerindeki `GPIO 1` pinine taktığınızı doğrulayınız. |
| **Sinyal yumruk sıkınca hiç oynamıyor** | Kırmızı ve Sarı elektrotlar kasın üzerine denk gelmemiştir. | Yumruk sıkınca kolun iç kısmında kabaran kas göbeğini parmağınızla bulup elektrotları oraya taşıyınız. |
| **Upload sırasında `Failed to connect`** | ESP32 otomatik boot moduna geçememiştir. | Yükleme başlarken kart üzerindeki **BOOT** butonuna basılı tutunuz, yükleme başlayınca bırakınız. |
