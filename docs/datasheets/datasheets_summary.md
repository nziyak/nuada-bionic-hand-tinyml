# Nuada: Bionic Hand Movement Estimation via TinyML
## Donanım Bileşenleri Datasheet ve Veri Yolu Analiz Raporu

Bu doküman, projede kullanılan/değerlendirilen mikrodenetleyici, analog ön uç (AFE), ADC, sensör ve veri yollarına ait teknik parametreleri, bus aralıklarını, SPI/I2C zamanlamalarını ve resmi datasheet referanslarını içerir.

---

## 1. Hızlı Referans ve Datasheet Arşivi

İndirilen resmi datasheet PDF'leri `docs/datasheets/` dizininde yer almaktadır:

| Bileşen | Görevi / Rolü | Protokol / Giriş | Önemli Parametreler | Yerel PDF Dosyası |
|---|---|---|---|---|
| **ESP32-S3** | Ana İşlemci & TinyML Çıkarım Ünitesi | Wi-Fi 4, BLE 5.0, 2x SPI, I2C, DMA ADC | 240 MHz Çift Çekirdek Xtensa LX7, Vektör/AI Komutları, 512 KB SRAM | [esp32-s3_datasheet_en.pdf](esp32-s3_datasheet_en.pdf) |
| **AD8232** | Biyopotansiyel Analog Ön Uç (AFE) | Analog Giriş / Diferansiyel | CMRR > 80 dB, Enstrümantasyon Kazancı x100, 2 Kutuplu Filtre | [ad8232_datasheet.pdf](ad8232_datasheet.pdf) |
| **MCP3008** | Harici 8-Kanal 10-Bit ADC (Yedek/Plan B) | SPI Arayüzü (10-bit) | 200 kSPS @ 5V, 75-100 kSPS @ 3.3V, Düşük Güç (5 µA standby) | [mcp3008_datasheet.pdf](mcp3008_datasheet.pdf) |
| **MPU-6050** | 6 Eksen Eylemsizlik Sensörü (IMU) | I2C Arayüzü (100/400 kHz) | 3-Eksen İvmeölçer + 3-Eksen Jiroskop, Dahili DMP, 16-bit ADC | [mpu6050_datasheet.pdf](mpu6050_datasheet.pdf) |
| **ADS1115** | 4-Kanal 16-Bit I2C ADC (Referans/İnceleme) | I2C Arayüzü | Maks. 860 SPS (Çok kanallı ham EMG için yetersiz, zarf için uygun) | [ads1115_datasheet.pdf](ads1115_datasheet.pdf) |

---

## 2. Danışman Hocanın Sorularına Teknik Cevaplar

### Soru 1: Sensör Aralığı (Sensor Range) Nedir?
Biyomedikal mühendisliği ve sinyal arayüzü açısından sensör aralığı 3 farklı boyutta tanımlanır:

1. **Giriş Dinamik Voltaj Aralığı (Input Dynamic Range):**
   - İnsan önkol kaslarının ürettiği cilt yüzeyi biyopotansiyel sinyali: **10 µV – 5 mV (Peak-to-Peak)**.
   - Elektrotlar bu mikrovolt seviyesindeki iyonik potansiyeli toplar.
2. **Yükseltilmiş Çıkış Dinamik Aralığı (Output Dynamic Range):**
   - Analog Ön Uç (AD8232 / Enstrümantasyon devresi), bu sinyali yaklaşık **x1100 kat** yükseltir.
   - Sinyal, $1.65\text{ V}$ sanal toprak (DC bias) üzerine bindirilerek **0.0 V – 3.3 V** aralığına ötelenir. Böylece ADC'nin tam ölçekli (Full-Scale) giriş aralığı eksiksiz kullanılır.
3. **Fiziksel Elektrot Aralığı (Inter-Electrode Distance - IED):**
   - Uluslararası **SENIAM** standardına göre iki ölçüm elektrotu arasındaki merkezden merkeze mesafe tam **20 mm** olmalıdır.
   - *20 mm'den dar olursa:* Potansiyel farkı çok küçülür, SNR düşer.
   - *20 mm'den geniş olursa:* Komşu parmak kaslarından çapraz sinyal (crosstalk) biner.
4. **Frekans Aralığı (Bandwidth):**
   - İnsan yüzeyel EMG (sEMG) enerji spektrumu: **20 Hz – 450 Hz**.
   - Analog filtre kesim frekansları: $f_{HPF} = 20\text{ Hz}$, $f_{LPF} = 450\text{ Hz}$.

---

### Soru 2: ESP32-S3'te Kaç SPI Veri Yolu Vardır?
ESP32-S3 mikrokontrolcüsünde toplam **4 adet SPI denetleyicisi** bulunmaktadır:
* **SPI0 ve SPI1:** Çipin kendi dahili SPI Flash ve harici PSRAM hafıza erişimi için ayrılmıştır (kullanıcı koduna kapalıdır).
* **SPI2 (FSPI):** Kullanıcıya açık 1. bağımsız SPI veri yoludur. DMA (Direct Memory Access) desteklidir. 80 MHz clock hızına kadar çalışabilir.
* **SPI3 (HSPI):** Kullanıcıya açık 2. bağımsız SPI veri yoludur. Bu da tamamen bağımsız ve DMA desteklidir.

> **Hocaya Net Cevap:** ESP32-S3 üzerinde harici çevre birimleri için **2 adet bağımsız kullanıcı SPI arayüzü (SPI2/FSPI ve SPI3/HSPI)** vardır. Harici ADC veya SPI ekran kullanılacaksa SPI2 (FSPI) tahsis edilir.

---

### Soru 3: Bus Aralığı / Saat Hızı ve Bant Genişliği (Bus Timings & Bandwidth)

#### A. SPI Veri Yolu (MCP3008 ADC Kullanılması Durumunda):
* **Besleme Gerilimi:** $V_{DD} = 3.3\text{ V}$
* **Maksimum SPI Saat Hızı:** MCP3008 Datasheet Bölüm 6.2 uyarınca $3.3\text{ V}$ altında maksimum clock hızı **1.35 MHz – 2.0 MHz**'dir.
* **ESP32-S3 SPI Saat Seçimi:** **1.5 MHz** ($T_{CLK} = 0.667\text{ µs}$).
* **Zamanlama Hesabı (1 Örnek Okuma):**
  - MCP3008 protokolü: 1 Start Biti + 4 Konfigürasyon Biti + 1 Boş/Sample Biti + 10 Data Biti = Toplam **17 Clock Cycle** (SPI transferinde pratik olarak 3 byte = 24 clock döngüsü kullanılır).
  - 1 kanal dönüşüm süresi: $24 \times 0.667\text{ µs} = 16\text{ µs}$.
  - 4 kanalın tamamını ardışık okuma süresi: $4 \times 16\text{ µs} = 64\text{ µs}$.
  - 2000 Hz örnekleme periyodu: $T_{sample} = 1 / 2000 = 500\text{ µs}$.
  - **SPI Bus Kullanım Oranı (Bus Utilization):** $64\text{ µs} / 500\text{ µs} = \%12.8$!
  - **Sonuç:** SPI veri yolunun $\%87.2$'si boştadır. Sıfır gecikme ve sıfır darboğaz ile çalışır.

#### B. I2C Veri Yolu (MPU-6050 IMU Kol Kaldırma Sensörü):
* **Protokol:** I2C Fast-Mode (**400 kHz** saat hızı).
* **Veri Paketi:** 3 eksen ivme + 1 sıcaklık + 3 eksen jiroskop = Toplam 14 byte veri ($14 \times 9\text{ bit} \approx 126\text{ saat döngüsü} \approx 0.315\text{ ms}$).
* **IMU Örnekleme Hızı:** 100 Hz ($T = 10\text{ ms}$).
* **I2C Bus Kullanım Oranı:** $0.315\text{ ms} / 10\text{ ms} = \%3.15$!
* **Sonuç:** I2C veri yolu son derece rahat çalışır.

---

### Soru 4: "ADC'ye Gerek Kalmayabilir, ESP32'ninki Yeter Belki" (Stratejik Analiz)

Danışman hocanızın bu yorumu hem maliyeti düşüren hem de donanımı sadeleştiren **çok doğru ve vizyoner bir yaklaşımdır**.

#### ESP32-S3 Dahili ADC'sinin Güçlü Yönleri (Neden Yeterli Olabilir?):
1. **Continuous ADC Driver (DMA Modu):**  
   ESP32-S3'te I2S/DMA tabanlı kesintisiz analog örnekleme motoru bulunur. Bu modda CPU'ya hiç yük bindirmeden, 4 analog pini (GPIO 1, 2, 3, 4) saniyede kanal başı 2 kHz (hatta 20 kHz) hızla DMA arabelleğine akıtabilir.
2. **Wi-Fi Çakışma Sorunu Çözüldü:**  
   Eski ESP32'de Wi-Fi açılınca ADC2 kilitleniyordu. ESP32-S3'te ise sadece ADC1 pinleri kullanıldığında (GPIO 1 - 10) Wi-Fi açıkken analog okuma sorunsuz devam eder.
3. **eFuse Fabrika Kalibrasyonu:**  
   ESP32-S3 yongalarında üretim aşamasında kalibre edilmiş voltaj referans eğrileri yer alır (`esp_adc_cal` / `adc_cali_curve_fitting`). Doğrusallık hatası yazılımsal olarak telafi edilir.
4. **Maliyet ve Boyut:**  
   Harici ADC çipini ve SPI kablolamasını tamamen ortadan kaldırır. Giyilebilir kol bandının boyutunu küçültür.

#### Tek Olası Risk ve Alınacak Önlem:
* Wi-Fi RF sinyal vericisi veri paketi gönderirken $3.3\text{ V}$ hattında mikro-dalgalanmalar (RF ripple) oluşturabilir.
* **Donanımsal Önlem:** Analog giriş pinlerine $100\text{ nF}$ seramik dekuplaj kondansatörü ve $1\text{ k}\Omega$ RC alçak geçiren filtre eklenir.

#### Jüriye / Hocaya Sunulacak Mühendislik Kararı:
* **PLAN A (Öncelikli & Hocanın Önerisi):** ESP32-S3 Dahili ADC1 + DMA Continuous Mode. Sıfır ekstra maliyet, kompakt giyilebilir tasarım.
* **PLAN B (Yedek / Sigorta):** SPI2 portu üzerinden MCP3008 harici ADC. (Eğer Wi-Fi RF gürültüsü yüksek çıkarsa tak-çalıştır yedek hat).
