# Nuada: Bionic Hand Movement Estimation via TinyML
## Hardware Component Datasheets, Interface Buses & Timing Report

This technical report compiles the architectural specifications, electrical ratings, dynamic ranges, and communication bus timing calculations for all key hardware components evaluated in the **Nuada** bionic prosthesis system.

---

## 1. Quick Reference & Datasheet Archive

All official manufacturer PDF documents are archived in the `docs/datasheets/` directory:

| Component | Function / Role | Interface / Signal | Core Technical Specifications | Local PDF Link |
|---|---|---|---|---|
| **ESP32-S3** | Primary Edge MCU & TinyML Inference Engine | Wi-Fi 4, BLE 5.0, 2x SPI, I2C, DMA ADC | 240 MHz Dual-Core Xtensa LX7, Hardware Vector/AI Acceleration (ESP-NN), 512 KB SRAM | [esp32-s3_datasheet_en.pdf](esp32-s3_datasheet_en.pdf) |
| **AD8232** | Biopotential Analog Front-End (AFE) | Differential Analog Input | CMRR > 80 dB, Integrated Instrumentation Gain x100, 2-Pole Sallen-Key Filter Stage | [ad8232_datasheet.pdf](ad8232_datasheet.pdf) |
| **MCP3008** | External 8-Channel 10-Bit ADC (Plan B / Redundancy) | SPI Bus (Up to 4-Wire) | 200 kSPS @ 5.0V, 75-100 kSPS @ 3.3V, Low Standby Current (5 µA) | [mcp3008_datasheet.pdf](mcp3008_datasheet.pdf) |
| **MPU-6050** | 6-Axis Inertial Measurement Unit (IMU) | I2C Bus (Standard / Fast Mode) | 3-Axis Gyroscope + 3-Axis Accelerometer, Onboard Digital Motion Processor (DMP), 16-Bit ADCs | [mpu6050_datasheet.pdf](mpu6050_datasheet.pdf) |
| **ADS1115** | 4-Channel 16-Bit ADC (Evaluated & Audited) | I2C Bus | Max 860 SPS (Insufficient for multi-channel raw sEMG, viable for envelope only) | [ads1115_datasheet.pdf](ads1115_datasheet.pdf) |

---

## 2. Technical Inquiries & Engineering Analyses

### 2.1 Sensor Range Definitions
In biomedical engineering and sensor interfacing, "sensor range" encompasses three distinct technical parameters:

1. **Input Dynamic Voltage Range:**
   - Raw sEMG potentials generated across superficial forearm muscles: **10 µV – 5 mV (Peak-to-Peak)**.
   - Electrodes transduce ionic cellular currents into electronic microvolt potentials.
2. **Amplified Output Dynamic Range:**
   - The Analog Front-End (AFE / Instrumentation Stage) provides a composite gain of approximately **x1100 V/V**.
   - The output is biased around a virtual ground midpoint of 1.65 V DC, spanning a clean **0.0 V – 3.3 V** scale to utilize the full dynamic resolution of the 12-bit ADC.
3. **Physical Inter-Electrode Distance (IED):**
   - In accordance with the international **SENIAM** (Surface ElectroMyoGraphy for the Non-Invasive Assessment of Muscles) guidelines, the center-to-center spacing between differential pairs is fixed at **20 mm**.
   - Spacing narrower than 20 mm diminishes differential potential magnitude (poor SNR), whereas spacing wider than 20 mm introduces severe muscle crosstalk from adjacent digital flexors/extensors.
4. **Frequency Bandwidth:**
   - Spectral energy density of surface EMG: **20 Hz – 450 Hz**.
   - Analog filter corner frequencies: f_{HPF} = 20 Hz (eliminates motion artifacts), f_{LPF} = 450 Hz (anti-aliasing).

---

### 2.2 SPI Peripheral Architecture on ESP32-S3
The ESP32-S3 system-on-chip incorporates **4 distinct SPI controller peripherals**:
* **SPI0 & SPI1:** Dedicated strictly to internal Flash and external PSRAM memory bus transactions (inaccessible to user firmware).
* **SPI2 (FSPI):** General-purpose, master/slave SPI controller available to user applications. Features independent DMA channels and supports clock frequencies up to 80 MHz.
* **SPI3 (HSPI):** Second fully independent, general-purpose SPI controller available to user applications, also DMA-capable.

> **Definitive Summary:** The ESP32-S3 provides **2 dedicated, user-accessible SPI controllers (SPI2 and SPI3)**. For external ADC integration, **SPI2 (FSPI)** is designated.

---

### 2.3 Bus Timings, Clock Frequencies & Bandwidth Utilization

#### A. SPI Bus Interface (MCP3008 ADC Scenario):
* **Supply Voltage:** V_{DD} = 3.3 V.
* **Maximum SPI Clock Rating:** Per MCP3008 Datasheet Section 6.2, maximum operating frequency at 3.3 V is **1.35 MHz – 2.0 MHz**.
* **ESP32-S3 Master Clock Setting:** **1.5 MHz** (T_{CLK} = 0.667 µs).
* **Single-Sample Acquisition Timing:**
  - Protocol overhead: 1 Start Bit + 4 Configuration Bits + 1 Sample/Null Bit + 10 Data Bits = **17 Clock Cycles** (implemented via 3-byte / 24-clock SPI transactions).
  - Single-channel read latency: 24 \times 0.667 µs = 16 µs.
  - Sequential 4-channel read latency: 4 \times 16 µs = 64 µs.
  - 2000 Hz sampling period: T_{sample} = 1 / 2000 Hz = 500 µs.
  - **Bus Utilization Factor:** 64 µs / 500 µs = \mathbf{12.8\%}.
  - **Conclusion:** Over 87% of the SPI bus remains idle, guaranteeing deterministic, zero-jitter telemetry.

#### B. I2C Bus Interface (MPU-6050 IMU Arm Elevation):
* **Bus Speed:** I2C Fast-Mode (**400 kHz**).
* **Burst Payload:** 3-axis Accelerometer + Temperature + 3-axis Gyroscope = 14 contiguous bytes (14 \times 9 bits \approx 126 cycles \approx 0.315 ms).
* **Sampling Rate:** 100 Hz (T = 10 ms).
* **Bus Utilization Factor:** 0.315 ms / 10 ms = \mathbf{3.15\%}.

---

### 2.4 Internal vs. External ADC: Feasibility of ESP32-S3 Internal ADC

The proposal to utilize the **ESP32-S3 internal SAR ADC** in place of a separate converter IC is technically sound and highly advantageous:

#### Advantages of ESP32-S3 Internal ADC:
1. **Continuous ADC Driver (DMA Mode):**
   The ESP32-S3 features a dedicated I2S/DMA continuous sampling engine. It continuously fills circular DMA buffers with multi-channel conversions (e.g., 4 channels at 2 kHz to 20 kHz each) without consuming CPU cycles.
2. **Immunity from Wi-Fi Collision on ADC1:**
   In legacy ESP32 chips, activating the Wi-Fi radio incapacitated ADC2. On the ESP32-S3, dedicating **ADC1 pins (GPIO 1 through GPIO 4)** ensures zero interference from active RF transmissions.
3. **eFuse Factory Calibration:**
   ESP32-S3 chips are burned with factory calibration parameters (`adc_cali_curve_fitting`), compensating for non-linearities and offset drift across temperature.
4. **Form Factor & Bill of Materials (BOM):**
   Eliminating the external ADC IC reduces PCB footprint, component count, and solder joints on the wearable armband.

#### Engineering Risk Mitigation (Plan A vs. Plan B):
* **Primary Approach (Plan A):** Utilize ESP32-S3 ADC1 in Continuous DMA mode with an external 100 nF decoupling capacitor and 1 kΩ passive RC low-pass filter on each analog input.
* **Redundant Approach (Plan B):** Retain the SPI2-driven MCP3008 architecture as an immediate drop-in fallback if high-power RF burst noise degrades low-amplitude sEMG baselines.
