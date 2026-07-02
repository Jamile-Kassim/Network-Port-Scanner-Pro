import time
from scanner import run_scan
from utils import save_results

ip = "127.0.0.1"
start_port = 1
end_port = 1000

start = time.perf_counter()

open_ports = run_scan(ip, start_port, end_port)

end = time.perf_counter()
scan_time = end - start

results = {
    "ip": ip,
    "scan_time_seconds": round(scan_time, 2),
    "open_ports": open_ports
}

file_path = save_results("scan_results.json", results)

print(f"\nScan took {scan_time:.2f} seconds")
print(f"Results saved to: {file_path}")