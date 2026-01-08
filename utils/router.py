from config import MODEL_CONFIG
def choose_models(task_type):
    if task_type == "Coding":
        return ["chatgpt","gemini"]
    elif task_type == "Fast Responses":
        return ["gemini"]
    elif task_type == "Cost Saving":
        return ["llama","gemini"]
    else:
        return ["chatgpt","gemini","llama"]