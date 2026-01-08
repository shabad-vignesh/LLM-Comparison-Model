import os
from huggingface_hub import InferenceClient

def llama_response(prompt: str) -> str:
    token = os.getenv("HF_API_KEY")
    if not token:
        return "HF_API_KEY not found"

    try:
        client = InferenceClient(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            token=token,
            timeout=30  # optional
        )

        response = client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        # Safety checks
        if not response or not hasattr(response, "choices") or len(response.choices) == 0:
            return "No response from model"

        content = response.choices[0].message.get("content", "")
        return content if content else "Empty model response"

    except Exception as e:
        return f"Model error: {str(e)}"
