from config import MODEL_CONFIG

def estimate_cost(model,tokens=500):
    return MODEL_CONFIG[model]["cost"] * tokens