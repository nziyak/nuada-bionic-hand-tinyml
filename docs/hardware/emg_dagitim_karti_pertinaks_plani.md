# Nuada - 4 Kanal sEMG & Güç Dağıtım Hub'ı
## Delikli Pertinaks (Perfboard) Yerleşim ve Lehimleme Kılavuzu

Bu belge; breadboard üzerindeki jumper kablo karmaşasını, temassızlıkları ve sinyal parazitlerini ortadan kaldırmak amacıyla tasarlanan **4 Kanal sEMG & Güç Dağıtım Hub'ı**nın delikli pertinaks üzerindeki bileşen yerleşimini, lehim yollarını ve kablo bağlantılarını içerir.

---

## 1. Malzeme Listesi (BOM)

| Parça | Adet | Açıklama |
| :--- | :--- | :--- |
| **Delikli Pertinaks / Plaket** | 1 | Standart delikli tek yüzey pertinaks (~5 cm x 5 cm veya daha küçük) |
| **4'lü Dişi Pin Header (2.54 mm)** | 4 | Sensör modüllerinden gelen kablolar için (CH1, CH2, CH3, CH4) |
| **3'lü Vidalı Klemens (veya Erkek Header)** | 1 | Güç besleme girişi (`+Vs`, `GND`, `-Vs`) |
| **5'li Erkek Pin Header (2.54 mm)** | 1 | ESP32'ye giden sinyal ve toprak çıkışı (`GND`, `CH1`, `CH2`, `CH3`, `CH4`) |
| **Montaj Teli / Zil Teli** | ~30 cm | Kartın arkasındaki bağlantı yolları için |
| *(İsteğe Bağlı)* **100 nF Seramik Kondansatör** | 2 | Besleme gürültü filtreleme (`+Vs - GND` ve `-Vs - GND` arasına) |
| **10 kΩ Direnç** | 4 | ESP giriş koruması – gerilim bölücünün üst direnci (her kanala 1 adet, bkz. Bölüm 5) |
| **20 kΩ Direnç** | 4 | ESP giriş koruması – gerilim bölücünün alt direnci (her kanala 1 adet, bkz. Bölüm 5) |
| *(Alternatif)* **BAT54S Schottky Diyot + 2.2 kΩ Direnç** | 4 + 4 | Bölücü yerine kırpıcı koruma (negatif gerilime karşı da korur, bkz. Bölüm 5) |

> **Not:** Proje, AD8232 kartlarının modifikasyonu yerine **hazır sEMG sensör modülleriyle** devam etmektedir. Bu hub, çift (±Vs) beslemeli hazır sensörler için tasarlanmıştır. AD8232 kartları **tek 3.3V** ile beslenir ve bu hub'a **takılmamalıdır** (5V, AD8232'nin 3.6V mutlak üst sınırını aşar).

---

## 2. Üst Yüzey Bileşen Yerleşim Planı (Component Side)

Soketler kartın delikli pertinaks yüzeyine aşağıdaki düzende yerleştirilir:

```
┌────────────────────────────────────────────────────────────────────────┐
│              4 KANAL sEMG DAĞITIM HUB'I (ÜSTTEN GÖRÜNÜM)               │
│                                                                        │
│   [ GÜÇ GİRİŞİ ]                          [ ESP32 BAĞLANTI SOKETİ ]    │
│   (3'lü Vidalı Klemens)                   (5'li Erkek Header)          │
│     ┌───┬───┬───┐                           ┌───┬───┬───┬───┬───┐      │
│     │+Vs│GND│-Vs│                           │GND│CH1│CH2│CH3│CH4│      │
│     └───┴───┴───┘                           └───┴───┴───┴───┴───┘      │
│       1   2   3                               1   2   3   4   5        │
│                                                                        │
│   ──────────────────────────────────────────────────────────────────   │
│                                                                        │
│   [ SENSÖR 1 ]       [ SENSÖR 2 ]       [ SENSÖR 3 ]       [ SENSÖR 4 ]│
│   (4'lü Dişi)        (4'lü Dişi)        (4'lü Dişi)        (4'lü Dişi) │
│   ┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐│
│ 1 │ +Vs      │     1 │ +Vs      │     1 │ +Vs      │     1 │ +Vs      ││
│ 2 │ GND      │     2 │ GND      │     2 │ GND      │     2 │ GND      ││
│ 3 │ -Vs      │     3 │ -Vs      │     3 │ -Vs      │     3 │ -Vs      ││
│ 4 │ SIG      │     4 │ SIG      │     4 │ SIG      │     4 │ SIG      ││
│   └──────────┘       └──────────┘       └──────────┘       └──────────┘│
│       (FDS)              (FPL)              (ED)             (FCU/EI)  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Alt Yüzey Lehimleme ve Hat Bağlantı Şeması (Wiring Side)

Kartın arkasında toplamda yalnızca **4 ana hat** çekilecektir. *(Sinyal hatlarına eklenecek koruma dirençleri/diyotları için Bölüm 5'e bakınız.)*

```
PİL/GÜÇ GİRİŞİ                ORTAK RAYLAR                     SENSÖR SOKETLERİ
══════════════                ════════════                     ════════════════

(+Vs Klemensi) ──[Tel 1]──┬───► Sensör 1 (+Vs - Pin 1)
                          ├───► Sensör 2 (+Vs - Pin 1)
                          ├───► Sensör 3 (+Vs - Pin 1)
                          └───► Sensör 4 (+Vs - Pin 1)

(GND Klemensi) ──[Tel 2]──┬───► ESP32 Soketi (GND - Pin 1)
                          ├───► Sensör 1 (GND - Pin 2)
                          ├───► Sensör 2 (GND - Pin 2)
                          ├───► Sensör 3 (GND - Pin 2)
                          └───► Sensör 4 (GND - Pin 2)

(-Vs Klemensi) ──[Tel 3]──┬───► Sensör 1 (-Vs - Pin 3)
                          ├───► Sensör 2 (-Vs - Pin 3)
                          ├───► Sensör 3 (-Vs - Pin 3)
                          └───► Sensör 4 (-Vs - Pin 3)


SİNYAL ÇIKIŞLARI              DORUDAN HATLAR                   ESP32 SOKETİ
════════════════              ══════════════                   ════════════
Sensör 1 (SIG - Pin 4) ──────────[Tel 4A]────────────────────► ESP32 (CH1 - Pin 2)
Sensör 2 (SIG - Pin 4) ──────────[Tel 4B]────────────────────► ESP32 (CH2 - Pin 3)
Sensör 3 (SIG - Pin 4) ──────────[Tel 4C]────────────────────► ESP32 (CH3 - Pin 4)
Sensör 4 (SIG - Pin 4) ──────────[Tel 4D]────────────────────► ESP32 (CH4 - Pin 5)
```

---

## 4. Güç Kaynağı ve Pil Bağlantı Modları

Hazırlanan 3'lü klemens hem masaüstü güç kaynağıyla hem de taşınabilir pillerle **aynı şekilde** kullanılır:

### Mod A: Çift Çıkışlı Masaüstü DC Güç Kaynağı (UNI-T)
1. Güç kaynağında CH1 ve CH2 bağımsız modda **5.00 V** ayarlanır.
2. **CH1 Siyah (-)** ile **CH2 Kırmızı (+)** birbirine bağlanır (Ortak 0V köprüsü).
3. Klemens bağlantısı:
   * **`+Vs` Klemensi:** CH1 Kırmızı (+) ucuna bağlanır (+5.0 V).
   * **`GND` Klemensi:** Ortak 0V köprüsüne bağlanır (0 V).
   * **`-Vs` Klemensi:** CH2 Siyah (-) ucuna bağlanır (-5.0 V).

> **Neden ±3.3V değil?** Çift beslemeli EMG modüllerinin içindeki op-amp'ler (genellikle TL072/TL084) ve enstrümantasyon katı tipik olarak en az **±3.5V** ister. ±3.3V'ta sinyal kırpılır, kazanç düşer veya kart hiç çalışmaz. **±5V önerilen değerdir.** Sensörün kendi veri sayfasındaki minimum besleme değerini mutlaka teyit edin.

### Mod B: 2 Adet 3.7 V Li-ion / LiPo Pil
1. **Pil 1'in (-)** kutbu ile **Pil 2'nin (+)** kutbu birbirine bağlanır (Ortak 0V köprüsü).
2. Klemens bağlantısı:
   * **`+Vs` Klemensi:** Pil 1'in (+) kutbuna bağlanır (+3.7 V / 4.2 V).
   * **`GND` Klemensi:** İki pilin birleştiği orta noktaya bağlanır (0 V).
   * **`-Vs` Klemensi:** Pil 2'nin (-) kutbuna bağlanır (-3.7 V / -4.2 V).

---

## 5. ESP32-S3 Giriş Koruması (Zorunlu)

Besleme hattı (`+Vs` / `-Vs`) ESP32-S3'e **hiçbir zaman** bağlanmaz; ESP'ye yalnızca `GND` ve `CH1–CH4` sinyalleri gider. Ancak sensörler ±5V ile beslendiğinde **SIG çıkışı 3.3V'un üzerine çıkabilir** (özellikle güçlü kasılmada ve kazanç potu yüksekken). ESP32-S3 GPIO pinlerinin mutlak sınırları:

* **Üst sınır:** ~3.6V (VDD + 0.3V) — aşılırsa ADC pini veya çip hasar görür.
* **Alt sınır:** -0.3V — negatif gerilim de pine zarar verir.
* **Kullanışlı ADC aralığı (11 dB zayıflatma):** ~0 – 3.1V.

Bu nedenle her kanalda aşağıdaki iki korumadan **biri** uygulanır:

### Seçenek A: Gerilim Bölücü (Önerilen, en basit)
```
Sensör SIG ──[10 kΩ]──┬──► ESP32 GPIO (CH)
                      │
                   [20 kΩ]
                      │
                     GND
```
* Oran: 20 / (10 + 20) = **0.667** → en kötü durumda 5.0V çıkış ≈ **3.33V**'a iner.
* ADC okumaları yazılımda `× 1.5` ile gerçek sensör gerilimine çevrilebilir (sınıflandırma için gerekmez).

### Seçenek B: Seri Direnç + Schottky Kırpıcı Diyot
```
                         3V3
                          ▲
                          │ (BAT54S üst diyot)
Sensör SIG ──[2.2 kΩ]──┬──┴──► ESP32 GPIO (CH)
                       │
                       ▼ (BAT54S alt diyot)
                      GND
```
* Sinyal ölçeklenmez; 3.3V üstünü ve 0V altını kırpar. Negatif gerilime karşı da korur.

### Kazanç Ayarı
Korumaya ek olarak, sensörde kazanç potu varsa **maksimum kasılmada SIG çıkışı ~3.0V'u geçmeyecek** şekilde ayarlanmalıdır (Bölüm 7, Test 4).

---

## 6. ESP32-S3 Ara Bağlantı Tablosu

Dağıtım kartındaki 5'li erkek soketten ESP32-S3'e **tek bir 5'li dişi-dişi şerit kablo** çekilir:

| Dağıtım Kartı Pini | ESP32-S3 Pini | Sinyal Tanımı | Donanımsal ADC Kanalı |
| :--- | :--- | :--- | :--- |
| **`GND`** | **`GND`** | Ortak Toprak Hattı | Sistem Referansı (0 V) |
| **`CH1`** | **`GPIO 1`** | FDS Kas Sinyali (İç Orta - Yumruk) | ADC1_CH0 |
| **`CH2`** | **`GPIO 2`** | FPL Kas Sinyali (İç Başparmak - Pinch) | ADC1_CH1 |
| **`CH3`** | **`GPIO 3`** | ED Kas Sinyali (Dış Orta - El Açma) | ADC1_CH2 |
| **`CH4`** | **`GPIO 4`** | FCU/EI Kas Sinyali (Bilek / İşaret) | ADC1_CH3 |

*(MPU-6050 modülü doğrudan ESP32-S3'ün `3V3`, `GND`, `GPIO 8 (SDA)` ve `GPIO 9 (SCL)` pinlerine bağlı kalır).*

---

## 7. Devreye Alma Öncesi Güvenlik Kontrolü (Multimetre Testi)

Lehimleme bittikten sonra sensörleri ve ESP32'yi **takmadan önce** multimetreyle şu 3 testi yapın:

- [ ] **1. Kısa Devre Testi (Buzzer Modu):**
  * Klemens üzerindeki `+Vs` ile `GND` arasına probları değdirin -> **Ötmemelidir.**
  * Klemens üzerindeki `-Vs` ile `GND` arasına probları değdirin -> **Ötmemelidir.**
  * Klemens üzerindeki `+Vs` ile `-Vs` arasına probları değdirin -> **Ötmemelidir.**
- [ ] **2. Ortak Toprak Süreklilik Testi (Buzzer Modu):**
  * `GND` klemensine bir probu koyun; 4 sensör soketinin 2. pinlerine ve ESP32 soketinin 1. pinine sırayla değdirin -> **Hepsinde öterek sıfır direnç (0 Ω) vermelidir.**
- [ ] **3. Voltaj Doğrulama (DC Volt Modu):**
  * Güç kaynağını veya pilleri klemense bağlayın (sensörler henüz takılı değil).
  * Siyah prob `GND`'deyken; `+Vs`'de **+3.7V / +5.0V**, `-Vs`'de ise **-3.7V / -5.0V** okunduğunu teyit edin.
- [ ] **4. Sensör Çıkış Gerilimi Testi (ESP32 takılı DEĞİLKEN):**
  * Sensörleri takın ve elektrotları kola yerleştirin; ESP32 soketi boş kalsın.
  * Kası **maksimum kuvvetle** kasarken her kanalın `SIG` – `GND` gerilimini ölçün.
  * Koruma devresinden **sonraki** noktada (ESP soketinin CH pini) okunan değer **3.3V'u geçmemeli** ve **0V'un altına inmemelidir**. Geçiyorsa kazanç potunu düşürün.
- [ ] **5. -Vs İzolasyon Testi (Buzzer Modu):**
  * `-Vs` klemensi ile ESP32 soketinin tüm pinleri arasında **süreklilik olmamalıdır.**

Bu testler tamamlandıktan sonra sensörler ve ESP32 güvenle takılabilir. Breadboard üzerindeki onlarca jumper kablo tek bir kompakt dağıtım modülüne dönüşmüş olur.
