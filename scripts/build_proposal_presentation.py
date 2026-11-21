import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
<<<<<<< HEAD
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'docs', 'presentations', 'GTU_graduate_project_presentation_template.pptx')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'docs', 'presentations', 'Nuada_Bionic_Hand_Project_Proposal_Presentation.pptx')

if not os.path.exists(TEMPLATE_PATH):
    print(f"Error: Template not found at {TEMPLATE_PATH}")
    sys.exit(1)
=======
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'docs', 'presentations', 'GTU_graduate_project_presentation_template.pptx')
OUTPUT_PATH_1 = os.path.join(PROJECT_ROOT, 'docs', 'presentations', 'Nuada_Bionic_Hand_Project_Proposal_Presentation.pptx')
OUTPUT_PATH_2 = os.path.join(PROJECT_ROOT, '..', 'docs', 'presentations', 'Nuada_Bionic_Hand_Project_Proposal_Presentation.pptx')
>>>>>>> 5775d284e2f9bdc0a5f85d5fdff7a6f66cceb6d3

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
    has_date = False
    has_foot = False
    has_num = False
    for sh in slide.shapes:
        if 'Date' in sh.name or 'Veri' in sh.name:
            if sh.has_text_frame:
                sh.text_frame.text = '12.10.2026'
                has_date = True
        elif 'Footer' in sh.name or 'Altbilgi' in sh.name:
            if sh.has_text_frame:
                sh.text_frame.text = 'CSE496 – First Presentation'
                has_foot = True
        elif 'Slide Number' in sh.name or 'Slayt Numarası' in sh.name or 'Slayt Numaras' in sh.name:
            if sh.has_text_frame:
                sh.text_frame.text = str(slide_num)
                has_num = True

    # If any footer shape is missing, add cleanly
    if not has_date:
        tb_date = slide.shapes.add_textbox(Inches(10.8), Inches(7.1), Inches(1.15), Inches(0.4))
        tb_date.text_frame.text = '12.10.2026'
        tb_date.text_frame.paragraphs[0].font.size = Pt(10)
        tb_date.text_frame.paragraphs[0].font.color.rgb = RGBColor(120, 120, 120)
    if not has_foot:
        tb_foot = slide.shapes.add_textbox(Inches(1.8), Inches(7.1), Inches(8.7), Inches(0.4))
        tb_foot.text_frame.text = 'CSE496 – First Presentation'
        tb_foot.text_frame.paragraphs[0].font.size = Pt(10)
        tb_foot.text_frame.paragraphs[0].font.color.rgb = RGBColor(120, 120, 120)
    if not has_num:
        tb_num = slide.shapes.add_textbox(Inches(12.0), Inches(7.1), Inches(1.0), Inches(0.4))
        tb_num.text_frame.text = str(slide_num)
        tb_num.text_frame.paragraphs[0].font.size = Pt(10)
        tb_num.text_frame.paragraphs[0].font.color.rgb = RGBColor(120, 120, 120)

print("Building Nuada Presentation with Split Hardware Selection & Cost Optimization Slides...")

# ==========================================================
# INSERT NEW SLIDES: COST OPTIMIZATION & WORK BREAKDOWN
# ==========================================================
# 1. Insert Slide 6 (index 5) = Cost Optimization (Economic Feasibility & Sensor Strategy)
new_slide = prs.slides.add_slide(prs.slide_layouts[1])
slide_elem = prs.slides._sldIdLst[-1]
prs.slides._sldIdLst.remove(slide_elem)
prs.slides._sldIdLst.insert(5, slide_elem)

# 2. Insert Slide 11 (index 10) = Work Breakdown & Team Responsibilities
new_slide_wb = prs.slides.add_slide(prs.slide_layouts[1])
slide_elem_wb = prs.slides._sldIdLst[-1]
prs.slides._sldIdLst.remove(slide_elem_wb)
prs.slides._sldIdLst.insert(10, slide_elem_wb)

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
            '3. Hardware Selection: Microcontroller & Platform Benchmark (Why ESP32-S3?)',
            '4. Cost Optimization: Economic Feasibility & Sensor Strategy (AD8232 vs. MyoWare)',
            '5. Hardware Engineering: AD8232 EKG to sEMG Modification (10x Savings)',
            '6. Circuit Layout Verification & Safe Laboratory Soldering Protocol',
            '7. Project Requirements (Hardware, Software, Subject Protocol)',
            '8. Concrete & Testable Success Criteria (Quantitative Thresholds)',
            '9. Work Breakdown & Team Responsibilities (Symmetrical Embedded/AI Allocation)',
            '10. Project Timeline & Monthly Milestones (Oct 2026 – Apr 2027)',
            '11. References, Project Summary & Discussion'
        ]
        for idx, item in enumerate(items):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = item
            p.font.size = Pt(14)
            p.font.bold = (idx in [0, 1, 2, 3, 4, 7, 8, 9])

# ==========================================================
# SLIDE 3: PROJECT DEFINITION & MOTIVATION
# ==========================================================
s3 = prs.slides[2]
set_footer(s3, 3)
remove_all_pictures(s3)
img_s3 = os.path.join(PROJECT_ROOT, 'docs', 'presentations', 'emg_armband_placement.jpg')
if os.path.exists(img_s3):
    s3.shapes.add_picture(img_s3, Inches(0.4), Inches(1.5), width=Inches(5.7), height=Inches(5.2))

for sh in s3.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Project Definition & Motivation'
    elif 'İçerik' in sh.name and sh.left > Inches(5):
        tf = sh.text_frame
        tf.clear()
        points = [
            ('Economic Problem & Need:', True, 15, RGBColor(160, 20, 20)),
            ('• $10,000 – $50,000 Commercial Prosthesis Cost\n• > 90% Global Accessibility Barrier (Unaffordable)', False, 12.5, RGBColor(40, 40, 40)),
            
            ('Nuada Project Vision:', True, 15, RGBColor(10, 80, 150)),
            ('• Ultra-Affordable (< $30) Complete Hardware Kit\n• Wearable, Standalone & Real-Time Bionic Control', False, 12.5, RGBColor(40, 40, 40)),
            
            ('Dual-Sensing Modality (Anti-Drift Fusion):', True, 14, RGBColor(20, 100, 40)),
            ('• 4-Ch sEMG: Forearm Flexors/Extensors (Motor Intent)\n• 6-Axis IMU: Arm Elevation (Pitch/Roll) — Cancels Gravity Drift', False, 12, RGBColor(50, 50, 50)),
            
            ('Standalone Edge Intelligence (Zero Cloud):', True, 14, RGBColor(110, 40, 140)),
            ('• ESP32-S3 TinyML: INT8 Quantized (< 25 ms Latency)\n• 5 Functional Gestures: Rest, Fist, Open, Pinch, Point\n• Actuation: 3-Finger Bionic Hand + Three.js 3D Digital Twin', False, 12, RGBColor(50, 50, 50)),
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col
    elif 'İçerik' in sh.name and sh.top > Inches(5):
        sh.text_frame.clear()

# ==========================================================
# SLIDE 4: PROJECT DESIGN & SYSTEM ARCHITECTURE
# ==========================================================
s4 = prs.slides[3]
set_footer(s4, 4)
remove_all_pictures(s4)
img_s4 = os.path.join(PROJECT_ROOT, 'docs', 'presentations', 'system_architecture_diagram.png')
if os.path.exists(img_s4):
    s4.shapes.add_picture(img_s4, Inches(0.3), Inches(1.45), width=Inches(7.3), height=Inches(5.35))

for sh in s4.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Project Design & System Architecture'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('End-to-End System Breakdown:', True, 15, RGBColor(10, 50, 120)),
            ('1. Front-End Sensing Layer (Forearm Acquisition):', True, 13.5, RGBColor(0, 120, 150)),
            ('• 4x AD8232 Modules: 1100x Gain, Modified 410.9 Hz sEMG LPF\n• 1x MPU-6050 IMU: I2C Fast-Mode (400 kHz), Pitch & Roll Kinematics\n• Custom Armband: Stainless-Steel Snaps + Reusable Conductive Gel', False, 11.5, RGBColor(40, 40, 40)),
            
            ('2. Dual-Core FreeRTOS Pipeline on ESP32-S3:', True, 13.5, RGBColor(110, 40, 150)),
            ('• Core 0 (DSP & Telemetry Task @ 1000 Hz):\n  - DMA Double-Buffering: Continuous 12-bit ADC1 Sampling\n  - Digital Filter Cascades: 20 Hz HPF + 50 Hz IIR Notch\n  - Sliding Window: 200 ms Window (MAV, RMS, WL, ZC, Pitch/Roll)', False, 11, RGBColor(50, 50, 50)),
            ('• Core 1 (TinyML Engine @ 20 Hz):\n  - TFLite Micro INT8: Hardware-Accelerated Vector Inference\n  - 5-Class Classifier: Real-Time Prediction + Majority Voting', False, 11, RGBColor(50, 50, 50)),
            
            ('3. Dual Actuation & Telemetry:', True, 13.5, RGBColor(160, 30, 80)),
            ('• 3-DOF Physical Hand: PWM Servos (Thumb, Index, Middle)\n• 3D Digital Twin: Real-Time Three.js WebGL via WebSockets (< 50 ms)', False, 11.5, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 5: HARDWARE SELECTION (MICROCONTROLLER BENCHMARK)
# ==========================================================
s5 = prs.slides[4]
set_footer(s5, 5)
for sh in s5.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Hardware Selection: Microcontroller & Platform Benchmark'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('Microcontroller Elimination & Decision Matrix (Why ESP32-S3?):', True, 15, RGBColor(10, 50, 140)),
            
            ('1. 🏆 ESP32-S3 (Xtensa LX7 Dual-Core @ 240 MHz) — Undefeated Winner:', True, 13.5, RGBColor(10, 110, 30)),
            ('• Native AI Vector Acceleration (ESP-NN): Hardware vector instructions for INT8 TFLite Micro\n• Symmetrical Dual-Core FreeRTOS: Core 1 dedicated to hard real-time DMA ADC & TinyML;\n  Core 0 handles soft real-time LwIP Wi-Fi/BLE streaming & MPU-6050 kinematics\n• Continuous DMA ADC1: Deterministic 2000 Hz 4-channel sampling without CPU polling jitter', False, 11.5, RGBColor(40, 40, 40)),
            
            ('2. ❌ Raspberry Pi Pico / Pico W (RP2040) — Eliminated:', True, 13, RGBColor(160, 20, 20)),
            ('• No Hardware FPU: Dual Cortex-M0+ lacks FPU; digital filtering & ML requires slow software emulation\n• Radio Bottleneck: External wireless chip lacks high-throughput deterministic telemetry', False, 11.5, RGBColor(50, 50, 50)),
            
            ('3. ⚠️ Raspberry Pi Pico 2 W (RP2350) — Runner-Up:', True, 13, RGBColor(180, 90, 10)),
            ('• Has FPU/DSP, but concurrent Wi-Fi streaming + real-time TinyML creates severe firmware contention', False, 11.5, RGBColor(50, 50, 50)),
            
            ('4. ❌ Teensy 4.0 / STM32F446RE — Eliminated (Wearable Infeasible):', True, 13, RGBColor(160, 20, 20)),
            ('• Raw 600 MHz M7 Power, but ZERO built-in wireless (Wi-Fi/BLE); bulky external shields & high power draw', False, 11.5, RGBColor(50, 50, 50)),
            
            ('5. ❌ Arduino Nano 33 BLE / Uno — Eliminated:', True, 13, RGBColor(160, 20, 20)),
            ('• Nano 33 BLE restricted to slow BLE (no high-speed UDP/WebSockets); Uno (8-bit) obsolete for TinyML', False, 11.5, RGBColor(50, 50, 50))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 6: COST OPTIMIZATION & ECONOMIC FEASIBILITY
# ==========================================================
s6 = prs.slides[5]
set_footer(s6, 6)
<<<<<<< HEAD
=======
remove_all_pictures(s6)
s6.shapes.add_picture('docs/images/ad8232_gercek_kart_haritasi.png', Inches(0.3), Inches(1.45), width=Inches(7.4), height=Inches(5.35))

>>>>>>> 5775d284e2f9bdc0a5f85d5fdff7a6f66cceb6d3
for sh in s6.shapes:
    if 'Title' in sh.name or 'Unvan' in sh.name:
        sh.text_frame.text = 'Cost Optimization: Economic Feasibility & Sensor Strategy'
    elif 'Content' in sh.name or 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('1. 10x Front-End Cost Reduction (AD8232 vs. MyoWare 2.0):', True, 14.5, RGBColor(160, 20, 20)),
            ('• MyoWare 2.0 Baseline: ~$45 / ch  →  $180 (~₺6,000) for 4 Channels (+ proprietary snap shields)\n• Nuada Strategy (AD8232 Breakout): ~$3.50 / ch  →  $14 (~₺440) for 4 Channels\n• Cost Impact: > 90% Cost Reduction with Equal Biopotential Fidelity (1100x Gain, High CMRR)', False, 11.5, RGBColor(40, 40, 40)),
            
            ('2. Kinematic Anti-Drift Sensor Fusion (Zero Bulky Cords):', True, 14.5, RGBColor(10, 50, 140)),
            ('• Limb Position Challenge: Raising arm shifts muscle synergy patterns, causing false classifications\n• Conventional Fix: 2–4 Expensive Shoulder EMG Sensors ($90–$180) + clumsy shoulder/chest cabling\n• Nuada Solution: 1x Forearm MPU-6050 ($2.50)  →  Cancels gravity drift without shoulder wires', False, 11.5, RGBColor(40, 40, 40)),
            
            ('3. Sustainable Armband (Zero Single-Use Waste):', True, 14.5, RGBColor(110, 40, 140)),
            ('• Disposable Medical Pads: ~$15 / 50-pack (Depleted in only 6 subject sessions)\n• Reusable Snap Band: Elastic Velcro + Stainless Snaps + Conductive Gel ($1.50)  →  100+ Trials', False, 11.5, RGBColor(40, 40, 40)),
            
            ('4. Standalone Microcontroller Edge Intelligence:', True, 14.5, RGBColor(180, 80, 10)),
            ('• ESP32-S3 N16R8 ($7.50): Replaces external PC or Raspberry Pi ($50–$100)\n• COMPLETE HARDWARE KIT: Strictly < $30 (~₺950)  vs.  $300–$500 Commercial Baseline (> 90% Savings!)', True, 12, RGBColor(160, 10, 10))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 7: ENGINEERING CHALLENGE: AD8232 MODIFICATION
# ==========================================================
s7 = prs.slides[6]
set_footer(s7, 7)
remove_all_pictures(s7)
<<<<<<< HEAD
img_s7 = os.path.join(PROJECT_ROOT, 'docs', 'ad8232_gercek_kart_haritasi.png')
if os.path.exists(img_s7):
    s7.shapes.add_picture(img_s7, Inches(0.3), Inches(1.45), width=Inches(7.4), height=Inches(5.35))
=======
s7.shapes.add_picture('docs/images/ad8232_emg_mod_guide.png', Inches(0.3), Inches(1.45), width=Inches(7.4), height=Inches(5.35))
>>>>>>> 5775d284e2f9bdc0a5f85d5fdff7a6f66cceb6d3

for sh in s7.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Hardware Engineering: AD8232 EKG to sEMG Modification'
    elif 'İçerik' in sh.name or 'Content' in sh.name:
        # Reposition text placeholder to the right side of the picture
        sh.left = Inches(7.8)
        sh.top = Inches(1.4)
        sh.width = Inches(5.1)
        sh.height = Inches(5.4)
        tf = sh.text_frame
        tf.clear()
        points = [
            ('The Core Engineering Bottleneck:', True, 14.5, RGBColor(160, 20, 20)),
            ('• Stock AD8232: Factory ECG Bandwidth (0.5 Hz – 40 Hz Passband)\n• sEMG Signal Requirement: 10 Hz – 450 Hz Power Spectrum\n• Problem: 40 Hz Filter Clips > 90% of Motor Unit Action Potentials (MUAP)!', False, 11, RGBColor(40, 40, 40)),
            
            ('Sallen-Key LPF Rework (40 Hz → 410.9 Hz):', True, 14, RGBColor(10, 100, 30)),
            ('• Cutoff Formula: fc = 1 / (2 * π * R * √(C1 * C3))  [R = 100 kΩ]\n• C3 Rework: 10 nF  →  1.0 nF (SMD 0603 / Mercimek "102")\n• C1 Rework: 1.5 nF  →  150 pF (SMD 0603 / Mercimek "151" / "221")\n• Result: Preserves 1100x System Gain & Unlocks Full 410.9 Hz sEMG Band', False, 11, RGBColor(40, 40, 40)),
            
            ('High-Pass Filter Stage (Motion Artifact Rejection):', True, 14, RGBColor(0, 120, 140)),
            ('• C4 & C6 (SMD 0805): 0.33 µF  →  10 nF Shifts HPF Cutoff to 15.9 Hz\n• Software Fallback: 20 Hz 2nd-Order Butterworth HPF on ESP32-S3', False, 11, RGBColor(40, 40, 40)),
            
            ('Ceramic Mercimek Capacitor Innovation:', True, 13.5, RGBColor(110, 40, 140)),
            ('• Unmarked SMD Ambiguity Solved: Leaded Capacitors with Clear "102" & "151" Stamps\n• Academic Rigor: Guarantees 100% Visual Verification for Jury Evaluation', False, 11, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 8: CIRCUIT VERIFICATION & LABORATORY PROTOCOL
# ==========================================================
s8 = prs.slides[7]
set_footer(s8, 8)
remove_all_pictures(s8)
img_s8 = os.path.join(PROJECT_ROOT, 'docs', 'ad8232_emg_mod_guide.png')
if os.path.exists(img_s8):
    s8.shapes.add_picture(img_s8, Inches(0.3), Inches(1.45), width=Inches(7.4), height=Inches(5.35))

for sh in s8.shapes:
    if 'Title' in sh.name or 'Unvan' in sh.name:
        sh.text_frame.text = 'Circuit Layout Verification & Laboratory Protocol'

# Clear any previous dynamically added textboxes on Slide 8
for sh in list(s8.shapes):
    if sh.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.TEXT_BOX and sh.left > Inches(7):
        sp = sh._element
        sp.getparent().remove(sp)

tb_s8 = s8.shapes.add_textbox(Inches(7.8), Inches(1.4), Inches(5.1), Inches(5.4))
tf_s8 = tb_s8.text_frame
points_s8 = [
    ('Eagle CAD Netlist Verification (SparkFun SEN-12650):', True, 14.5, RGBColor(10, 50, 140)),
    ('• Official Schematic & BRD Files Cross-Checked to Sub-Millimeter Traces\n• C4 & C6 Confirmed as the Only Larger 0805 Capacitor Footprints', False, 11, RGBColor(40, 40, 40)),
    
    ('Multimeter Continuity (BEEP) Node Audit:', True, 14, RGBColor(0, 100, 40)),
    ('• Pin 13 (OPAMP+) ↔ C3 Pad: 0.0 Ω Beep (LPF Input Node Confirmed)\n• OUTPUT Pin ↔ C1 Pad: 0.0 Ω Beep (LPF Feedback Node Confirmed)\n• Pin 3 (HPDRIVE) ↔ C4 Pad: 0.0 Ω Beep (HPF Stage-1 Node Confirmed)', False, 11, RGBColor(40, 40, 40)),
    
    ('Safe Laboratory Soldering Protocol:', True, 14, RGBColor(160, 20, 20)),
    ('• Dual-Pad Solder Blob: Reflow Both SMD Pads Simultaneously (Zero Trace Tearing)\n• Strain Relief: Hot-Melt Adhesive Anchoring Prevents Copper Pad Peeling', False, 11, RGBColor(40, 40, 40)),
    
    ('Empirical Staging Strategy:', True, 14, RGBColor(110, 40, 140)),
    ('• Phase 1: Baseline Functional Test with 3 Gel Pads on Forearm\n• Phase 2: DMM Continuity Node Verification\n• Phase 3: Modify 1 Prototype Board → Compare 40 Hz vs. 410 Hz Waveforms Live', True, 11, RGBColor(160, 10, 10))
]
for idx, (txt, bld, sz, col) in enumerate(points_s8):
    p = tf_s8.add_paragraph() if idx > 0 else tf_s8.paragraphs[0]
    p.text = txt
    p.font.size = Pt(sz)
    p.font.bold = bld
    p.font.color.rgb = col

# ==========================================================
# SLIDE 9: PROJECT REQUIREMENTS
# ==========================================================
s9 = prs.slides[8]
set_footer(s9, 9)
for sh in s9.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Project Requirements'
    elif 'İçerik' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('1. Hardware Components & Instrumentation:', True, 14.5, RGBColor(10, 50, 140)),
            ('• Microcontroller: ESP32-S3-DevKitC-1 N16R8 (Dual Xtensa LX7 @ 240 MHz, 16 MB Flash, 8 MB PSRAM)\n• Analog AFE: 4x AD8232 Biopotential Modules (1 Modified Prototype + 3 Scaled Units)\n• Kinematics: 1x GY-521 MPU-6050 6-Axis IMU Module (I2C Fast-Mode 400 kHz)\n• Custom Electrodes: Elastic Velcro Armband (8x Stainless Snaps + 250 ml Conductive Gel)\n• Actuation: 3-Finger 3D-Printed Bionic Hand + 3x Micro Servos (MG90S)', False, 11.5, RGBColor(40, 40, 40)),
            
            ('2. Software Frameworks & Toolchains:', True, 14.5, RGBColor(0, 100, 40)),
            ('• Embedded OS: ESP-IDF / FreeRTOS (Dual-Core Tasks, DMA ADC1 Driver)\n• TinyML Engine: TensorFlow Lite for Microcontrollers (TFLM INT8) + ESP-NN Vector Acceleration\n• Signal Processing: Python (SciPy DSP, Scikit-learn, Hudgins Feature Extraction)\n• Simulation: Three.js / WebGL 3D Digital Twin (Real-Time WebSocket Telemetry)', False, 11.5, RGBColor(40, 40, 40)),
            
            ('3. Experimental & Laboratory Resources:', True, 14.5, RGBColor(110, 40, 140)),
            ('• Subject Cohort: 10 Healthy Right-Hand Dominant Subjects (SENIAM 20 mm IED Protocol)\n• Electronics Lab: Stereo Microscope, Temp-Controlled Soldering, DMM, Serial Plotter', False, 11.5, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 10: SUCCESS CRITERIA
# ==========================================================
s10 = prs.slides[9]
set_footer(s10, 10)
for sh in s10.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Concrete & Testable Success Criteria'
    elif 'İçerik' in sh.name or 'erik' in sh.name or 'Content' in sh.name:
        tf = sh.text_frame
        tf.clear()
        points = [
            ('Criterion 1: Gesture Classification Accuracy (5 Classes) (Nuri Ziya Kırtepe)', True, 13.5, RGBColor(10, 50, 140)),
            ('• Offline 10-Fold Cross-Validation: ≥ 90% Accuracy across Subject Cohort\n• Real-Time On-Device Inference: ≥ 88% Accuracy on Continuous Unseen Live Trials', False, 11, RGBColor(40, 40, 40)),
            
            ('Criterion 2: System Latency & Real-Time Responsiveness (Nuri Ziya Kırtepe)', True, 13.5, RGBColor(0, 100, 40)),
            ('• On-Device TinyML Inference Time: ≤ 25 ms on ESP32-S3 Core 1\n• Total End-to-End Latency: ≤ 75 ms (Sampling + DSP + ML + Servo) — Below Human Threshold (100–150 ms)', False, 11, RGBColor(40, 40, 40)),
            
            ('Criterion 3: Limb Position Invariance (Anti-Gravity Robustness) (Evrim Doğa Solmaz)', True, 13.5, RGBColor(160, 20, 20)),
            ('• Arm Elevation Invariance: ≥ 85% Accuracy maintained at -45°, 0°, and +45° Positions\n• Sensor Fusion Verification: Pitch/Roll Angles Fused into TinyML Feature Vector via MPU-6050', False, 11, RGBColor(40, 40, 40)),
            
            ('Criterion 4: Power Consumption & Battery Autonomy (Evrim Doğa Solmaz)', True, 13.5, RGBColor(110, 40, 140)),
            ('• Operating Current: ≤ 250 mA @ 3.3V (Standby: ≤ 0.85 W, Active Servos: ≤ 1.5 W)\n• Continuous Battery Runtime: ≥ 6 Hours on a Single 1200 mAh Li-Po Cell', False, 11, RGBColor(40, 40, 40)),
            
            ('Criterion 5: Hardware Cost & Environmental Sustainability (Joint: Nuri Ziya Kırtepe & Evrim Doğa Solmaz)', True, 13.5, RGBColor(180, 80, 10)),
            ('• Total Electronics BOM: Strictly < $30 (~₺950)\n• Sustainable Electrodes: 100% Reusable Snap Armband (< 50 kΩ Impedance, Zero Single-Use Pad Waste)', False, 11, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 11: WORK BREAKDOWN & TEAM RESPONSIBILITIES
# ==========================================================
s11 = prs.slides[10]
set_footer(s11, 11)
remove_all_pictures(s11)
for sh in list(s11.shapes):
    if 'İçerik' in sh.name or 'Content' in sh.name or 'erik' in sh.name or 'Metin' in sh.name:
        sp = sh._element
        sp.getparent().remove(sp)

for sh in s11.shapes:
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Work Breakdown & Team Responsibilities'
        sh.left = Inches(0.4)
        sh.top = Inches(0.28)
        sh.width = Inches(12.5)
        sh.height = Inches(0.85)
        p = sh.text_frame.paragraphs[0]
        p.font.size = Pt(25)
        p.font.bold = True
        p.font.color.rgb = RGBColor(10, 30, 80)
        p2 = sh.text_frame.add_paragraph()
        p2.text = 'Symmetrical Engineering Allocation Across ESP32-S3 Dual-Core FreeRTOS, TinyML & Hardware Pipelines'
        p2.font.size = Pt(11.5)
        p2.font.italic = True
        p2.font.color.rgb = RGBColor(90, 90, 90)

# Card 1 (Left): Nuri Ziya Kırtepe
rect1 = s11.shapes.add_shape(pptx.enum.shapes.MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(1.22), Inches(6.1), Inches(4.88))
rect1.fill.solid()
rect1.fill.fore_color.rgb = RGBColor(246, 249, 254)
rect1.line.color.rgb = RGBColor(185, 205, 235)
rect1.line.width = Pt(1.2)
tf1 = rect1.text_frame
tf1.word_wrap = True
tf1.margin_left = Inches(0.22)
tf1.margin_right = Inches(0.22)
tf1.margin_top = Inches(0.14)
tf1.margin_bottom = Inches(0.12)

lines1 = [
    ('👤 Nuri Ziya Kırtepe', True, 13.5, RGBColor(10, 40, 110), 0),
    ('Specialization: High-Speed Sampling, Hard Real-Time OS & Deep TinyML', False, 9.5, RGBColor(70, 70, 70), 5),
    
    ('1. Hard Real-Time OS & Embedded Drivers (ESP32-S3 Core 1):', True, 10.5, RGBColor(10, 50, 140), 2),
    ('• Continuous DMA ADC1 Driver: 2000 Hz 4-ch deterministic acquisition (ping-pong ring buffer)', False, 9, RGBColor(40, 40, 40), 1),
    ('• Hard Real-Time Tasks: vTaskEMGSampling & vTaskTinyMLInference pinned to Core 1', False, 9, RGBColor(40, 40, 40), 1),
    ('• ISR Synchronization: xTaskNotifyFromISR wakeups triggered by DMA buffer-ready interrupts', False, 9, RGBColor(40, 40, 40), 1),
    ('• Inter-Core IPC: Co-develops thread-safe FreeRTOS Queues streaming windows to Core 0', False, 9, RGBColor(40, 40, 40), 5),
    
    ('2. Edge-AI & Machine Learning Engine:', True, 10.5, RGBColor(10, 50, 140), 2),
    ('• Deep TinyML: Quantized 1D-CNN temporal classifier via TensorFlow Lite Micro (TFLM)', False, 9, RGBColor(40, 40, 40), 1),
    ('• Vector Acceleration: Espressif ESP-NN vector instructions for sub-25 ms hardware inference', False, 9, RGBColor(40, 40, 40), 1),
    ('• Model Profiling: INT8 post-training quantization, Tensor Arena & heap memory optimization', False, 9, RGBColor(40, 40, 40), 5),
    
    ('3. Primary Success Criteria & Milestones Ownership:', True, 10.5, RGBColor(10, 50, 140), 2),
    ('• Criterion 1: Gesture Classification Accuracy (≥ 90% CV, ≥ 88% live on-device trials)', True, 9.5, RGBColor(10, 50, 140), 1),
    ('• Criterion 2: System Latency & Real-Time Responsiveness (≤ 25 ms Core 1 inference)', True, 9.5, RGBColor(0, 100, 40), 1),
    ('• Electrode Routing & Cohort: Multi-channel signal routing and automated subject data logging', False, 9, RGBColor(60, 60, 60), 0)
]
for idx, (txt, bld, sz, col, sa) in enumerate(lines1):
    p = tf1.add_paragraph() if idx > 0 else tf1.paragraphs[0]
    p.text = txt
    p.font.size = Pt(sz)
    p.font.bold = bld
    p.font.color.rgb = col
    p.space_after = Pt(sa)

# Card 2 (Right): Evrim Doğa Solmaz
rect2 = s11.shapes.add_shape(pptx.enum.shapes.MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.22), Inches(6.1), Inches(4.88))
rect2.fill.solid()
rect2.fill.fore_color.rgb = RGBColor(248, 246, 254)
rect2.line.color.rgb = RGBColor(215, 195, 235)
rect2.line.width = Pt(1.2)
tf2 = rect2.text_frame
tf2.word_wrap = True
tf2.margin_left = Inches(0.22)
tf2.margin_right = Inches(0.22)
tf2.margin_top = Inches(0.14)
tf2.margin_bottom = Inches(0.12)

lines2 = [
    ('👤 Evrim Doğa Solmaz', True, 13.5, RGBColor(90, 25, 120), 0),
    ('Specialization: Real-Time DSP Filters, Kinematic Fusion, Soft Real-Time OS & Telemetry', False, 9.5, RGBColor(70, 70, 70), 5),
    
    ('1. Soft Real-Time OS & Communication Layer (ESP32-S3 Core 0):', True, 10.5, RGBColor(90, 25, 120), 2),
    ('• Periodic RTOS Tasks: vTaskIMUSampling (100 Hz via vTaskDelayUntil) & vTaskTelemetry', False, 9, RGBColor(40, 40, 40), 1),
    ('• Wireless Networking Stack: FreeRTOS LwIP network tasks for low-latency Wi-Fi UDP / BLE', False, 9, RGBColor(40, 40, 40), 1),
    ('• Cross-Core IPC Consumer: Thread-safe queue receiver feeding DSP filter & telemetry pipelines', False, 9, RGBColor(40, 40, 40), 1),
    ('• Power Management: FreeRTOS tickless idle & low-power wireless telemetry scheduling', False, 9, RGBColor(40, 40, 40), 5),
    
    ('2. Embedded DSP & Kinematic Sensor Fusion:', True, 10.5, RGBColor(90, 25, 120), 2),
    ('• Embedded DSP Filters: Real-time C++ IIR bandpass (20–450 Hz) and 50 Hz notch cascades', False, 9, RGBColor(40, 40, 40), 1),
    ('• IMU Kinematic Fusion: I2C MPU-6050 driver + Complementary/Madgwick Pitch & Roll filter', False, 9, RGBColor(40, 40, 40), 1),
    ('• Feature ML Engine: Real-time Hudgins extractor (MAV, RMS, WL, ZC) + C SVM classifier (emlearn)', False, 9, RGBColor(40, 40, 40), 5),
    
    ('3. Primary Success Criteria & Milestones Ownership:', True, 10.5, RGBColor(90, 25, 120), 2),
    ('• Criterion 3: Limb Position Invariance (≥ 85% accuracy across -45° to +45° arm elevation)', True, 9.5, RGBColor(160, 20, 20), 1),
    ('• Criterion 4: Power Consumption & Battery Autonomy (≤ 250 mA current, ≥ 6h runtime)', True, 9.5, RGBColor(110, 40, 140), 1),
    ('• Digital Twin Simulation: Low-latency Three.js WebGL 3D hand telemetry (< 50 ms)', False, 9, RGBColor(60, 60, 60), 0)
]
for idx, (txt, bld, sz, col, sa) in enumerate(lines2):
    p = tf2.add_paragraph() if idx > 0 else tf2.paragraphs[0]
    p.text = txt
    p.font.size = Pt(sz)
    p.font.bold = bld
    p.font.color.rgb = col
    p.space_after = Pt(sa)

# Card 3 (Bottom): Joint Responsibilities
rect_joint = s11.shapes.add_shape(pptx.enum.shapes.MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(6.18), Inches(12.5), Inches(0.78))
rect_joint.fill.solid()
rect_joint.fill.fore_color.rgb = RGBColor(245, 248, 245)
rect_joint.line.color.rgb = RGBColor(175, 210, 185)
rect_joint.line.width = Pt(1.2)
tfj = rect_joint.text_frame
tfj.word_wrap = True
tfj.margin_left = Inches(0.2)
tfj.margin_right = Inches(0.2)
tfj.margin_top = Inches(0.08)
tfj.margin_bottom = Inches(0.08)

lines_joint = [
    ('🤝 Collaborative Subsystems & Joint Engineering Milestones:', True, 10.5, RGBColor(15, 90, 40), 1),
    ('• Criterion 5 (Hardware Cost & Sustainability): Total BOM strictly < $30 (~₺950) | Reusable snap armband with conductive gel (< 50 kΩ)', True, 9.2, RGBColor(180, 80, 10), 1),
    ('• Experimental Protocol & Thesis: SENIAM-compliant 10-subject cohort trials (20 mm IED), physical 3D hand assembly, & CSE 496 Capstone Thesis', False, 9, RGBColor(50, 50, 50), 0)
]
for idx, (txt, bld, sz, col, sa) in enumerate(lines_joint):
    p = tfj.add_paragraph() if idx > 0 else tfj.paragraphs[0]
    p.text = txt
    p.font.size = Pt(sz)
    p.font.bold = bld
    p.font.color.rgb = col
    p.space_after = Pt(sa)

# ==========================================================
# SLIDE 12: PROJECT TIMELINE & GANTT CHART
# ==========================================================
s12 = prs.slides[11]
set_footer(s12, 12)
for sh in list(s12.shapes):
    if 'Unvan' in sh.name or 'Title' in sh.name:
        sh.text_frame.text = 'Project Timeline & Milestone Gantt Chart'
        sh.left = Inches(0.31)
        sh.top = Inches(0.31)
        sh.width = Inches(10.67)
        sh.height = Inches(0.83)
    elif 'Metin' in sh.name:
        sp = sh._element
        sp.getparent().remove(sp)

remove_all_pictures(s12)
img_s12 = os.path.join(PROJECT_ROOT, 'docs', 'presentations', 'project_timeline_gantt.png')
if os.path.exists(img_s12):
    s12.shapes.add_picture(img_s12, Inches(0.6), Inches(1.4), width=Inches(12.1), height=Inches(5.4))

# ==========================================================
# SLIDE 13: REFERENCES
# ==========================================================
s13 = prs.slides[12]
set_footer(s13, 13)
remove_all_pictures(s13)
for sh in list(s13.shapes):
    if sh.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.TEXT_BOX or 'Rectangle' in sh.name or 'DİYAGRAM' in sh.name:
        sp = sh._element
        sp.getparent().remove(sp)

tb_title = s13.shapes.add_textbox(Inches(0.31), Inches(0.31), Inches(10.67), Inches(0.83))
tb_title.text_frame.text = 'References'
tb_title.text_frame.paragraphs[0].font.size = Pt(28)
tb_title.text_frame.paragraphs[0].font.bold = True

tb_refs = s13.shapes.add_textbox(Inches(0.4), Inches(1.4), Inches(12.5), Inches(5.5))
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
# SLIDE 14: PROJECT SUMMARY
# ==========================================================
s14 = prs.slides[13]
set_footer(s14, 14)
remove_all_pictures(s14)
for sh in list(s14.shapes):
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
            ('Key Innovations of Nuada:', True, 15, RGBColor(10, 50, 140)),
            ('• Ultra-Affordable Bionic Control: Strictly < $30 Complete Kit Disrupting $10,000+ Market\n• Hardware Selection (ESP32-S3): Vector AI instructions & dual-core FreeRTOS outperforming Pico/Teensy\n• Kinematic Sensor Fusion: 4-Ch sEMG + Forearm IMU Eliminates Gravitational Drift\n• Hardware Rework (AD8232 Mod): $3.50 ECG to 410.9 Hz sEMG Delivers 10x Cost Savings\n• Sustainable Multi-Subject Armband: Reusable Snaps + Gel (100+ Trials, Zero Pad Waste)\n• Standalone Edge Computing: Dual-Core FreeRTOS on ESP32-S3 (< 25 ms, Zero Cloud)', False, 11.5, RGBColor(40, 40, 40)),
            
            ('Expected Deliverables:', True, 15, RGBColor(110, 40, 140)),
            ('• Physical Bionic Hand: Real-Time 3-Finger Reaction (< 75 ms End-to-End Latency)\n• 3D Digital Twin: Interactive Three.js WebGL Simulation via Real-Time WebSockets\n• Academic Thesis: Comprehensive CSE 496 Capstone Report & Benchmark Dataset', False, 12, RGBColor(40, 40, 40))
        ]
        for idx, (txt, bld, sz, col) in enumerate(points):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = txt
            p.font.size = Pt(sz)
            p.font.bold = bld
            p.font.color.rgb = col

# ==========================================================
# SLIDE 15: Q&A / CONCLUSION
# ==========================================================
s15 = prs.slides[14]
set_footer(s15, 15)
remove_all_pictures(s15)
for sh in list(s15.shapes):
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

# Save presentation
prs.save(OUTPUT_PATH)
print(f"Successfully generated 15-slide proposal presentation at:\n  {OUTPUT_PATH}")
