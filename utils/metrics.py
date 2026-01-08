import os 
import csv
import time 
from threading import Lock
METRICS_DIR = "data/metrics"
METRICS_FILE = os.path.join(METRICS_DIR, "metrics.csv")
file_lock = Lock()
os.makedirs(METRICS_DIR, exist_ok=True)
if not os.path.exists(METRICS_FILE):
    with open(METRICS_FILE,"w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "model",
            "latency",
            "response_length"
            ])
def log_metrics(model: str, latency: float, response_length: int):
    with file_lock:
        with open(METRICS_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                time.time(),
                model,
                round(latency,3),
                response_length
            ])