from models.chatgpt_model import chatgpt_response
from models.gemini_model import gemini_response
from models.llama_model import llama_response

MODEL_MAP = {
    "chatgpt": chatgpt_response,
    "gemini": gemini_response,
    "llama": llama_response,
}

FALLBACK_ORDER = {
    "chatgpt": ["gemini", "llama"],
    "gemini": [ "llama"],
    "llama": [],
}


def execute_with_fallback(model_name: str,prompt: str):
    """
    Try primary model.
    If it fails, automatically try fallback models.
    """
    try:
        return MODEL_MAP[model_name](prompt)
    except Exception as primary_error:

        for fallback_model in FALLBACK_ORDER.get(model_name, []):
            try:
                return MODEL_MAP[fallback_model](prompt)
            except Exception:
                continue

        return f"All models fallback failed for {model_name}"