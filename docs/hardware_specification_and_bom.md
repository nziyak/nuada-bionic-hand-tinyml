# Nuada: Bionic Hand Movement Estimation via TinyML
## Final Hardware Specification, Bill of Materials (BOM) & Wiring Architecture

This document establishes the finalized, production-ready embedded hardware blueprint for the **Nuada** bionic prosthesis system. Based on faculty advisory guidance, the architecture is engineered to be **100% off-the-shelf, modular, solderless, and dry-electrode native**, eliminating custom analog prototyping risks while focusing engineering effort directly on TinyML execution and real-time inference.

---

## 1. Engineering Philosophy: Modular & Solderless Architecture

### Why No Custom Discrete Circuits or SMD Rework?
1. **0402 / 0603 SMD Desoldering Risks:** Standard AD8232 commercial breakout boards populate miniature 0603 (1.6 mm x 0.8 mm) and 0402 (1.0 mm x 0.5 mm) passive components. Manual desoldering carries a high probability of lifting copper PCB pads or thermal destruction.
2. **Unmarked MLCC Ceramic Capacitors:** Unlike resistors, SMD ceramic capacitors bear no stamped numerical values. Identifying capacitance without a laboratory-grade LCR meter is impossible.
3. **Focus on TinyML & Firmware:** Building custom breadboard op-amp circuits introduces parasitic capacitance and antenna noise. Using tested, off-the-shelf breakout modules guarantees repeatable biopotential amplification, directing primary development time toward the dual-core FreeRTOS architecture and neural network deployment.
4. **Signal Sufficiency of Unmodified AD8232:** While individual motor unit action potentials fire at up to 450 Hz, the energetic recruitment envelope and firing rate modulation governing gross muscle contractions are concentrated below 40 Hz. The factory 0.5 Hz – 40 Hz passband of the AD8232 delivers clean, pre-filtered activation envelopes that the ESP32-S3 ADC can directly classify into hand gestures with high fidelity.

---

## 2. Complete Bill of Materials (BOM) & Budget

The entire 4-channel sEMG + 6-axis IMU + TinyML hardware pipeline is procured for under $30 (~850 – 950 TL):

| Qty | Component | Technical Function / Model | Estimated Cost (TRY) | Estimated Cost (USD) |
|---|---|---|---|---|
| **1x** | **ESP32-S3 Development Board** | Dual-core Xtensa LX7 @ 240 MHz, AI Vector Instructions, 512 KB SRAM, 2x SPI, I2C, 12-bit ADC1 *(ESP32-S3 DevKitC-1 or Seeed Studio XIAO ESP32-S3)* | ~₺220 - ₺280 | ~$7.50 |
| **4x** | **AD8232 Biopotential Modules** | Single-lead analog front-end breakout boards (red PCB), each bundled with a 3-lead 3.5 mm medical snap cable. Used unmodified. | 4 x ~₺110 = ~₺440 | ~$13.50 |
| **1x** | **MPU-6050 6-Axis IMU Module** | 3-axis accelerometer + 3-axis gyroscope with integrated DMP, I2C Fast-Mode interface. | ~₺70 - ₺90 | ~$2.50 |
| **1 Tube** | **Medical Conductive Gel (250 ml)** | Medical EKG/Ultrasound conductive gel applied in micro-droplets on snaps for multi-subject clean data acquisition without single-use pad waste. | ~₺35 - ₺50 | ~$1.20 |
| **1 Pk** | **Stainless-Steel Snap Fasteners** | 3.7 mm / 4 mm male/female metal snaps perching through the armband to form reusable **snap electrodes**. | ~₺25 - ₺40 | ~$1.00 |
| **1x** | **Elastic Velcro Armband** | Breathable neoprene / elastic sport strap to secure snap electrodes firmly against forearm skin across diverse arm sizes. | ~₺40 - ₺60 | ~$1.50 |
| **1 Pk** | **Breadboard Jumper Wires** | Female-to-female and female-to-male jumper wires for solderless interconnects. | ~₺35 | ~$1.00 |
| **TOTAL** | **Complete Wearable TinyML Hardware Kit** | **Reusable Across 100+ Subjects, Zero Custom PCB, Zero Soldering Required** | **~₺865 - ₺995** | **~$28.00** |


---

## 3. Physical Snap-Electrode Construction & Multi-Subject Standardization Protocol

```
   [ OUTER ARMBAND SURFACE ] ─── (Female Snap Connector: Plugs into AD8232 Cable)
              │
      [ ELASTIC FABRIC ]     ─── (20 mm SENIAM Spacing Between Pairs)
              │
   [ INNER ARMBAND SURFACE ] ─── (Smooth Stainless-Steel Stud: Direct Contact with Skin)
              │
     [ MICRO GEL DROPLET ]   ─── (Optional: 1 drop of conductive gel for ultra-low impedance)
```

### Construction & Multi-Subject Hygiene:
1. **Electrode Material:** Standard stainless-steel snap buttons (3.7 mm or 4 mm stud diameter).
2. **Fabric Mounting:** Snaps are riveted through the elastic armband at the four designated muscle sites:
   * **Pair 1 (CH1):** *Flexor Digitorum Superficialis* (Anterior/Medial)
   * **Pair 2 (CH2):** *Flexor Pollicis Longus* (Anterior/Radial)
   * **Pair 3 (CH3):** *Extensor Digitorum* (Posterior/Central)
   * **Pair 4 (CH4):** *Extensor Pollicis & Indicis* (Posterior/Radial)
   * **Ground / Reference:** Single snap located over the bony elbow *Olecranon*.
3. **Dual-Mode Operation (Gel-Assisted vs. True Dry):**
   * **Phase 1 (Proof-of-Concept / Gel-Assisted):** Apply a single micro-droplet of conductive gel directly onto each metal snap. The elastic band provides mechanical pressure while the gel eliminates skin-contact impedance. Wipe clean with an alcohol wipe after each subject session. Zero disposable waste.
   * **Phase 2 (True Dry Benchmark):** Test the exact same armband dry to evaluate noise tolerance and domain shift resistance.

### Multi-Subject Anatomical Normalization Rules:
* **The 5 cm Height Rule:** Measure exactly 5 cm distal from the cubital elbow crease. Align the top edge of the armband to this marker on every subject.
* **Angular Landmark:** Align Channel 1 with the medial epicondyle axis to ensure identical spatial muscle mapping across varying forearm circumferences (20 cm to 30 cm).
* **MVC Normalization:** Prior to recording, record a 3-second Maximum Voluntary Contraction (full fist) per subject to normalize signal amplitude into a standardized [0, 1] range, preventing variations in muscle volume from corrupting classification.


---

## 4. Complete Interconnect & Pinout Mapping

All modules operate natively from the ESP32-S3's regulated 3.3 V rail. No external voltage level shifters or pull-up resistors are required.

```
+-------------------------------------------------------------------------------+
|                               ESP32-S3 DevKit                                 |
|                                                                               |
|  3.3V  GND   GPIO1   GPIO2   GPIO3   GPIO4       GPIO8   GPIO9                |
+----+----+------+-------+-------+-------+-----------+-------+------------------+
     |    |      |       |       |       |           |       |
     |    |      |       |       |       |           |       | (I2C Fast Mode)
     |    |   +--+----+  |       |       |           |       |
     |    |   |AD8232 |  |       |       |           |       |
     |    |   | CH 1  |  |       |       |           |       |
     |    |   +-------+  |       |       |           |       |
     |    |   (OUTPUT)   |       |       |           |       |
     |    |              |       |       |           |       |
     |    |           +--+----+  |       |           |       |
     |    |           |AD8232 |  |       |           |       |
     |    |           | CH 2  |  |       |           |       |
     |    |           +-------+  |       |           |       |
     |    |           (OUTPUT)   |       |           |       |
     |    |                      |       |           |       |
     |    |                   +--+----+  |           |       |
     |    |                   |AD8232 |  |           |       |
     |    |                   | CH 3  |  |           |       |
     |    |                   +-------+  |           |       |
     |    |                   (OUTPUT)   |           |       |
     |    |                              |           |       |
     |    |                           +--+----+      |       |
     |    |                           |AD8232 |      |       |
     |    |                           | CH 4  |      |       |
     |    |                           +-------+      |       |
     |    |                           (OUTPUT)       |       |
     |    |                                          |       |
     |    +------------------------------------------+-------+--- MPU-6050 GND
     +-----------------------------------------------+-------+--- MPU-6050 VCC (3.3V)
                                                     |       |
                                                     |       +--- MPU-6050 SCL
                                                     +----------- MPU-6050 SDA
```

### Pin-by-Pin Interconnect Table:

| Subsystem | Peripheral Module | Module Pin | ESP32-S3 Target Pin | Pin Function / Hardware Channel | Electrical Notes |
|---|---|---|---|---|---|
| **Power** | All 4x AD8232 + MPU-6050 | `3.3V` / `VCC` | **3V3** | Regulated 3.3V Power Bus | Common rail from onboard MCU LDO regulator. |
| **Power** | All 4x AD8232 + MPU-6050 | `GND` | **GND** | System Common Ground | Common low-impedance ground plane. |
| **sEMG CH1** | AD8232 (Module 1 - FDS) | `OUTPUT` | **GPIO 1** | ADC1_CH0 (Analog Input) | 0.0 V - 3.3 V rail-to-rail analog waveform. |
| **sEMG CH2** | AD8232 (Module 2 - FPL) | `OUTPUT` | **GPIO 2** | ADC1_CH1 (Analog Input) | 0.0 V - 3.3 V rail-to-rail analog waveform. |
| **sEMG CH3** | AD8232 (Module 3 - ED) | `OUTPUT` | **GPIO 3** | ADC1_CH2 (Analog Input) | 0.0 V - 3.3 V rail-to-rail analog waveform. |
| **sEMG CH4** | AD8232 (Module 4 - EPL) | `OUTPUT` | **GPIO 4** | ADC1_CH3 (Analog Input) | 0.0 V - 3.3 V rail-to-rail analog waveform. |
| **Kinematics**| MPU-6050 IMU | `SDA` | **GPIO 8** | I2C Data (SDA) | Internal pull-up enabled; 400 kHz Fast-Mode. |
| **Kinematics**| MPU-6050 IMU | `SCL` | **GPIO 9** | I2C Clock (SCL) | Internal pull-up enabled; 400 kHz Fast-Mode. |
| **Unused** | All AD8232 Modules | `LO+`, `LO-`, `SDN` | *Not Connected* | Leads-Off / Shutdown | Left floating (open circuit). |

---

## 5. Firmware Execution & Dual-Core Task Allocation

With all four analog channels wired directly to **ADC1** and the IMU wired to **I2C**, the dual-core FreeRTOS architecture executes without resource contention:

```
[ ESP32-S3 CORE 1: HARD REAL-TIME ] ─────────► [ ESP32-S3 CORE 0: SOFT REAL-TIME ]
• vTaskEMGSampling (DMA ADC1 @ 1000 Hz)        • vTaskIMUSampling (MPU-6050 @ 100 Hz)
• Ping-Pong Double Ring Buffering              • Complementary Filter (Pitch/Roll)
• 1D-CNN Inference (TFLite Micro + ESP-NN)     • FreeRTOS LwIP Wi-Fi UDP Telemetry
• Latency: < 15 ms                             • Latency: < 5 ms
```

---

## 6. Summary Checklist for Faculty Review

1. **Hardware Simplicity:** Only 1x ESP32-S3, 4x unmodified AD8232 boards, 1x MPU-6050, and 1x snap-button armband.
2. **Solderless Assembly:** All interconnections made via standard jumper wires and 3.5 mm snap leads.
3. **Budget Compliance:** Full system cost is under 1000 TL (~$27 USD).
4. **Electrode Hygiene:** 100% dry, reusable metal electrodes; no messy single-use electrolyte gel required.
5. **Direct Analog Compatibility:** 0.0 V – 3.3 V analog output directly feeds ESP32-S3 ADC1 (GPIO 1–4) with zero Wi-Fi RF collision.
