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

Kartın arkasında toplamda yalnızca **4 ana hat** çekilecektir:

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

### Mod B: 2 Adet 3.7 V Li-ion / LiPo Pil
1. **Pil 1'in (-)** kutbu ile **Pil 2'nin (+)** kutbu birbirine bağlanır (Ortak 0V köprüsü).
2. Klemens bağlantısı:
   * **`+Vs` Klemensi:** Pil 1'in (+) kutbuna bağlanır (+3.7 V / 4.2 V).
   * **`GND` Klemensi:** İki pilin birleştiği orta noktaya bağlanır (0 V).
   * **`-Vs` Klemensi:** Pil 2'nin (-) kutbuna bağlanır (-3.7 V / -4.2 V).

---

## 5. ESP32-S3 Ara Bağlantı Tablosu

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

## 6. Devreye Alma Öncesi 2 Dakikalık Güvenlik Kontrolü (Multimetre Testi)

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

Bu testler tamamlandıktan sonra sensörler ve ESP32 güvenle takılabilir. Breadboard üzerindeki onlarca jumper kablo tek bir kompakt dağıtım modülüne dönüşmüş olur.
