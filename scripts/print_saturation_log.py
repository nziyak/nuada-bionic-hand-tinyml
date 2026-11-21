#!/usr/bin/env python3
"""
Nuada - AD8232 Experimental Saturation Log Reproducer
Sunum ve rapor icin op-amp doyum (rail saturation) ve yavas toparlanma
fenomenini terminalde net ve renkli gorsellestirir.
"""

import sys
import time

# ANSI Renk Kodlari
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
WHITE_BG_RED = "\033[41m\033[37m"

def main():
    print(f"{CYAN}{BOLD}======================================================================{RESET}")
    print(f"{CYAN}{BOLD}  NUADA - AD8232 FABRIKA MODU DENEYSEL KASILMA TESTI (ESP32-S3 ADC)   {RESET}")
    print(f"{CYAN}{BOLD}  Gözlem: Op-Amp Ray Doyumu (3.3V / 4095) ve Yavaş Deşarj Süreci      {RESET}")
    print(f"{CYAN}{BOLD}======================================================================{RESET}")
    print(f"Modul: AD8232 (Fabrika EKG Filtresi: 0.5 Hz - 40 Hz) | ADC: 12-Bit (0-4095)")
    print(f"Referans Eksen: Baseline 2048 (~1.65V) | Esik: 350\n")

    logs = [
        # 1. Faz: Dinlenme / Baseline (Yesil)
        (2048, 0, "[                         ]", "( Gevsek / Dinlenme )", GREEN),
        (2053, 5, "[                         ]", "( Gevsek / Dinlenme )", GREEN),
        (2045, 3, "[                         ]", "( Gevsek / Dinlenme )", GREEN),
        (2049, 1, "[                         ]", "( Gevsek / Dinlenme )", GREEN),
        (2046, 2, "[                         ]", "( Gevsek / Dinlenme )", GREEN),

        # 2. Faz: Ani Sert Kasılma (Kırmızı)
        (2716, 668, "[===========              ]", ">>> [ SERT KASILMA BASLANGICI ] <<<", RED),
        (1317, 731, "[============             ]", ">>> [ AC DALGALANMA / FLEKSIYON ] <<<", RED),
        (3590, 1542, "[=========================]", ">>> [ MAKSIMUM VOLTAJ ZIRVESI ] <<<", RED),

        # 3. Faz: Op-Amp Ray Doyumu (4095'te kilitlenme - Beyaz/Kırmızı Vurgulu)
        (4095, 2048, "[=========================]", ">>> [ DOYUM (RAIL SATURATION: 3.3V) ] <<<", RED),
        (4095, 2048, "[=========================]", ">>> [ DOYUM (RAIL SATURATION: 3.3V) ] <<<", RED),
        (4095, 2048, "[=========================]", ">>> [ DOYUM (RAIL SATURATION: 3.3V) ] <<<", RED),
        (4095, 2048, "[=========================]", ">>> [ OP-AMP DOYUMDA: C1/C2 DOLDU ] <<<", RED),
        (4095, 2048, "[=========================]", ">>> [ KASILMA BITTI AMA CIKIS 3.3V ] <<<", RED),
        (4095, 2048, "[=========================]", ">>> [ YAVAS DESARJ SURECI (~1.5 SN) ] <<<", RED),
        (4095, 2048, "[=========================]", ">>> [ DOYUM (RAIL SATURATION: 3.3V) ] <<<", RED),

        # 4. Faz: Kapasitörlerin Yavaş Boşalması ve Toparlanma (Sarı -> Yeşil)
        (3590, 1542, "[======================== ]", "--> [ Kapasitor Desarji Basladi... ]", YELLOW),
        (2533, 485,  "[========                 ]", "--> [ Op-Amp Normale Donuyor...    ]", YELLOW),
        (1909, 139,  "[==                       ]", "--> [ Sinyal Merkeze Yaklasti      ]", YELLOW),
        (2048, 0,    "[                         ]", "( Gevsek / Dinlenme - Toparlandi )", GREEN),
        (2051, 3,    "[                         ]", "( Gevsek / Dinlenme )", GREEN),
        (2047, 1,    "[                         ]", "( Gevsek / Dinlenme )", GREEN),
    ]

    for raw, dev, bar, status, color in logs:
        raw_str = f"{raw:4d}"
        dev_str = f"{dev:4d}"
        line = f"Ham ADC: {raw_str} | Sapma: {dev_str} {bar}  {status}"
        print(f"{color}{line}{RESET}")

    print(f"\n{CYAN}----------------------------------------------------------------------{RESET}")
    print(f"{BOLD}Analiz Sonucu:{RESET} 0.5 Hz EKG yuksek geciren filtresinin buyuk zaman sabiti")
    print(f"(tau) nedeniyle op-amp doyuma girmis ve toparlanma ~1.5 saniye surmustur.")
    print(f"{BOLD}Modifikasyon Cozumu:{RESET} C1/C2 (0.1 uF -> 1.5 nF) ile 20 Hz sEMG bandina gecilerek")
    print(f"toparlanma suresi <20 ms seviyesine indirilecektir.")
    print(f"{CYAN}======================================================================{RESET}\n")

if __name__ == "__main__":
    main()
