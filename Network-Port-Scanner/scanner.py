import socket
from concurrent.futures import ThreadPoolExecutor
from services import SERVICES
import threading

checked = 0
lock = threading.Lock()
open_ports = []

def scan_port(port, ip, total_ports, progress_callback, result_callback):
    global checked

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)

    result = s.connect_ex((ip, port))

    if result == 0:
        service = SERVICES.get(port, "Unknown")

        open_ports.append({
            "port": port,
            "service": service
        })

        if result_callback:
            result_callback(port, service)

    s.close()

    with lock:
        checked += 1
        progress_value = (checked / total_ports) * 100

        # send progress to GUI (NOT direct UI update)
        if progress_callback:
            progress_callback(progress_value)


def run_scan(ip, start_port, end_port, progress_callback=None, result_callback=None, max_workers=100):
    global checked, open_ports

    checked = 0
    open_ports = []

    total_ports = end_port - start_port + 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for port in range(start_port, end_port + 1):
            executor.submit(scan_port, port, ip, total_ports, progress_callback, result_callback)

    return open_ports