import os
import re
from typing import Optional

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

STYLE_PRESETS = {
    "real_photo": "raw photograph, shot on 35mm DSLR, f/1.8 aperture, 8k resolution, ultra-sharp focus, realistic fine details, natural soft lighting, neutral color grading",
    "cinematic": "cinematic movie still, 35mm anamorphic lens, dramatic chiaroscuro lighting, subtle film grain, deep shadows, shallow depth of field, blockbuster aesthetic",
    "studio_portrait": "professional studio portrait, 85mm portrait lens, Rembrandt key lighting, soft background bokeh, 8k resolution, crisp skin details",
    "landscape": "breathtaking National Geographic landscape photograph, ultra-wide 16mm lens, golden hour sunlight, vivid colors, crisp atmosphere, sharp horizon detail",
    "architecture": "architectural Digest photography, straight vertical lines, ambient light, sharp structural geometry, modern materials, editorial shot"
}

GREETINGS_MAP = {
    "hi": "A friendly modern greeting poster featuring big bold letters spelling 'HI!', vibrant speech bubble artwork, warm cheerful colors, clean design",
    "hello": "A welcoming graphic poster featuring bold text 'HELLO!', colorful speech bubble design, happy cheerful illustration",
    "hey": "A vibrant graphic greeting poster featuring bold text 'HEY!', creative speech bubble art, modern design",
    "test": "A high-tech digital test pattern with futuristic abstract geometric shapes and glowing grid lines",
    "ok": "A modern 3D graphic icon depicting a thumbs up 'OK' sign with soft cheerful lighting"
}

def enhance_prompt(raw_prompt: str, style_preset: str = "real_photo", gemini_key: Optional[str] = None) -> str:
    """
    Enhances a simple user voice or text input into a photorealistic AI prompt.
    Uses Google Gemini 2.0 Flash LLM when GEMINI_API_KEY is available.
    """
    cleaned_prompt = raw_prompt.strip()
    if not cleaned_prompt:
        return ""
    
    # Check if input is a simple greeting or short conversational word
    lower_prompt = cleaned_prompt.lower()
    if lower_prompt in GREETINGS_MAP:
        return GREETINGS_MAP[lower_prompt]

    # Strip common leading voice commands
    cleaned_prompt = re.sub(r'^(generate|create|make|draw|show me|take a picture of|give me)\s+(an?|the)?\s+(image|picture|photo|photograph)?\s*(of)?\s*', '', cleaned_prompt, flags=re.IGNORECASE).strip()
    if not cleaned_prompt:
        cleaned_prompt = raw_prompt.strip()

    api_key = (gemini_key or os.getenv("GEMINI_API_KEY", "")).strip()

    # Strategy 1: Google Gemini 2.0 Flash LLM Prompt Optimization
    if api_key and GENAI_AVAILABLE:
        try:
            print(f"[PromptOptimizer] Enhancing prompt with Google Gemini 2.0 Flash LLM...")
            client = genai.Client(api_key=api_key)
            
            system_instruction = (
                "You are an expert AI prompt engineer for high-end photorealistic image generators (Imagen 3). "
                "Your task is to take a user voice/text description and transform it into a single, highly detailed, "
                "visually rich image prompt. "
                "CRITICAL RULE 1: If the input is a short greeting, single word, or non-visual text (e.g. 'hi', 'hello', 'hey'), "
                "transform it into a creative 3D typography or graphic artwork of that text. "
                "DO NOT generate people, women, men, or portrait photos UNLESS the user explicitly asks for a person. "
                "Include realistic lighting, camera settings (lens, aperture, resolution), environment details, and atmosphere. "
                f"Style directive: {style_preset.replace('_', ' ')}. "
                "Return ONLY the final prompt text. Do NOT include intro text, explanation, quotes, or markdown code blocks."
            )
            
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=f"Convert this idea into a photorealistic image prompt: '{cleaned_prompt}'",
                config={'system_instruction': system_instruction, 'temperature': 0.7}
            )
            
            enhanced_text = response.text.strip().replace('"', '').replace('`', '')
            if enhanced_text:
                print(f"[PromptOptimizer] Gemini Enhanced Prompt: {enhanced_text[:80]}...")
                return enhanced_text
        except Exception as e:
            print(f"[PromptOptimizer] Gemini LLM optimization failed ({e}). Falling back to template optimizer.")

    # Strategy 2: Template-based fallback enhancer
    preset_suffix = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["real_photo"])
    return f"{cleaned_prompt}, {preset_suffix}"


def optimize_prompt_for_search(raw_prompt: str, gemini_key: Optional[str] = None) -> dict:
    """
    Transforms a user voice/text input into an optimized Internet Web Search Query.
    Unlike AI image prompts (which need lens/aperture specs), search engine queries
    need concise keywords, visual terms, and entity names to find relevant photos across the web.
    """
    cleaned_prompt = raw_prompt.strip()
    if not cleaned_prompt:
        return {"search_query": "", "original": raw_prompt, "method": "empty"}

    # Strip voice command prefixes
    cleaned_prompt = re.sub(
        r'^(find|search|show me|get me|look for|fetch|give me|bring up|display)\s+(an?|the)?\s+(images?|pictures?|photos?|photographs?|wallpapers?)\s*(of|for|about)?\s*',
        '',
        cleaned_prompt,
        flags=re.IGNORECASE
    ).strip()

    if not cleaned_prompt:
        cleaned_prompt = raw_prompt.strip()

    api_key = (gemini_key or os.getenv("GEMINI_API_KEY", "")).strip()

    if api_key and GENAI_AVAILABLE:
        try:
            print(f"[PromptOptimizer] Optimizing internet search query with Gemini 2.0 Flash...")
            client = genai.Client(api_key=api_key)
            system_instruction = (
                "You are an expert search engine query optimizer for image search across the web. "
                "Convert the user's voice/text query into a clean, concise, high-precision search query string "
                "suitable for web search engines (Google, Bing, DuckDuckGo). "
                "Remove conversational filler, keep essential subject keywords, photography/style descriptors, and location/entity names. "
                "CRITICAL: Return ONLY the optimized query string as plain text. No quotes, no explanations, no markdown."
            )
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=f"Convert this request into an optimal web image search query: '{cleaned_prompt}'",
                config={'system_instruction': system_instruction, 'temperature': 0.3}
            )
            optimized_query = response.text.strip().replace('"', '').replace('`', '')
            if optimized_query:
                print(f"[PromptOptimizer] Gemini Search Query: '{optimized_query}'")
                return {
                    "search_query": optimized_query,
                    "original": raw_prompt,
                    "method": "gemini_llm"
                }
        except Exception as e:
            print(f"[PromptOptimizer] Gemini Search Query Optimization failed ({e}). Using NLP fallback.")

    # NLP Fallback
    # Remove remaining noise words
    fallback_query = re.sub(r'[^\w\s-]', '', cleaned_prompt).strip()
    return {
        "search_query": fallback_query,
        "original": raw_prompt,
        "method": "nlp_fallback"
    }

