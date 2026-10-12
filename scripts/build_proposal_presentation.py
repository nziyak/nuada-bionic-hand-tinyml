import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

TEMPLATE_PATH = '/home/zia/Documents/school/graduation-project/nuada/docs/presentations/GTU_graduate_project_presentation_template.pptx'
OUTPUT_PATH_1 = '/home/zia/Documents/school/graduation-project/nuada/docs/presentations/Nuada_Bionic_Hand_Project_Proposal_Presentation.pptx'
OUTPUT_PATH_2 = 'docs/presentations/Nuada_Bionic_Hand_Project_Proposal_Presentation.pptx'

prs = pptx.Presentation(TEMPLATE_PATH)

def clear_shape_paragraphs(shape):
    if shape.has_text_frame:
        tf = shape.text_frame
        while len(tf.paragraphs) > 1:
            p = tf.paragraphs[-1]._p
            p.getparent().remove(p)
        tf.paragraphs[0].text = ''

def remove_all_pictures(slide):
    for sh in list(slide.shapes):
        if sh.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
            sp = sh._element
            sp.getparent().remove(sp)

def set_footer(slide, slide_num):
    for sh in slide.shapes:
        if 'Date' in sh.name or 'Veri' in sh.name:
            if sh.has_text_frame:
                sh.text_frame.text = '12.10.2026'
        elif 'Footer' in sh.name or 'Altbilgi' in sh.name:
            if sh.has_text_frame:
                sh.text_frame.text = 'CSE496 – First Presentation'
        elif 'Slide Number' in sh.name or 'Slayt Numarası' in sh.name:
            if sh.has_text_frame:
                sh.text_frame.text = str(slide_num)

print("Building Nuada Presentation...")

# ==========================================================
# SLIDE 1: TITLE SLIDE
# ==========================================================
s1 = prs.slides[0]
for sh in s1.shapes:
    if sh.name == 'Title 1':
        sh.text_frame.text = 'Nuada: Bionic Hand Movement Estimation via TinyML'
        p = sh.text_frame.paragraphs[0]
        p.font.size = Pt(34)
        p.font.bold = True
        p.font.color.rgb = RGBColor(10, 30, 80)
    elif sh.name == 'Subtitle 2':
        tf = sh.text_frame
        tf.clear()
        lines = [
            ('Edge-AI Hand Gesture Classification via Multi-Channel sEMG and IMU Fusion', 17, True, RGBColor(20, 50, 100)),
            ('CSE 496 - Graduation Project Proposal Presentation', 15, False, RGBColor(70, 70, 70)),
            ('', 8, False, RGBColor(0,0,0)),
            ('Researchers: Nuri Ziya Kırtepe & Evrim Doğa Solmaz', 16, True, RGBColor(30, 30, 30)),
            ('Advisor: Asst. Prof. Alp Arslan Bayrakci', 15, False, RGBColor(50, 50, 50)),
            ('Department of Computer Engineering, Gebze Technical University', 13, False, RGBColor(80, 80, 80)),
            ('October 2026', 13, False, RGBColor(100, 100, 100))
        ]
        for idx, (text, sz, bld, col) in enumerate(lines):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = text
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 2: CONTENTS
# ==========================================================
s2 = prs.slides[1]
set_footer(s2, 2)
for sh in s2.shapes:
    if sh.name == 'Title 1':
        sh.text_frame.text = 'Contents'
    elif 'Content' in sh.name:
        tf = sh.text_frame
        tf.clear()
        items = [
            '1. Project Definition & Motivation (Affordable Bionic Hand Control)',
            '2. Project Design & System Architecture (Dual-Core FreeRTOS Pipeline)',
            '3. Hardware Selection & Cost Optimization (AD8232 vs. MyoWare 2.0)',
            '4. Hardware Engineering: AD8232 EKG to sEMG Modification (10x Savings)',
            '5. Circuit Layout Verification & Safe Laboratory Soldering Protocol',
            '6. Project Requirements (Hardware, Software, Subject Protocol)',
            '7. Concrete & Testable Success Criteria (Quantitative Thresholds)',
            '8. Project Timeline & Monthly Milestones (Oct 2026 – Apr 2027)',
            '9. References & Discussion'
        ]
        for idx, item in enumerate(items):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = item
            p.font.size = Pt(16)
            p.font.bold = (idx in [0, 1, 2, 3, 6, 7])

# ==========================================================
# SLIDE 3: PROJECT DEFINITION & MOTIVATION
# ==========================================================
s3 = prs.slides[2]
set_footer(s3, 3)
remove_all_pictures(s3)
s3.shapes.add_picture('docs/presentations/emg_armband_placement.jpg', Inches(0.4), Inches(1.5), width=Inches(5.7), height=Inches(5.2))

for sh in s3.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Project Definition & Motivation'
    elif 'İçerik' in sh.name and sh.left > Inches(5):
        tf = sh.text_frame
        tf.clear()
        points = [
            ('Economic Problem & Need:', True, 15, RGBColor(160, 20, 20)),
            ('Commercial active myoelectric prostheses cost between $10,000 and $50,000, creating an insurmountable economic barrier for over 90% of amputees globally.', False, 13, RGBColor(40, 40, 40)),
            ('Nuada Project Vision:', True, 15, RGBColor(10, 80, 150)),
            ('An ultra-affordable (< $30 total hardware kit), wearable, real-time hand gesture recognition system for bionic hand actuation.', False, 13, RGBColor(40, 40, 40)),
            ('Dual-Sensing Modality (Overcoming Limb Position Drift):', True, 14, RGBColor(20, 100, 40)),
            ('• 4-Channel sEMG: Surface electrodes capture motor unit action potentials from forearm flexor/extensor muscle groups.', False, 12.5, RGBColor(50, 50, 50)),
            ('• 6-Axis IMU on Forearm: Tracks arm elevation (Pitch/Roll) to cancel gravity-induced EMG pattern distortion.', False, 12.5, RGBColor(50, 50, 50)),
            ('Zero Cloud Latency & Standalone Edge Intelligence:', True, 14, RGBColor(110, 40, 140)),
            ('• Quantized TinyML models execute directly on-device on an ESP32-S3 microcontroller (< 25 ms inference time).', False, 12.5, RGBColor(50, 50, 50)),
            ('• 5-Class Functional Gestures: Rest, Power Grasp, Open Hand, Pinch, Point mapped to a 3-finger (Thumb, Index, Middle) bionic hand and WebGL 3D Digital Twin.', False, 12.5, RGBColor(50, 50, 50))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col
    elif 'İçerik' in sh.name and sh.top > Inches(5):
        # hide template lower banner text placeholder
        sh.text_frame.clear()

# ==========================================================
# SLIDE 4: PROJECT DESIGN & SYSTEM ARCHITECTURE
# ==========================================================
s4 = prs.slides[3]
set_footer(s4, 4)
remove_all_pictures(s4)
s4.shapes.add_picture('docs/presentations/system_architecture_diagram.png', Inches(0.3), Inches(1.45), width=Inches(7.3), height=Inches(5.35))

for sh in s4.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Project Design & System Architecture'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('End-to-End System Breakdown:', True, 15, RGBColor(10, 50, 120)),
            ('1. Front-End Acquisition & Sensing Layer:', True, 13.5, RGBColor(0, 120, 150)),
            ('• 4x AD8232 front-ends (1100x gain, modified 410 Hz LPF).', False, 12, RGBColor(40, 40, 40)),
            ('• 1x MPU-6050 6-axis IMU over I2C Fast-Mode (400 kHz).', False, 12, RGBColor(40, 40, 40)),
            ('• Reusable snap armband + medical conductive gel.', False, 12, RGBColor(40, 40, 40)),
            ('2. Dual-Core FreeRTOS Pipeline on ESP32-S3:', True, 13.5, RGBColor(110, 40, 150)),
            ('• Core 0 (Acquisition & DSP Task @ 1000 Hz):', True, 12, RGBColor(60, 60, 60)),
            ('  - 12-bit ADC1 DMA double-buffering.', False, 11.5, RGBColor(50, 50, 50)),
            ('  - 20 Hz HPF + 50 Hz Notch digital filtering.', False, 11.5, RGBColor(50, 50, 50)),
            ('  - 200 ms sliding window feature extraction (MAV, RMS, WL, ZC, WAMP, Pitch/Roll).', False, 11.5, RGBColor(50, 50, 50)),
            ('• Core 1 (TinyML Inference Task @ 20 Hz):', True, 12, RGBColor(60, 60, 60)),
            ('  - Quantized INT8 model inference (TFLite Micro).', False, 11.5, RGBColor(50, 50, 50)),
            ('  - 5-Class gesture classification + majority voting.', False, 11.5, RGBColor(50, 50, 50)),
            ('3. Actuation & Digital Twin Telemetry:', True, 13.5, RGBColor(160, 30, 80)),
            ('• PWM servo driving 3D bionic fingers (Thumb, Index, Middle).', False, 12, RGBColor(40, 40, 40)),
            ('• WebSocket telemetry to Three.js 3D WebGL Digital Twin (< 50 ms).', False, 12, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 5: HARDWARE SELECTION & COST OPTIMIZATION
# ==========================================================
s5 = prs.slides[4]
set_footer(s5, 5)
for sh in s5.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Hardware Selection & Cost Optimization (AD8232 vs MyoWare)'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('1. 10x Front-End Cost Reduction (AD8232 vs. MyoWare 2.0):', True, 15, RGBColor(160, 20, 20)),
            ('• Commercial Standard (MyoWare 2.0): ~$45 / channel -> 4 channels = ~$180 (~6,000 TL), proprietary snap shields, costly replacement.', False, 13, RGBColor(40, 40, 40)),
            ('• Nuada Strategy (AD8232 Breakout): ~$3.50 / channel -> 4 channels = ~$14 (~440 TL). Over 10x cost reduction for equivalent biopotential instrumentation specs!', False, 13, RGBColor(10, 100, 30)),
            ('2. Sensor Fusion Solves Limb Position Bias Without Extra Shoulder Sensors:', True, 15, RGBColor(10, 50, 140)),
            ('• Raising/lowering the arm introduces gravity-induced muscle shift and gesture misclassification.', False, 13, RGBColor(40, 40, 40)),
            ('• Rather than adding 2-4 expensive shoulder EMG sensors ($90-$180), we fuse 1x MPU-6050 6-axis IMU ($2.50) on the forearm, feeding pitch/roll angles into the TinyML feature vector.', False, 13, RGBColor(40, 40, 40)),
            ('3. Sustainable Multi-Subject Protocol (Snap Armband + Gel):', True, 15, RGBColor(110, 40, 140)),
            ('• Disposable medical gel pads cost ~$15 per 50-pack and deplete in 6 subject sessions.', False, 13, RGBColor(40, 40, 40)),
            ('• We custom-built an elastic armband with stainless-steel snap buttons + 250 ml conductive gel tube ($1.50) -> Reusable across 100+ subjects with zero ongoing consumable cost.', False, 13, RGBColor(40, 40, 40)),
            ('4. Standalone Edge Intelligence (ESP32-S3):', True, 15, RGBColor(180, 80, 10)),
            ('• Dual-Core Xtensa LX7 @ 240 MHz + AI vector instructions ($7.50) eliminates external PC or Raspberry Pi ($50-$100).', False, 13, RGBColor(40, 40, 40)),
            ('• COMPLETE HARDWARE KIT COST: Strictly under $30 (~₺950) vs. $300 - $500 commercial standard (> 90% savings!).', True, 13.5, RGBColor(160, 10, 10))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 6: ENGINEERING CHALLENGE: AD8232 MODIFICATION
# ==========================================================
s6 = prs.slides[5]
set_footer(s6, 6)
remove_all_pictures(s6)
s6.shapes.add_picture('docs/ad8232_gercek_kart_haritasi.png', Inches(0.3), Inches(1.45), width=Inches(7.4), height=Inches(5.35))

for sh in s6.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Hardware Engineering: AD8232 EKG to sEMG Modification'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('The Core Engineering Bottleneck:', True, 15, RGBColor(160, 20, 20)),
            ('• AD8232 is factory-tuned for heart ECG with a 0.5 Hz – 40 Hz passband.', False, 12.5, RGBColor(40, 40, 40)),
            ('• Surface EMG spectral power spans 10 Hz – 450 Hz. A 40 Hz filter clips > 90% of motor unit action potentials (MUAP)!', False, 12.5, RGBColor(40, 40, 40)),
            ('Sallen-Key Low-Pass Filter Rework (40 Hz -> 410.9 Hz):', True, 14, RGBColor(10, 100, 30)),
            ('• Theoretical Formula: fc = 1 / (2 * pi * R * sqrt(C1 * C3))', True, 12, RGBColor(20, 50, 120)),
            ('• C3 (0603 SMD / Mercimek 102): 10 nF -> 1.0 nF (Mandatory)', False, 12, RGBColor(40, 40, 40)),
            ('• C1 (0603 SMD / Mercimek 151/221): 1.5 nF -> 150 pF (Mandatory)', False, 12, RGBColor(40, 40, 40)),
            ('• Preserves system gain (1100x) and Q factor while opening the full sEMG bandwidth to 410.9 Hz.', False, 12, RGBColor(40, 40, 40)),
            ('High-Pass Filter Stage (Motion Artifact Rejection):', True, 14, RGBColor(0, 120, 140)),
            ('• C4 & C6 (Large 0805 SMD): 0.33 µF -> 10 nF shifts cutoff from 0.5 Hz to 15.9 Hz.', False, 12, RGBColor(40, 40, 40)),
            ('• Alternatively, kept stock and motion artifacts rejected via software 20 Hz Butterworth HPF on ESP32-S3.', False, 12, RGBColor(40, 40, 40)),
            ('Through-Hole Mercimek Capacitor Innovation:', True, 13.5, RGBColor(110, 40, 140)),
            ('• Unmarked SMD capacitors cause inspection ambiguity. Using leaded capacitors with visible printed codes (\"102\" & \"221\") guarantees 100% visual verification.', False, 12, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 7: CIRCUIT VERIFICATION & LABORATORY PROTOCOL
# ==========================================================
s7 = prs.slides[6]
set_footer(s7, 7)
remove_all_pictures(s7)
s7.shapes.add_picture('docs/ad8232_emg_mod_guide.png', Inches(0.3), Inches(1.45), width=Inches(7.4), height=Inches(5.35))

for sh in s7.shapes:
    if 'Title' in sh.name or 'Unvan' in sh.name:
        sh.text_frame.text = 'Circuit Layout Verification & Laboratory Protocol'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('Eagle CAD Netlist Verification (SparkFun SEN-12650):', True, 15, RGBColor(10, 50, 140)),
            ('• Official schematic & board files cross-verified down to sub-millimeter coordinates.', False, 12.5, RGBColor(40, 40, 40)),
            ('• C4 & C6 verified as the only 0805 (larger) capacitors on the PCB.', False, 12.5, RGBColor(40, 40, 40)),
            ('Multimeter Continuity (BEEP) Verification Protocol:', True, 14, RGBColor(0, 100, 40)),
            ('• Pin 13 (OPAMP+) <-> C3 Pad: Instant 0.0 Ω beep confirms LPF input node.', False, 12, RGBColor(40, 40, 40)),
            ('• OUTPUT Pin <-> C1 Pad: 0.0 Ω beep confirms LPF feedback node.', False, 12, RGBColor(40, 40, 40)),
            ('• Pin 3 (HPDRIVE) <-> C4 Pad: 0.0 Ω beep confirms HPF 1st stage node.', False, 12, RGBColor(40, 40, 40)),
            ('Safe Laboratory Soldering Protocol:', True, 14, RGBColor(160, 20, 20)),
            ('• \"Solder Blob Technique\": Heat both SMD pads simultaneously with a solder bead to slide the component off without tearing copper PCB traces.', False, 12, RGBColor(40, 40, 40)),
            ('• Mechanical Strain Relief: Hot glue anchoring beneath leaded capacitors eliminates mechanical pad peeling.', False, 12, RGBColor(40, 40, 40)),
            ('Experimental Staging Strategy:', True, 14, RGBColor(110, 40, 140)),
            ('• Step 1: Baseline functional test with 3 disposable pads on forearm.', False, 12, RGBColor(40, 40, 40)),
            ('• Step 2: Continuity verification with digital multimeter.', False, 12, RGBColor(40, 40, 40)),
            ('• Step 3: Modify ONLY 1 board as prototype; compare modded (410 Hz) vs. unmodded (40 Hz) waveforms side-by-side on Serial Plotter!', True, 12, RGBColor(160, 10, 10))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 8: PROJECT REQUIREMENTS
# ==========================================================
s8 = prs.slides[7]
set_footer(s8, 8)
for sh in s8.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Project Requirements'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('1. Hardware Components & Instrumentation:', True, 15, RGBColor(10, 50, 140)),
            ('• Microcontroller: ESP32-S3-DevKitC-1 N16R8 (Dual Xtensa LX7 @ 240 MHz, 16 MB Flash, 8 MB PSRAM).', False, 12.5, RGBColor(40, 40, 40)),
            ('• Analog Front-Ends: 4x AD8232 Biopotential Modules (1 modified prototype, 3 comparative).', False, 12.5, RGBColor(40, 40, 40)),
            ('• Inertial Unit: 1x GY-521 MPU-6050 6-Axis IMU Module (I2C Fast-Mode).', False, 12.5, RGBColor(40, 40, 40)),
            ('• Custom Electrodes: Elastic Velcro Armband with 8x Stainless Snap Fasteners + 250 ml Conductive Gel.', False, 12.5, RGBColor(40, 40, 40)),
            ('• Actuation: 3-Finger 3D-Printed Bionic Hand Mechanism + 3x Micro Servos (SG90/MG90S).', False, 12.5, RGBColor(40, 40, 40)),
            ('2. Software Frameworks & Toolchains:', True, 15, RGBColor(0, 100, 40)),
            ('• Embedded: ESP-IDF v5.1 / Arduino-ESP32, FreeRTOS dual-task scheduler, ESP32 ADC1 DMA driver.', False, 12.5, RGBColor(40, 40, 40)),
            ('• TinyML Engine: TensorFlow Lite for Microcontrollers (TFLite Micro) / ESP-DL.', False, 12.5, RGBColor(40, 40, 40)),
            ('• Machine Learning Pipeline: Python 3.10+, PyTorch, Scikit-learn, SciPy (DSP filtering & feature extraction).', False, 12.5, RGBColor(40, 40, 40)),
            ('• 3D Simulation: Three.js / WebGL Web Application with bi-directional WebSocket telemetry.', False, 12.5, RGBColor(40, 40, 40)),
            ('3. Experimental & Laboratory Resources:', True, 15, RGBColor(110, 40, 140)),
            ('• Human Participants: 10 healthy subjects (diverse forearm circumferences) under SENIAM 20 mm protocol.', False, 12.5, RGBColor(40, 40, 40)),
            ('• Electronics Lab: Stereo microscope, temperature-controlled soldering station, digital multimeter, hot glue gun.', False, 12.5, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 9: SUCCESS CRITERIA
# ==========================================================
s9 = prs.slides[8]
set_footer(s9, 9)
for sh in s9.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Concrete & Testable Success Criteria'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('Criterion 1: Gesture Classification Accuracy (Verifiable & Quantitative)', True, 14.5, RGBColor(10, 50, 140)),
            ('• Target: Offline 10-fold cross-validation accuracy >= 90% across 5 gesture classes.', False, 12.5, RGBColor(40, 40, 40)),
            ('• On-device real-time prediction accuracy >= 88% on unseen continuous evaluation trials.', False, 12.5, RGBColor(40, 40, 40)),
            ('Criterion 2: System Latency & Real-Time Control Threshold', True, 14.5, RGBColor(0, 100, 40)),
            ('• Target: On-device TinyML inference time <= 25 ms on ESP32-S3.', False, 12.5, RGBColor(40, 40, 40)),
            ('• Total end-to-end pipeline latency (sampling + DSP + inference + servo command) <= 75 ms (well below human perceptual delay threshold of 100 - 150 ms).', False, 12.5, RGBColor(40, 40, 40)),
            ('Criterion 3: Robustness to Arm Elevation & Orientation (Limb Position Invariance)', True, 14.5, RGBColor(160, 20, 20)),
            ('• Target: Classification accuracy maintained at >= 85% when the arm is positioned at -45°, 0°, and +45° elevation, verified through MPU-6050 sensor fusion.', False, 12.5, RGBColor(40, 40, 40)),
            ('Criterion 4: Power Consumption & Battery Autonomy', True, 14.5, RGBColor(110, 40, 140)),
            ('• Target: Total operating current <= 250 mA @ 3.3V (power <= 0.85 W standby, <= 1.5 W active servo actuation).', False, 12.5, RGBColor(40, 40, 40)),
            ('• Minimum continuous battery runtime >= 6 hours on a single 1200 mAh Li-Po cell.', False, 12.5, RGBColor(40, 40, 40)),
            ('Criterion 5: Hardware Cost & Sustainability Constraint', True, 14.5, RGBColor(180, 80, 10)),
            ('• Target: Total electronic hardware BOM strictly under $30 (~₺950). 100% reusable snap-electrode armband with < 50 kΩ skin-electrode impedance and zero single-use pad waste.', False, 12.5, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 10: PROJECT TIMELINE & GANTT CHART
# ==========================================================
s10 = prs.slides[9]
set_footer(s10, 10)
# Slide 10 in template is Section Header. Let's make it a full content slide.
for sh in list(s10.shapes):
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Project Timeline & Milestone Gantt Chart'
        sh.left = Inches(0.31)
        sh.top = Inches(0.31)
        sh.width = Inches(10.67)
        sh.height = Inches(0.83)
    elif 'Metin' in sh.name:
        sp = sh._element
        sp.getparent().remove(sp)

remove_all_pictures(s10)
s10.shapes.add_picture('docs/presentations/project_timeline_gantt.png', Inches(0.6), Inches(1.4), width=Inches(12.1), height=Inches(5.4))

# ==========================================================
# SLIDE 11: REFERENCES
# ==========================================================
s11 = prs.slides[10]
set_footer(s11, 11)
remove_all_pictures(s11)
for sh in list(s11.shapes):
    if 'Rectangle' in sh.name or 'DİYAGRAM' in sh.name:
        sp = sh._element
        sp.getparent().remove(sp)

# Add title and text box to Slide 11
tb_title = s11.shapes.add_textbox(Inches(0.31), Inches(0.31), Inches(10.67), Inches(0.83))
tb_title.text_frame.text = 'References'
tb_title.text_frame.paragraphs[0].font.size = Pt(28)
tb_title.text_frame.paragraphs[0].font.bold = True

tb_refs = s11.shapes.add_textbox(Inches(0.4), Inches(1.4), Inches(12.5), Inches(5.5))
tf = tb_refs.text_frame
refs = [
    '1. Hermens, H. J., Freriks, B., Disselhorst-Klug, C., & Rau, G., “Development of recommendations for SEMG sensors and sensor placement procedures (SENIAM)”, Journal of Electromyography and Kinesiology, 10(5), 361-374, 2000.',
    '2. Analog Devices Inc., “AD8232: Single-Lead, Heart Rate Monitor Front End Data Sheet”, Rev. A, Analog Devices, Norwood, MA, 2013.',
    '3. SparkFun Electronics, “SparkFun Single Lead Heart Rate Monitor (SEN-12650) Hardware Design Files, Eagle Schematics and Board Layouts”, Open-Source Hardware, 2014.',
    '4. Phinyomark, A., Phukpattaranont, P., & Limsakul, C., “Feature extraction and selection for machine learning with applications to myoelectric signal classification”, International Conference on Biomedical Engineering (ICBME), 2012.',
    '5. Radmand, A., Scheme, E., & Englehart, K., “High-density surface EMG-based gesture classification for prosthetic control: evaluation of limb position and orientation effects”, IEEE Transactions on Neural Systems and Rehabilitation Engineering, 24(7), 808-817, 2016.',
    '6. Warden, P., & Situnayake, D., “TinyML: Machine Learning with TensorFlow Lite on Arduino and Ultra-Low-Power Microcontrollers”, O\'Reilly Media, Sebastopol, CA, 2019.'
]
for idx, r in enumerate(refs):
    p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
    p.text = r
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(40, 40, 40)
    p.space_after = Pt(14)

# ==========================================================
# SLIDE 12: PROJECT SUMMARY
# ==========================================================
s12 = prs.slides[11]
set_footer(s12, 12)
remove_all_pictures(s12)
for sh in list(s12.shapes):
    if 'Title' in sh.name or 'Unvan' in sh.name:
        sh.text_frame.text = 'Project Summary & Core Innovations'
        sh.left = Inches(0.31)
        sh.top = Inches(0.31)
        sh.width = Inches(10.67)
        sh.height = Inches(0.83)
    elif 'Text' in sh.name or 'İçerik' in sh.name:
        sh.left = Inches(0.4)
        sh.top = Inches(1.4)
        sh.width = Inches(12.5)
        sh.height = Inches(5.5)
        tf = sh.text_frame
        tf.clear()
        points = [
            ('Key Innovations of Nuada:', True, 16, RGBColor(10, 50, 140)),
            ('• Ultra-Affordable Bionic Control: Demonstrated feasibility of a strictly < $30 hardware kit replacing $10,000+ commercial prostheses.', False, 13.5, RGBColor(40, 40, 40)),
            ('• Inertial Sensor Fusion: Fusing 4-channel sEMG with 6-axis IMU solves the fundamental limb position problem without adding bulky shoulder sensors.', False, 13.5, RGBColor(40, 40, 40)),
            ('• Hardware Engineering (AD8232 Mod): Converting $3.50 ECG front-ends to 410 Hz sEMG delivers 10x savings over commercial MyoWare sensors.', False, 13.5, RGBColor(10, 100, 30)),
            ('• Sustainable Multi-Subject Protocol: Reusable snap-button armband + conductive gel eliminates consumable waste across 100+ subjects.', False, 13.5, RGBColor(40, 40, 40)),
            ('• Standalone Edge Computing: Dual-core FreeRTOS pipeline on ESP32-S3 guarantees < 25 ms inference with zero cloud dependency.', False, 13.5, RGBColor(40, 40, 40)),
            ('Expected Deliverables:', True, 16, RGBColor(110, 40, 140)),
            ('• Fully functioning 3-finger (Thumb, Index, Middle) 3D-printed bionic hand reacting in real time (< 75 ms end-to-end).', False, 13.5, RGBColor(40, 40, 40)),
            ('• Interactive WebGL 3D Digital Twin simulation accessible from any browser via WebSocket.', False, 13.5, RGBColor(40, 40, 40)),
            ('• Comprehensive academic graduation thesis and comparative benchmark dataset.', False, 13.5, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 13: Q&A / CONCLUSION
# ==========================================================
s13 = prs.slides[12]
set_footer(s13, 13)
remove_all_pictures(s13)
for sh in list(s13.shapes):
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Questions & Discussion'
        sh.left = Inches(0.31)
        sh.top = Inches(0.31)
        sh.width = Inches(10.67)
        sh.height = Inches(0.83)
    elif 'İçerik' in sh.name or 'Metin' in sh.name:
        sh.left = Inches(1.5)
        sh.top = Inches(1.8)
        sh.width = Inches(10.3)
        sh.height = Inches(4.8)
        tf = sh.text_frame
        tf.clear()
        lines = [
            ('Thank You for Your Attention!', True, 28, RGBColor(10, 40, 100)),
            (' ', False, 14, RGBColor(0,0,0)),
            ('Nuada: Bionic Hand Movement Estimation via TinyML', True, 20, RGBColor(20, 50, 120)),
            ('CSE 496 - Graduation Project Proposal', False, 16, RGBColor(80, 80, 80)),
            (' ', False, 10, RGBColor(0,0,0)),
            ('Researchers:', True, 16, RGBColor(40, 40, 40)),
            ('Nuri Ziya Kırtepe (nuriziyak@gmail.com)', False, 15, RGBColor(50, 50, 50)),
            ('Evrim Doğa Solmaz', False, 15, RGBColor(50, 50, 50)),
            (' ', False, 10, RGBColor(0,0,0)),
            ('Advisor: Asst. Prof. Alp Arslan Bayrakci', True, 16, RGBColor(40, 40, 40)),
            ('Department of Computer Engineering, Gebze Technical University', False, 14, RGBColor(80, 80, 80)),
            (' ', False, 14, RGBColor(0,0,0)),
            ('We welcome your questions, feedback, and committee guidance.', True, 16, RGBColor(160, 20, 20))
        ]
        for idx, (txt, bld, sz, col) in enumerate(lines):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col
            p.alignment = PP_ALIGN.CENTER

# Save to both destinations
prs.save(OUTPUT_PATH_1)
prs.save(OUTPUT_PATH_2)
print(f"Successfully generated proposal presentation at:\n  1. {OUTPUT_PATH_1}\n  2. {OUTPUT_PATH_2}")
