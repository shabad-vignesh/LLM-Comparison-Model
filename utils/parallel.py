from concurrent.futures import ThreadPoolExecutor
from models.chatgpt_model import chatgpt_response
from models.gemini_model import gemini_response
from models.llama_model import llama_response
from utils.metrics import log_metrics
import time

MODEL_FUNCTIONS = {
    "chatgpt": chatgpt_response,
    "gemini": gemini_response,
    "llama": llama_response
}
def run_parallel(prompt, models):
    results = {}

    def call_model(model_name):
        key = model_name.lower()  
        start_time = time.time()
        if key in MODEL_FUNCTIONS:
            try:
                response = MODEL_FUNCTIONS[key](prompt)
            except Exception as e:
                response = f"Error: {e}"
        else:
            response = f"Model {model_name} not supported."

        elapsed = time.time() - start_time
        log_metrics(model_name, elapsed, len(response))
        return response

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        futures = {model: executor.submit(call_model, model) for model in models}

        for model, future in futures.items():
            try:
                results[model] = future.result()
            except Exception as e:
                results[model] = f"Unexpected error: {e}"

    return results