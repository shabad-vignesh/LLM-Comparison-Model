import pandas as pd
import os
from datetime import datetime

def generate_report(prompt: str, responses: dict):
    # Create the correct folder
    os.makedirs("data/comparison", exist_ok=True)

    rows = []
    for model, output in responses.items():
        rows.append({
            "Model": model,
            "Prompt": prompt,
            "Response": output,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    df = pd.DataFrame(rows)

    # Save inside the folder you just created
    df.to_csv("data/comparison/report.csv", index=False)

    return "data/comparison/report.csv"
