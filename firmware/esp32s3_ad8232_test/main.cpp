#include <Arduino.h>
#include <Wire.h>

// ==============================================================================
// NUADA BIONIC HAND - 4x EMG + 1x MPU6050 SYNCHRONIZED ACQUISITION
// Microcontroller: ESP32-S3 DevKitC-1
// ADC Channels   : ADC1 (GPIO 1, 2, 3, 4) - Wi-Fi Bağımsız Donanımsal ADC
// IMU (MPU6050)  : I2C (SDA: GPIO 8, SCL: GPIO 9 @ 400 kHz Fast-Mode)
// Sampling Rate  : 100 Hz (Her 10 ms'de eş zamanlı 10 öznitelik)
// Baud Rate      : 115200 (veya 230400 / 921600)
// ==============================================================================

// --- EMG PİN TANIMLARI ---
#define EMG1_PIN 1   // CH1: FDS (Parmak Bükücü / Pinch)
#define EMG2_PIN 2   // CH2: FPL (Başparmak Bükücü)
#define EMG3_PIN 3   // CH3: ED  (Parmak Açıcı / Point)
#define EMG4_PIN 4   // CH4: FCU (Bilek / Yan Stabilite)

// --- MPU6050 I2C PİNLERİ VE ADRESİ ---
#define I2C_SDA_PIN 8
#define I2C_SCL_PIN 9
#define MPU6050_ADDR 0x68

// ESP32-S3 Dahili RGB LED (GPIO 48)
#ifndef RGB_BUILTIN
#define RGB_BUILTIN 48
#endif

// Zamanlama Değişkenleri (100 Hz = 10.000 µs)
const unsigned long SAMPLE_INTERVAL_US = 10000; 
unsigned long lastSampleTime = 0;
bool mpuAvailable = false;

// MPU6050 Başlatma ve Uyandırma Fonksiyonu
bool initMPU6050() {
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 400000); // 400 kHz Fast I2C
  Wire.beginTransmission(MPU6050_ADDR);
  byte error = Wire.endTransmission();
  if (error != 0) {
    return false; // Cihaz I2C hattında bulunamadı
  }

  // PWR_MGMT_1 register (0x6B) -> 0x00 yazarak uyku modundan çıkar
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission(true);

  // İvmeölçer Konfigürasyonu: ±4g aralığı (ACCEL_CONFIG 0x1C -> 0x08)
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x1C);
  Wire.write(0x08);
  Wire.endTransmission(true);

  // Jiroskop Konfigürasyonu: ±500 deg/s aralığı (GYRO_CONFIG 0x1B -> 0x08)
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x1B);
  Wire.write(0x08);
  Wire.endTransmission(true);

  return true;
}

// MPU6050'den 6 Eksen Veriyi Tek Burst ile Hızlı Okuma (~350 µs)
void readMPU6050(int16_t &ax, int16_t &ay, int16_t &az, int16_t &gx, int16_t &gy, int16_t &gz) {
  if (!mpuAvailable) {
    ax = ay = az = gx = gy = gz = 0;
    return;
  }

  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B); // ACCEL_XOUT_H register adresi
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)MPU6050_ADDR, (size_t)14, true);

  if (Wire.available() >= 14) {
    ax = Wire.read() << 8 | Wire.read();
    ay = Wire.read() << 8 | Wire.read();
    az = Wire.read() << 8 | Wire.read();
    Wire.read(); Wire.read(); // Sıcaklık verisini atla
    gx = Wire.read() << 8 | Wire.read();
    gy = Wire.read() << 8 | Wire.read();
    gz = Wire.read() << 8 | Wire.read();
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // 12-bit ADC Kalibrasyonu (0 - 4095)
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  pinMode(EMG1_PIN, INPUT);
  pinMode(EMG2_PIN, INPUT);
  pinMode(EMG3_PIN, INPUT);
  pinMode(EMG4_PIN, INPUT);

  // Dahili LED Başlangıç: Mavi
  neopixelWrite(RGB_BUILTIN, 0, 0, 64);

  Serial.println("\n=======================================================");
  Serial.println("  NUADA - 4 KANAL sEMG + MPU6050 EŞ ZAMANLI VERİ HATTI ");
  Serial.println("=======================================================");
  Serial.println("Kanal Haritası: ADC1 [GPIO 1, 2, 3, 4]");
  Serial.println("IMU Arayüzü   : I2C [SDA: GPIO 8, SCL: GPIO 9]");
  Serial.println("Örnekleme Hızı: 100 Hz (10 ms eş zamanlı paket)");
  Serial.println("Paket Formatı : DATA,time_ms,e1,e2,e3,e4,ax,ay,az,gx,gy,gz");
  Serial.println("-------------------------------------------------------");

  // MPU6050 Başlat
  mpuAvailable = initMPU6050();
  if (mpuAvailable) {
    Serial.println("[TAMAM] MPU6050 başarıyla bağlandı ve uyandırıldı (0x68).");
    neopixelWrite(RGB_BUILTIN, 0, 64, 0); // Yeşil
  } else {
    Serial.println("[UYARI] MPU6050 bulunamadı! Yalnızca EMG kanalları okunacak.");
    neopixelWrite(RGB_BUILTIN, 64, 30, 0); // Sarı
  }
  Serial.println("=======================================================\n");
  delay(1000);
}

void loop() {
  unsigned long now = micros();

  // 100 Hz Hassas Eş Zamanlı Örnekleme (Her 10.000 µs = 10 ms)
  if (now - lastSampleTime >= SAMPLE_INTERVAL_US) {
    lastSampleTime = now;
    unsigned long timeMs = millis();

    // 1. Dört Analog EMG Kanalını Sırayla Oku (Toplam süre: ~80 µs)
    int emg1 = analogRead(EMG1_PIN);
    int emg2 = analogRead(EMG2_PIN);
    int emg3 = analogRead(EMG3_PIN);
    int emg4 = analogRead(EMG4_PIN);

    // 2. MPU-6050 IMU Verilerini Oku (~350 µs)
    int16_t ax, ay, az, gx, gy, gz;
    readMPU6050(ax, ay, az, gx, gy, gz);

    // 3. Eş Zamanlı Tek Satır Veri Paketi Bas
    // Format: DATA,time_ms,emg1,emg2,emg3,emg4,ax,ay,az,gx,gy,gz
    Serial.print("DATA,");
    Serial.print(timeMs);
    Serial.print(",");
    Serial.print(emg1);
    Serial.print(",");
    Serial.print(emg2);
    Serial.print(",");
    Serial.print(emg3);
    Serial.print(",");
    Serial.print(emg4);
    Serial.print(",");
    Serial.print(ax);
    Serial.print(",");
    Serial.print(ay);
    Serial.print(",");
    Serial.print(az);
    Serial.print(",");
    Serial.print(gx);
    Serial.print(",");
    Serial.print(gy);
    Serial.print(",");
    Serial.println(gz);
  }
}
