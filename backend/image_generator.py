import os
import urllib.parse
import requests
import base64
import time
from typing import Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class ImageGenerator:
    def __init__(self):
        self.provider = os.getenv("IMAGE_API_PROVIDER", "gemini").lower()
        self.default_gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    def generate(self, prompt: str, aspect_ratio: str = "1:1", gemini_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates photorealistic images using:
        1. Google Imagen 3 (Primary)
        2. Pollinations FLUX (Secondary)
        3. Pollinations Turbo (Multi-tier Fail-safe)
        """
        valid_aspect_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]
        ar = aspect_ratio if aspect_ratio in valid_aspect_ratios else "1:1"

        active_key = (gemini_key or self.default_gemini_key).strip()

        # Tier 1: Google Imagen 3 (Gemini API)
        if active_key and GENAI_AVAILABLE and self.provider != "pollinations":
            try:
                print(f"[ImageGenerator] Routing request to Google Imagen 3 ({ar})...")
                return self._generate_gemini_imagen(prompt, ar, active_key)
            except Exception as e:
                print(f"[ImageGenerator] Google Imagen 3 failed: {e}. Switching to Pollinations fallback...")

        # Tier 2 & Tier 3: Pollinations FLUX / Turbo Multi-tier Fallback
        print("[ImageGenerator] Routing request to Pollinations multi-tier fallback...")
        return self._generate_pollinations_multi_tier(prompt, ar)

    def _generate_gemini_imagen(self, prompt: str, aspect_ratio: str, api_key: str) -> Dict[str, Any]:
        """
        Primary Provider: Google Imagen 3 model via google-genai SDK
        """
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio=aspect_ratio,
                person_generation="ALLOW_ADULT"
            )
        )

        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            img_b64 = base64.b64encode(image_bytes).decode('utf-8')
            return {
                "success": True,
                "branch": "Primary",
                "provider": "Google Imagen 3 (Gemini)",
                "image_url": f"data:image/jpeg;base64,{img_b64}",
                "prompt": prompt,
                "aspect_ratio": aspect_ratio
            }
        else:
            raise Exception("Imagen 3 returned no images in response.")

    def _generate_pollinations_multi_tier(self, prompt: str, aspect_ratio: str) -> Dict[str, Any]:
        """
        Fail-Safe Provider: Tries Pollinations FLUX -> Pollinations Turbo -> Direct URL
        """
        width, height = 1024, 1024
        if aspect_ratio == "16:9":
            width, height = 1280, 720
        elif aspect_ratio == "9:16":
            width, height = 720, 1280
        elif aspect_ratio == "4:3":
            width, height = 1152, 864
        elif aspect_ratio == "3:4":
            width, height = 864, 1152

        encoded_prompt = urllib.parse.quote(prompt)
        seed = int(time.time() * 1000) % 1000000

        models_to_try = ["flux", "turbo", "bimpay"]

        for model in models_to_try:
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model={model}&nologo=true"
            try:
                print(f"[ImageGenerator] Attempting Pollinations ({model})...")
                response = requests.get(image_url, timeout=15)
                if response.status_code == 200 and len(response.content) > 1000:
                    img_b64 = base64.b64encode(response.content).decode('utf-8')
                    return {
                        "success": True,
                        "branch": "Fallback",
                        "provider": f"Pollinations ({model.upper()})",
                        "image_url": f"data:image/jpeg;base64,{img_b64}",
                        "direct_url": image_url,
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio
                    }
            except Exception as err:
                print(f"[ImageGenerator] Pollinations model '{model}' failed: {err}")

        # Final Direct URL Fallback (Never fail HTTP 500)
        direct_fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
        return {
            "success": True,
            "branch": "DirectFallback",
            "provider": "Pollinations Direct Stream",
            "image_url": direct_fallback_url,
            "direct_url": direct_fallback_url,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio
        }
