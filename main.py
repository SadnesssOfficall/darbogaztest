import argparse
import shutil
import subprocess
import time
import psutil
import csv
from datetime import datetime
from colorama import Fore, Style, init


init(autoreset=True)

def renkli_yuzde(val):
    """Yüzde değerlerini renklendir."""
    if val >= 85:
        return Fore.RED + f"{val:.1f}%" + Style.RESET_ALL
    elif val >= 50:
        return Fore.YELLOW + f"{val:.1f}%" + Style.RESET_ALL
    else:
        return Fore.GREEN + f"{val:.1f}%" + Style.RESET_ALL

def has_nvidia_smi():
    return shutil.which("nvidia-smi") is not None

def read_gpu_stats():
    if not has_nvidia_smi():
        return None
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,memory.total",
            "--format=csv,noheader,nounits",
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
        first_line = out.splitlines()[0]
        parts = [p.strip() for p in first_line.split(",")]
        if len(parts) >= 3:
            gpu_util = float(parts[0])
            vram_used = float(parts[1])
            vram_total = float(parts[2])
            return gpu_util, vram_used, vram_total
    except Exception:
        return None
    return None

def detect_bottleneck(cpu_vals, ram_vals, gpu_vals):
    cpu_high = sum(1 for v in cpu_vals if v > 85) / len(cpu_vals) * 100
    ram_high = sum(1 for v in ram_vals if v > 85) / len(ram_vals) * 100
    gpu_high = sum(1 for v in gpu_vals if v > 85) / len(gpu_vals) * 100 if gpu_vals else 0

    results = []
    if cpu_high >= 40:
        results.append(f"CPU darboğazı (%{cpu_high:.1f} süre yüksek kullanım)")
    if ram_high >= 40:
        results.append(f"RAM darboğazı (%{ram_high:.1f} süre yüksek kullanım)")
    if gpu_vals and gpu_high >= 40:
        results.append(f"GPU darboğazı (%{gpu_high:.1f} süre yüksek kullanım)")

    if not results:
        results.append("Belirgin darboğaz yok")
    return results

parser = argparse.ArgumentParser(description="Darboğaz testi ve log kaydı")
parser.add_argument("--duration", type=int, default=60, help="Test süresi (sn)")
parser.add_argument("--interval", type=float, default=1.0, help="Örnekleme aralığı (sn)")
parser.add_argument("--log", type=str, default="test_log.csv", help="Log dosyası adı")
args = parser.parse_args()

duration = args.duration
interval = args.interval
start_time = time.time()

cpu_vals, ram_vals, gpu_vals = [], [], []

print(Fore.CYAN + f"Test başlıyor... Süre: {duration}s\n" + Style.RESET_ALL)

# CSV başlat
with open(args.log, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Zaman", "CPU (%)", "RAM (%)", "GPU (%)", "VRAM Kullanılan (MB)", "VRAM Toplam (MB)"])

    while time.time() - start_time < duration:
        elapsed = int(time.time() - start_time)
        remaining = duration - elapsed

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        gpu_info = read_gpu_stats()

        zaman = datetime.now().isoformat(timespec="seconds")

        if gpu_info:
            gpu_util, vram_used, vram_total = gpu_info
            print(f"[{elapsed:02d}s | Kalan: {remaining:02d}s] CPU: {renkli_yuzde(cpu)} | RAM: {renkli_yuzde(ram)} | GPU: {renkli_yuzde(gpu_util)} | VRAM: {vram_used:.0f}/{vram_total:.0f} MB")
            gpu_vals.append(gpu_util)
            writer.writerow([zaman, f"{cpu:.1f}", f"{ram:.1f}", f"{gpu_util:.1f}", f"{vram_used:.0f}", f"{vram_total:.0f}"])
        else:
            print(f"[{elapsed:02d}s | Kalan: {remaining:02d}s] CPU: {renkli_yuzde(cpu)} | RAM: {renkli_yuzde(ram)}")
            writer.writerow([zaman, f"{cpu:.1f}", f"{ram:.1f}", "", "", ""])

        cpu_vals.append(cpu)
        ram_vals.append(ram)

        time.sleep(interval)

# Test bittiğinde sonuçlar
print(Fore.MAGENTA + "\n--- TEST BİTTİ ---" + Style.RESET_ALL)
cpu_avg = sum(cpu_vals) / len(cpu_vals)
ram_avg = sum(ram_vals) / len(ram_vals)
print(f"CPU Ortalama: {renkli_yuzde(cpu_avg)}")
print(f"RAM Ortalama: {renkli_yuzde(ram_avg)}")
if gpu_vals:
    gpu_avg = sum(gpu_vals) / len(gpu_vals)
    print(f"GPU Ortalama: {renkli_yuzde(gpu_avg)}")

# Darboğaz tespiti
bottlenecks = detect_bottleneck(cpu_vals, ram_vals, gpu_vals)
print(Fore.CYAN + "\n--- DARBOĞAZ ANALİZİ ---" + Style.RESET_ALL)
for b in bottlenecks:
    renk = Fore.RED if "darboğaz" in b else Fore.GREEN
    print(renk + f"- {b}" + Style.RESET_ALL)

# Log dosyasına yaz
with open(args.log, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([])
    writer.writerow(["--- DARBOĞAZ ANALİZİ ---"])
    for b in bottlenecks:
        writer.writerow([b])

print(Fore.GREEN + f"\n📄 Log dosyası oluşturuldu: {args.log}" + Style.RESET_ALL)
