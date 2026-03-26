import os
from agno.tools import tool
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
DEFAULT_IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1536x1024")
ALLOWED_SIZES = {"1024x1024", "1536x1024", "1024x1536", "auto"}


@tool
def generate_header_image(
    prompt: str,
    size: str = DEFAULT_IMAGE_SIZE,
    quality: str = "high",
    alt_text: str = "Generated email header image",
) -> dict:
    """
    Generate a marketing image and return inline base64 payload.

    Args:
        prompt: The image generation prompt.
        size: Image dimensions supported by the selected model.
        quality: Rendering quality preference (auto, low, medium, high).
        alt_text: Accessible fallback description for frontend rendering.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"success": False, "error": "OPENAI_API_KEY is not configured."}

    if size not in ALLOWED_SIZES:
        return {
            "success": False,
            "error": f"Unsupported size '{size}'. Allowed: {sorted(ALLOWED_SIZES)}",
        }

    try:
        client = OpenAI(api_key=api_key)
        response = client.images.generate(
            model=DEFAULT_IMAGE_MODEL,
            prompt=prompt,
            size=size,
            quality=quality,
        )

        b64_data = None
        if getattr(response, "data", None):
            first = response.data[0]
            b64_data = getattr(first, "b64_json", None)
            if not b64_data and isinstance(first, dict):
                b64_data = first.get("b64_json")

        if not b64_data:
            return {"success": False, "error": "Image API did not return base64 data."}

        return {
            "success": True,
            "mime_type": "image/png",
            "base64_data": b64_data,
            "alt_text": alt_text,
            "model": DEFAULT_IMAGE_MODEL,
            "size": size,
        }
    except Exception as exc:
        return {"success": False, "error": f"Image generation failed: {str(exc)}"}
