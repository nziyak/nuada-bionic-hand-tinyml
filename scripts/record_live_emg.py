#!/usr/bin/env python3
"""
Nuada Bionic Hand - Synchronized 4x sEMG + 1x MPU6050 Live Recorder & Multi-Subject Session Manager
Supports 0°, 45°, and 90° limb position angles, randomized trials to prevent overfitting,
and logs raw labeled datasets for TinyML training.
"""

import os
import sys
import time
import glob
import random
import argparse
from datetime import datetime

try:
    import serial
except ImportError:
    print("[HATA] pyserial kütüphanesi bulunamadı! 'pip install pyserial' çalıştırınız.")
    sys.exit(1)

# Sabitler
ACCEL_SCALE = 8192.0  # LSB / g (±4g)
GYRO_SCALE = 65.5     # LSB / (deg/s) (±500 dps)
CORE_GESTURES = ["rest", "fist", "open_hand", "pinch", "point"]
TARGET_ANGLES = [0, 45, 90]
ANGLE_DESCRIPTIONS = {
    0: "0° (Ön Kol Yatay / Masada Düz)",
    45: "45° (Ön Kol Yarı Eğik / 45 Derece Açı)",
    90: "90° (Ön Kol Dikey / Dirsekten 90 Derece Dik)"
}

def find_serial_port():
    """Detect common ESP32 serial ports on Linux."""
    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
    if not ports:
        return None
    return sorted(ports)[0]

def parse_args():
    parser = argparse.ArgumentParser(description="Nuada Bionic Hand - 4x EMG + MPU6050 Multi-Angle Synchronized Recorder")
    parser.add_argument("port", nargs="?", default=None, help="Seri port (/dev/ttyACM0). Belirtilmezse otomatik bulunur.")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate (varsayılan: 115200)")
    parser.add_argument("-s", "--subject", type=str, default=None, help="Denek kodu/adı (örn: s01, ahmet, test)")
    parser.add_argument("-g", "--gesture", type=str, default="unlabeled", 
                        help="Hareket etiketi (örn: rest, fist, open_hand, pinch, point, wrist_flex)")
    parser.add_argument("-a", "--angle", type=int, default=0, choices=[0, 45, 90],
                        help="Kol açısı (0, 45 veya 90 derece; varsayılan: 0)")
    parser.add_argument("-p", "--posture", type=str, default="neutral",
                        help="Kol duruşu (örn: neutral, pronated; varsayılan: neutral)")
    parser.add_argument("-t", "--trial", type=int, default=1, help="Tekrar/Deneme numarası (varsayılan: 1)")
    parser.add_argument("-d", "--duration", type=float, default=0.0,
                        help="Kayıt süresi (saniye). 0 ise Ctrl+C yapılana kadar kesintisiz kaydeder.")
    parser.add_argument("--trials-per-angle", type=int, default=2,
                        help="Rehberli modda açı başına tekrar sayısı (varsayılan: 2)")
    parser.add_argument("--guided", action="store_true",
                        help="0°, 45° ve 90° açılarında etkileşimli, geri sayımlı çoklu denek protokolünü başlatır.")
    return parser.parse_args()

def make_mini_bar(val, max_val=4095, width=6):
    """Generate a compact ASCII visual bar for terminal."""
    val = max(0, min(val, max_val))
    filled = int((val / max_val) * width)
    return "[" + "=" * filled + " " * (width - filled) + "]"

def record_trial(ser, csv_path, gesture, duration, subject="common", angle=0, posture="neutral", trial_idx=1):
    """
    Kayıt oturumunu çalıştırır ve doğrudan RAW verileri CSV'ye kaydeder.
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    header = (
        "timestamp_iso,elapsed_sec,esp_time_ms,"
        "emg1_raw,emg2_raw,emg3_raw,emg4_raw,"
        "emg1_v,emg2_v,emg3_v,emg4_v,"
        "ax_raw,ay_raw,az_raw,gx_raw,gy_raw,gz_raw,"
        "ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,"
        "gesture_label,angle_deg,posture,subject,trial\n"
    )

    ser.reset_input_buffer()
    with open(csv_path, "w", encoding="utf-8") as f_out:
        f_out.write(header)
        start_time = time.time()
        last_display_time = 0
        record_count = 0

        try:
            while True:
                line = ser.readline().decode("utf-8", errors="replace").strip()
                if not line:
                    continue

                if not line.startswith("DATA,"):
                    if line.startswith("[") or line.startswith("="):
                        print(line)
                    continue

                parts = line.split(",")
                # Format: DATA,time_ms,e1,e2,e3,e4,ax,ay,az,gx,gy,gz
                if len(parts) == 12:
                    try:
                        esp_time_ms = int(parts[1])
                        e1 = int(parts[2])
                        e2 = int(parts[3])
                        e3 = int(parts[4])
                        e4 = int(parts[5])
                        ax = int(parts[6])
                        ay = int(parts[7])
                        az = int(parts[8])
                        gx = int(parts[9])
                        gy = int(parts[10])
                        gz = int(parts[11])

                        # Mühendislik birimleri (Referans/İzleme amaçlı)
                        e1_v = round((e1 * 3.3) / 4095.0, 3)
                        e2_v = round((e2 * 3.3) / 4095.0, 3)
                        e3_v = round((e3 * 3.3) / 4095.0, 3)
                        e4_v = round((e4 * 3.3) / 4095.0, 3)

                        ax_g = round(ax / ACCEL_SCALE, 3)
                        ay_g = round(ay / ACCEL_SCALE, 3)
                        az_g = round(az / ACCEL_SCALE, 3)

                        gx_dps = round(gx / GYRO_SCALE, 2)
                        gy_dps = round(gy / GYRO_SCALE, 2)
                        gz_dps = round(gz / GYRO_SCALE, 2)

                        now = time.time()
                        elapsed = now - start_time
                        iso_now = datetime.now().isoformat()

                        # CSV satırı yaz (RAW değerler aynen korunur)
                        f_out.write(
                            f"{iso_now},{elapsed:.3f},{esp_time_ms},"
                            f"{e1},{e2},{e3},{e4},"
                            f"{e1_v},{e2_v},{e3_v},{e4_v},"
                            f"{ax},{ay},{az},{gx},{gy},{gz},"
                            f"{ax_g},{ay_g},{az_g},{gx_dps},{gy_dps},{gz_dps},"
                            f"{gesture},{angle},{posture},{subject},{trial_idx}\n"
                        )
                        record_count += 1

                        # Terminal görsel barı (~15 Hz)
                        if (now - last_display_time) >= 0.066:
                            last_display_time = now
                            b1 = make_mini_bar(e1)
                            b2 = make_mini_bar(e2)
                            b3 = make_mini_bar(e3)
                            b4 = make_mini_bar(e4)
                            dur_str = f"{duration:4.1f}s" if duration > 0 else " CANLI "
                            disp = (
                                f"\r[{elapsed:4.1f}s/{dur_str}] "
                                f"CH1:{b1} {e1_v:.2f}V | "
                                f"CH2:{b2} {e2_v:.2f}V | "
                                f"CH3:{b3} {e3_v:.2f}V | "
                                f"CH4:{b4} {e4_v:.2f}V | "
                                f"IMU:({ax_g:+4.1f},{ay_g:+4.1f},{az_g:+4.1f})g"
                            )
                            sys.stdout.write(disp)
                            sys.stdout.flush()

                        if duration > 0 and elapsed >= duration:
                            break

                    except ValueError:
                        continue

        except KeyboardInterrupt:
            print("\n[BİLGİ] Kayıt durduruldu (Ctrl+C).")

    print(f"\n[OK] {record_count} satır kaydedildi -> {csv_path}")
    return record_count

def run_guided_protocol(ser, subject, root_data_dir, trials_per_angle=2):
    """
    0°, 45° ve 90° açı durumlarını içeren tam rehberli oturum.
    """
    print("\n" + "="*75)
    print(f"  NUADA ÇOKLU DENEK & ÇOKLU AÇI REHBERLİ KAYIT SİSTEMİ: [{subject.upper()}]")
    print("="*75)
    print("Protokol Tasarımı:")
    print(" • Açılar       : 0° (Yatay), 45° (Yarı Eğik), 90° (Dikey / Dik)")
    print(f" • Hareketler   : {', '.join([g.upper() for g in CORE_GESTURES])}")
    print(f" • Tekrar Sayısı: Her açı için {trials_per_angle} tur")
    print(" • Zamanlama    : 3 sn hazırlık -> 3 sn KASILMA/TUTUŞ -> 3 sn DİNLENME")
    print(" • Overfit Önlem: Hareket sıraları her turda rastgele karıştırılır!")
    print("="*75)

    total_recordings = len(TARGET_ANGLES) * trials_per_angle * len(CORE_GESTURES)
    print(f"Toplam Alınacak Kayıt: {len(TARGET_ANGLES)} açı x {trials_per_angle} tekrar x {len(CORE_GESTURES)} hareket = {total_recordings} dosya.")
    input("\nHazırsanız BAŞLAMAK için [ENTER] tuşuna basınız...")

    current_step = 0
    for angle in TARGET_ANGLES:
        angle_desc = ANGLE_DESCRIPTIONS[angle]
        print("\n" + "#"*75)
        print(f"  >>> KOL AÇISINI DEĞİŞTİRİN: [ {angle_desc.upper()} ] <<<")
        print("#"*75)
        print(f"Lütfen deneğin kolunu {angle_desc} konumuna getirmesini sağlayın.")
        input(f"Kol {angle}° açısına hazırsa DEVAM ETMEK için [ENTER] tuşuna basınız...")

        for trial in range(1, trials_per_angle + 1):
            # Rest hep ilk referanstır; diğer hareketler rastgele karıştırılır (overfitting önlemi)
            active_gestures = [g for g in CORE_GESTURES if g != "rest"]
            random.shuffle(active_gestures)
            round_gestures = ["rest"] + active_gestures

            print(f"\n--- Açı: {angle}° | Tur / Deneme: {trial}/{trials_per_angle} ---")

            for gesture in round_gestures:
                current_step += 1
                print(f"\n[{current_step}/{total_recordings}] Açı: {angle}° | Hareket: >>> {gesture.upper()} <<<")
                print("Hazırlanın: ", end="", flush=True)
                for c in range(3, 0, -1):
                    print(f"{c}... ", end="", flush=True)
                    time.sleep(1.0)
                print("ŞİMDİ TUTUN (KAYIT BAŞLADI)!")

                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                folder = os.path.join(root_data_dir, subject, gesture)
                filename = f"{gesture}_deg{angle}_trial{trial}_{ts}.csv"
                csv_path = os.path.join(folder, filename)

                record_trial(ser, csv_path, gesture=gesture, duration=3.0, 
                             subject=subject, angle=angle, posture="neutral", trial_idx=trial)

                if current_step < total_recordings:
                    print("Dinlenme (Rest): ", end="", flush=True)
                    for c in range(3, 0, -1):
                        print(f"{c}... ", end="", flush=True)
                        time.sleep(1.0)
                    print("Tamam.")

    print("\n" + "="*75)
    print(f"TEBRİKLER! Denek [{subject}] için 0°, 45° ve 90° tüm açılarda kayıtlar tamamlandı!")
    print(f"Kayıtlar: {os.path.join(root_data_dir, subject)}")
    print("="*75)

def main():
    args = parse_args()
    port = args.port if args.port else find_serial_port()
    baudrate = args.baud

    if not port:
        print("[HATA] ESP32 seri portu bulunamadı (/dev/ttyACM* veya /dev/ttyUSB* yok)!")
        print("Lütfen ESP32-S3'ü USB kablosuyla bilgisayara bağlayın.")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        time.sleep(1.0) # ESP32 açılış beklemesi
    except Exception as e:
        print(f"[HATA] Seri porta bağlanılamadı ({port}): {e}")
        print("İpucu: 'sudo chmod 666 /dev/ttyACM0' çalıştırınız.")
        sys.exit(1)

    try:
        if args.guided:
            subject = args.subject if args.subject else input("Lütfen denek kodunu girin (örn: s01): ").strip()
            if not subject:
                subject = "s01"
            run_guided_protocol(ser, subject, data_dir, trials_per_angle=args.trials_per_angle)
        else:
            gesture = args.gesture.lower().strip()
            duration = args.duration
            angle = args.angle
            posture = args.posture.lower().strip()
            subject = args.subject.lower().strip() if args.subject else "common"
            trial = args.trial

            if subject != "common":
                target_dir = os.path.join(data_dir, subject, gesture)
            else:
                target_dir = data_dir

            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{gesture}_deg{angle}_trial{trial}_{timestamp_str}.csv"
            csv_path = os.path.join(target_dir, csv_filename)

            print("\n==========================================================================")
            print("  NUADA - 4x sEMG + MPU6050 EŞ ZAMANLI CANLI VERİ TOPLAMA VE KAYIT SİSTEMİ")
            print("==========================================================================")
            print(f"Seri Port       : {port} @ {baudrate} baud")
            print(f"Denek (Subject) : {subject}")
            print(f"Kol Açısı       : {angle}° ({ANGLE_DESCRIPTIONS.get(angle, '')})")
            print(f"Hedef Hareket   : >> {gesture.upper()} << (Deneme: {trial})")
            if duration > 0:
                print(f"Kayıt Süresi    : {duration:.1f} saniye (Otomatik sonlanacak)")
            else:
                print(f"Kayıt Süresi    : Kesintisiz (Durdurmak için: Ctrl + C)")
            print(f"Kayıt Dosyası   : {csv_path}")
            print("--------------------------------------------------------------------------")

            record_trial(ser, csv_path, gesture=gesture, duration=duration, 
                         subject=subject, angle=angle, posture=posture, trial_idx=trial)
    finally:
        ser.close()

if __name__ == "__main__":
    main()
