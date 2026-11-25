# Nuada - 4 Kanal sEMG & Güç Dağıtım Hub'ı
## Delikli Pertinaks (Perfboard) Yerleşim ve Lehimleme Kılavuzu

Bu belge; breadboard üzerindeki jumper kablo karmaşasını, temassızlıkları ve sinyal parazitlerini ortadan kaldırmak amacıyla tasarlanan **4 Kanal sEMG & Güç Dağıtım Hub'ı**nın delikli pertinaks üzerindeki bileşen yerleşimini, delik delik lehim planını ve kablo bağlantılarını içerir.

---

## 0. Kullanılan Sensör ve Ölçülen Değerler

| Özellik | Değer |
| :--- | :--- |
| **Modül** | Hazır sEMG kas sensörü (TLS Robotik AC-NB084) – Advancer Technologies *Muscle Sensor V3* klonu, 27.3 × 27.3 mm kırmızı kart |
| **Yükselteç** | TL084 (4'lü op-amp) |
| **Besleme konnektörü (J1)** | `+Vs` · `GND` · `-Vs` → **çift (±) besleme** (satıcı sayfasındaki "3.3–5V" bilgisi yanıltıcıdır) |
| **Sinyal konnektörü (J2)** | `SIG` · `GND` |
| **Elektrot girişi** | 3.5 mm jak (kas ortası, kas ucu, referans) |
| **Kazanç potu** | Yok (sabit kazanç) |
| **Çalışma beslemesi** | **±5V** |
| **Ölçülen çıkış (osiloskop, ±5V)** | Dinlenme ~0V · Kasılmada yalnızca **pozitif**, doğrultulmuş sivri darbeler · Tepe **2.5 – 3.3V** · En düşük **-40 mV** |

> **Sonuç:** ±5V'ta TL084 çıkışı fiziksel olarak ~3.3–3.5V'u geçemez. Her kanala bir **10 kΩ / 20 kΩ gerilim bölücü** yeterlidir (ESP'ye en fazla ~2.3V ulaşır). Diyot veya başka koruma parçası gerekmez.
>
> **Yazılım notu:** Sinyal milisaniyelik darbelerden oluştuğu için 100 Hz örnekleme yetersizdir; ESP32-S3 tarafında **~1000 Hz** örnekleme + pencere RMS/ortalama kullanılmalıdır. Dinlenme tabanı **~0** (AD8232'deki 2048 değil). Multimetre bu sinyalin yalnızca ortalamasını (~0.1–0.5V) gösterir; tepe ölçümü için osiloskop kullanın.

---

## 1. Malzeme Listesi (BOM)

| Parça | Adet | Açıklama |
| :--- | :--- | :--- |
| **Delikli Pertinaks / Plaket** | 1 | Tek yüzey, ada (pad) tipi, 2.54 mm aralık. **En az 22 × 16 delik** (~6 × 4.5 cm) |
| **4'lü Dişi Pin Header (2.54 mm)** | 4 | Sensör kabloları için (CH1–CH4) |
| **3'lü Vidalı Klemens (5.08 mm)** | 1 | Güç girişi (`+Vs`, `GND`, `-Vs`) |
| **5'li Erkek Pin Header (2.54 mm)** | 1 | ESP32'ye giden çıkış (`GND`, `CH1`–`CH4`) |
| **10 kΩ Direnç (1/4 W)** | 4 | Bölücü üst direnci (kahverengi-siyah-turuncu) |
| **20 kΩ Direnç (1/4 W)** | 4 | Bölücü alt direnci (kırmızı-siyah-turuncu). Yoksa **22 kΩ** (kırmızı-kırmızı-turuncu) |
| **Çıplak kalaylı tel** (veya kesilmiş direnç bacakları) | ~25 cm | Arka yüzdeki 3 ray (+Vs, -Vs, GND) |
| **İzoleli ince montaj teli** (zil teli / 30 AWG) | ~1 m | Sensör soketlerinden raylara ve ESP soketine giden hatlar |
| **Dişi-Erkek Jumper Kablo** | 16 | Sensör kartı (dişi uç) → hub soketi (erkek uç), kanal başına 4 adet |
| **Dişi-Dişi Jumper Kablo** | 5 | Hub ESP soketi → ESP32-S3 pinleri |
| *(İsteğe Bağlı)* **100 nF Seramik Kondansatör** | 2 | Besleme gürültü filtresi (`+Vs–GND` ve `-Vs–GND` arasına, klemense yakın) |

---

## 2. Devre Şeması (Tek Kanal)

Her kanal aynıdır; dört kez tekrarlanır:

```
 Güç klemensi                     Sensör soketi (dişi)              ESP32 soketi
 ─────────────                    ─────────────────────             ────────────
 +Vs ── [+Vs rayı] ─────────────► pin 1 (+Vs)
 GND ── [GND rayı] ─────────────► pin 2 (GND)
 -Vs ── [-Vs rayı] ─────────────► pin 3 (-Vs)
                                  pin 4 (SIG) ──[10 kΩ]──●──────────► CHk
                                                         │
                                                      [20 kΩ]
                                                         │
                                  [GND rayı] ────────────┴──────────► GND
```

* **`+Vs` ve `-Vs` hiçbir şekilde ESP soketine gitmez.**
* Bölücü oranı 20 / (10 + 20) = **0.667** → 3.3V tepe ≈ **2.2V**, -40 mV ≈ **-27 mV** (ESP sınırları: -0.3V … 3.6V).

---

## 3. Delik Delik Yerleşim Planı (Üstten Görünüm)

Kartı, **sol üst köşe = satır 1, sütun 1** olacak şekilde tutun. Satırlar yukarıdan aşağıya (1–16), sütunlar soldan sağa (01–22) numaralandırılır. Kart daha büyükse planı sol üst köşeden başlatın.

```
     01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22
 1    . K+  . K0  . K-  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
 2    . P= P= P= P= P= P= P= P= P= P= P= P= P= P= P= P= P= P= P=  .  .
 3    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
 4    . N= N= N= N= N= N= N= N= N= N= N= N= N= N= N= N= N= N= N=  .  .
 5    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
 6    . G= G= G= d1 G= G= G= G= d2 G= G= G= G= d3 G= G= G= G= d4 G= E0
 7    .  .  .  .  :  .  .  .  .  :  .  .  .  .  :  .  .  .  .  :  . E1
 8    .  .  .  .  :  .  .  .  .  :  .  .  .  .  :  .  .  .  .  :  . E2
 9    .  .  .  .  :  .  .  .  .  :  .  .  .  .  :  .  .  .  .  :  . E3
10    .  .  .  . c1  .  .  .  . c2  .  .  .  . c3  .  .  .  . c4  . E4
11    .  .  .  . b1  .  .  .  . b2  .  .  .  . b3  .  .  .  . b4  .  .
12    .  .  .  .  |  .  .  .  .  |  .  .  .  .  |  .  .  .  .  |  .  .
13    .  .  .  .  |  .  .  .  .  |  .  .  .  .  |  .  .  .  .  |  .  .
14    .  .  .  .  |  .  .  .  .  |  .  .  .  .  |  .  .  .  .  |  .  .
15    .  .  .  . a1  .  .  .  . a2  .  .  .  . a3  .  .  .  . a4  .  .
16    . 1+ 10 1- 1S  . 2+ 20 2- 2S  . 3+ 30 3- 3S  . 4+ 40 4- 4S  .  .
```

**Gösterim:**

| İşaret | Anlamı |
| :--- | :--- |
| `K+` `K0` `K-` | Güç klemensi bacakları: `+Vs`, `GND`, `-Vs` (5.08 mm aralık → 1 delik boşluklu) |
| `P=` | **+Vs rayı** (satır 2, arka yüzde çıplak tel) |
| `N=` | **-Vs rayı** (satır 4, arka yüzde çıplak tel) |
| `G=` | **GND rayı** (satır 6, arka yüzde çıplak tel) |
| `E0`–`E4` | ESP soketi (5'li erkek header, dik): `E0`=GND, `E1`=CH1, `E2`=CH2, `E3`=CH3, `E4`=CH4 |
| `k+` `k0` `k-` `kS` | k. sensör soketi (4'lü dişi header): `+Vs`, `GND`, `-Vs`, `SIG` |
| `ak`–`bk` (`|`) | k. kanalın **10 kΩ** direnci (bacaklar `a` ve `b` deliklerinde, 4 delik aralık) |
| `ck`–`dk` (`:`) | k. kanalın **20 kΩ** direnci (`d` bacağı doğrudan GND rayına lehimlenir) |

Kanal sütunları: **CH1 = 02–05**, **CH2 = 07–10**, **CH3 = 12–15**, **CH4 = 17–20**.

---

## 4. Tel Bağlantı Listesi

Koordinatlar **(satır, sütun)** biçimindedir. "Köprü" = komşu iki deliği lehimle birleştirmek. Raylar arasından geçen tüm teller **izoleli** olmalıdır.

### 4.1 Raylar (arka yüz, çıplak tel)
| # | Hat | Nereden → Nereye |
| :-: | :--- | :--- |
| R1 | +Vs rayı | (2,02) → (2,20) boyunca düz tel, her 3–4 delikte bir lehim |
| R2 | -Vs rayı | (4,02) → (4,20) |
| R3 | GND rayı | (6,02) → (6,21) |

### 4.2 Güç girişi ve ESP GND
| # | Hat | Nereden → Nereye | Tel |
| :-: | :--- | :--- | :--- |
| W1 | Klemens +Vs | (1,02) ↔ (2,02) | Köprü |
| W2 | Klemens GND | (1,04) → (6,04) | **İzoleli** (+Vs ve -Vs raylarının üstünden geçer) |
| W3 | Klemens -Vs | (1,06) → (4,06) | **İzoleli** (+Vs rayının üstünden geçer) |
| W4 | ESP GND | (6,22) ↔ (6,21) | Köprü |

### 4.3 Her kanal için (c = kanalın ilk sütunu: CH1=02, CH2=07, CH3=12, CH4=17)
| # | Hat | Nereden → Nereye | Tel |
| :-: | :--- | :--- | :--- |
| 1 | Soket +Vs → +Vs rayı | (16, c) → (2, c) | **İzoleli** |
| 2 | Soket GND → GND rayı | (16, c+1) → (6, c+1) | İzoleli (önerilir) |
| 3 | Soket -Vs → -Vs rayı | (16, c+2) → (4, c+2) | **İzoleli** (GND rayının üstünden geçer) |
| 4 | Soket SIG → 10 kΩ alt bacak | (16, c+3) ↔ (15, c+3) | Köprü |
| 5 | Bölücü orta noktası | (11, c+3) ↔ (10, c+3) | Köprü (10k üst bacak + 20k alt bacak) |
| 6 | Orta nokta → ESP soketi | (10, c+3) → (5+k, 22) | **İzoleli** (CH1→(7,22), CH2→(8,22), CH3→(9,22), CH4→(10,22)) |

Açık hâliyle:

| Kanal | +Vs teli | GND teli | -Vs teli | SIG köprü | 10 kΩ | 20 kΩ | Orta nokta → ESP |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CH1 | (16,02)→(2,02) | (16,03)→(6,03) | (16,04)→(4,04) | (16,05)↔(15,05) | (15,05)–(11,05) | (10,05)–(6,05) | (10,05)→(7,22) `E1` |
| CH2 | (16,07)→(2,07) | (16,08)→(6,08) | (16,09)→(4,09) | (16,10)↔(15,10) | (15,10)–(11,10) | (10,10)–(6,10) | (10,10)→(8,22) `E2` |
| CH3 | (16,12)→(2,12) | (16,13)→(6,13) | (16,14)→(4,14) | (16,15)↔(15,15) | (15,15)–(11,15) | (10,15)–(6,15) | (10,15)→(9,22) `E3` |
| CH4 | (16,17)→(2,17) | (16,18)→(6,18) | (16,19)→(4,19) | (16,20)↔(15,20) | (15,20)–(11,20) | (10,20)–(6,20) | (10,20)→(10,22) `E4` |

*(İsteğe bağlı 100 nF kondansatörler: biri +Vs rayı ile GND rayı arasına, biri -Vs rayı ile GND rayı arasına, klemense yakın boş deliklere; bacaklar raylara kısa izoleli tellerle bağlanır.)*

---

## 5. Lehimleme Sırası

1. **Plan çizimi:** Kartın üstüne kurşun kalemle satır 1/sütun 1'i ve kanal sütunlarını işaretleyin.
2. **Raylar (R1–R3):** Arka yüzde 2., 4. ve 6. satırlara çıplak teli yatırın, her 3–4 delikte bir lehimleyin. Raylar **birbirine değmemeli** (aralarında birer boş satır var).
3. **Dirençler (en alçak parçalar önce):** 4 × 10 kΩ'u `a`–`b`, 4 × 20 kΩ'u `c`–`d` deliklerine takın, lehimleyin, bacak fazlalarını kesin. `d` bacakları GND rayına lehimlenir.
4. **Köprüler:** Her kanalda (16,c+3)↔(15,c+3) ve (11,c+3)↔(10,c+3) köprülerini yapın. W1 ve W4 köprülerini yapın.
5. **Soketler:** 4 adet 4'lü dişi header'ı 16. satıra, 5'li erkek header'ı 22. sütuna (satır 6–10), klemensi 1. satıra lehimleyin.
6. **İzoleli teller:** Önce güç (W2, W3), sonra her kanalın +Vs / GND / -Vs telleri, en son orta nokta → ESP telleri.
7. **Temizlik:** Lehim artıklarını ve komşu adalar arasındaki istenmeyen köprüleri büyüteçle kontrol edin.

---

## 6. Güç Kaynağı Bağlantısı

### Masaüstü Çift Çıkışlı DC Güç Kaynağı (UNI-T) — Önerilen
1. Kaynağı **Independent (bağımsız)** moda alın.
2. CH1 ve CH2: **5.00 V**, akım limiti **0.1–0.2 A**, varsa OVP **5.5 V**.
3. **CH1 Siyah (-)** ile **CH2 Kırmızı (+)** birbirine bağlanır (ortak 0V köprüsü).
4. Klemens bağlantısı:
   * **`K+` (+Vs):** CH1 Kırmızı (+) → +5.0 V
   * **`K0` (GND):** Ortak 0V köprüsü → 0 V
   * **`K-` (-Vs):** CH2 Siyah (-) → -5.0 V
5. Normal çalışmada **CV** lambası yanar ve 4 sensörle toplam akım birkaç on mA'dır. **CC** lambası yanarsa çıkışı kapatıp bağlantıları kontrol edin.

> **Neden ±3.3V değil?** TL084 op-amp'leri yaklaşık ±5V altında düzgün çalışmaz; ±3.3V'ta sinyal kırpılır veya kart hiç çalışmaz.

### Pil ile Çalışma
* **2 × 3.7 V LiPo (±3.7V) KULLANMAYIN.** TL084 için yetersizdir ve pil boşaldıkça (~3.2V) daha da düşer.
* Pille çalışmak gerekirse besleme **±5V'a regüle edilmeli** ya da **2 × 9V pil (±9V)** kullanılmalıdır. **±9V'ta çıkış ~7.5V'a kadar çıkabilir; bu durumda 20 kΩ yerine 4.7 kΩ kullanılmalıdır** (10k/4.7k → 7.5V ≈ 2.4V).

---

## 7. Bağlantı Tabloları

### 7.1 Sensör Kartı → Hub (kanal başına 4 dişi-erkek jumper)
| Sensör kartı pini | Hub soket pini |
| :--- | :--- |
| J1 `+Vs` | `k+` |
| J1 `GND` | `k0` |
| J1 `-Vs` | `k-` |
| J2 `SIG` | `kS` |

*(J1'in pin sırası hub soketiyle aynıdır: +Vs, GND, -Vs. J2'deki GND boş kalabilir.)*

### 7.2 Hub → ESP32-S3 (5 dişi-dişi jumper)
| Hub ESP soketi | ESP32-S3 Pini | Sinyal | ADC Kanalı |
| :--- | :--- | :--- | :--- |
| **`E0`** | **`GND`** | Ortak Toprak | Referans (0 V) |
| **`E1`** | **`GPIO 1`** | CH1 – FDS (İç Orta - Yumruk) | ADC1_CH0 |
| **`E2`** | **`GPIO 2`** | CH2 – FPL (İç Başparmak - Pinch) | ADC1_CH1 |
| **`E3`** | **`GPIO 3`** | CH3 – ED (Dış Orta - El Açma) | ADC1_CH2 |
| **`E4`** | **`GPIO 4`** | CH4 – FCU/EI (Bilek / İşaret) | ADC1_CH3 |

*(MPU-6050 modülü doğrudan ESP32-S3'ün `3V3`, `GND`, `GPIO 8 (SDA)` ve `GPIO 9 (SCL)` pinlerine bağlı kalır.)*

---

## 8. Devreye Alma Öncesi Güvenlik Kontrolü

Lehimleme bittikten sonra sensörleri ve ESP32'yi **takmadan önce**:

- [ ] **1. Kısa Devre Testi (Multimetre, Buzzer Modu):**
  * `K+` ↔ `K0`, `K-` ↔ `K0`, `K+` ↔ `K-` → **Ötmemelidir.**
- [ ] **2. Ortak Toprak Sürekliliği (Buzzer Modu):**
  * `K0` ↔ her soketin `k0` pini ve `E0` → **Ötmelidir.**
- [ ] **3. -Vs / +Vs İzolasyonu (Buzzer Modu):**
  * `K-` ve `K+` ↔ `E0`–`E4` pinlerinin hiçbiri → **Ötmemelidir.**
- [ ] **4. Bölücü Direnç Kontrolü (Ohm Modu, güç kapalı):**
  * Her `kS` ↔ `E0`: **~30 kΩ** (10k + 20k)
  * Her `Ek` ↔ `E0`: **~20 kΩ** (sensör takılı değilken yalnızca alt direnç ölçülür)
  * Her `kS` ↔ `Ek`: **~10 kΩ**
- [ ] **5. Voltaj Doğrulama (DC Volt, sensörler takılı değil):**
  * Siyah prob `K0`'da: her soketin `k+` pininde **+5.0V**, `k-` pininde **-5.0V**.
- [ ] **6. Çıkış Testi (Osiloskop, ESP32 takılı DEĞİLKEN):**
  * Sensörleri takın, elektrotları yerleştirin. Prob `Ek` pinine, toprak klipsi `E0`'a (**asla ±Vs'ye değil**).
  * Ayarlar: DC kuplaj, 1 V/div, 200 ms/div, AUTO tetik.
  * Maksimum kasılmada tepe değer **≤ 2.5V** (bölücü sonrası) ve en düşük değer **> -0.3V** olmalıdır.

Bu testler tamamlandıktan sonra ESP32 güvenle bağlanabilir.

> **Güvenlik:** Elektrotlar denekteyken ESP32'ye USB ile bağlı laptopu **şarjdan çıkarın** (pil ile çalıştırın).
