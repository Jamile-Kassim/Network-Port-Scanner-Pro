import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
from scanner import run_scan
import json

latest_results = []

# Helper Functions
def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg="grey")

    def on_focus_in(_):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def on_focus_out(_):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def update_progress(value):
    progress.config(value=value)


def add_result(port, service):
    results_box.insert("", tk.END, values=(port, service, "OPEN ✔"))


def set_button_state(enabled: bool):
    if enabled: 
        scan_button.config(state="normal")
    else:
        scan_button.config(state="disabled")

def show_status(msg, color="green"):
    status_label.after(0, lambda: status_label.config(text=msg, fg=color))

def export_results():
    if not latest_results:
        status_label.config(text="No scan results to export.", fg="red")
        return

    filename = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")]
    )

    if not filename:
        return

    data = {
        "results": latest_results
    }

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    status_label.config(
        text=f"Results exported to {filename} ✔",
        fg="green"
    )
    
# Main function
def scan_thread():

    ip = ip_entry.get().strip()
    start = start_entry.get().strip()
    end = end_entry.get().strip()

    # Reset status message
    status_label.after(0, lambda: status_label.config(text=""))

    # Reset previous results
    results_box.after(0, lambda: results_box.delete(*results_box.get_children()))

    # validation: empty fields
    if not ip or not start or not end:
        show_status("Please fill in all fields.", "red")
        return

    # validation: numeric ports
    if not start.isdigit() or not end.isdigit():
        show_status("Ports must be numbers only.", "red")
        return

    start_port = int(start)
    end_port = int(end)

    # validation: logic check
    if start_port < 1 or end_port > 65535:
        show_status("Ports must be between 1–65535.", "red")
        return

    if start_port > end_port:
        show_status("Start port must be ≤ end port.", "red")
        return

    # Disable button
    scan_button.after(0, set_button_state, False)

    progress["value"] = 0

    results = run_scan(
        ip,
        start_port,
        end_port,
        progress_callback=lambda v: progress.after(0, update_progress, v),
        result_callback=lambda p, s: results_box.after(0, add_result, p, s)
    )

    # Save latest scan info
    global latest_results
    latest_results = results

    # Scan complete message
    show_status("Scan Complete ✔")
    
    # Enable button
    scan_button.after(0, set_button_state, True)

def start_scan():
    thread = threading.Thread(target=scan_thread)
    thread.start()

# Main application
window = tk.Tk()
window.title("Network Port Scanner")
window.geometry("700x600")

# Frames
top_frame = tk.Frame(window)
top_frame.pack(pady=10)

input_frame = tk.Frame(window)
input_frame.pack(pady=10)

button_frame = tk.Frame(window)
button_frame.pack(pady=10)

progress_frame = tk.Frame(window)
progress_frame.pack(pady=10)

results_frame = tk.Frame(window)
results_frame.pack(pady=10)

# Titel
title = tk.Label(
    top_frame,
    text="Network Port Scanner",
    font=("Arial", 18, "bold"),
)

title.pack(pady=10)

# Subtitle
subtitle = tk.Label(
    top_frame,
    text="Scan open ports on a target machine", 
)
subtitle.pack(pady=5)

# IP
ip_label = tk.Label(input_frame, text="Target IP:")
ip_label.grid(row=0, column=0, padx=5)

ip_entry = tk.Entry(input_frame, width=20)
ip_entry.grid(row=0, column=1, padx=5)

# Start port
start_label = tk.Label(input_frame, text="Start Port:")
start_label.grid(row=1, column=0, padx=5)

start_entry = tk.Entry(input_frame, width=20)
start_entry.grid(row=1, column=1, padx=5)

# End port
end_label = tk.Label(input_frame, text="End Port:")
end_label.grid(row=2, column=0, padx=5)

end_entry = tk.Entry(input_frame, width=20)
end_entry.grid(row=2, column=1, padx=5)

# Placeholder text
add_placeholder(ip_entry, "127.0.0.1")
add_placeholder(start_entry, "1")
add_placeholder(end_entry, "1000")

# Scan button
scan_button = tk.Button(
    button_frame,
    text="Start Scan",
    command=start_scan,
    width=20
)

scan_button.grid(row=0, column=0, padx=10)

# Export button
export_button = tk.Button(
    button_frame,
    text="Export JSON",
    command=export_results,
    width=20
)

export_button.grid(row=0, column=1, padx=10)

# Center the button row
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)

# Progress bar
progress = ttk.Progressbar(
    progress_frame,
    orient="horizontal",
    length=400,
    mode="determinate"
)

progress.pack()

# Result treeview/table
results_box = ttk.Treeview(
    results_frame, 
    columns=("port", "service", "status"), show="headings"
)

results_box.heading("port", text="Port")
results_box.heading("service", text="Service")
results_box.heading("status", text="Status")

results_box.column("port", width=100, anchor="center")
results_box.column("service", width=200, anchor="center")
results_box.column("status", width=120, anchor="center")

results_box.pack()

# Status of scan
status_label = tk.Label(
    results_frame,
    text="",
    font=("Arial", 10, "bold"),
    fg="black"
)

status_label.pack(pady=5)

window.mainloop()