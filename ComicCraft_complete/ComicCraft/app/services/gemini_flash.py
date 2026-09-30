from google import genai
from google.genai import types

from app.config import settings
from app.schemas import ComicOutline


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to your .env file."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicOutline:
    prompt = f"""
Create a coherent five-panel comic outline.

User story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Requirements:
- Exactly five panels.
- Each panel must advance the story.
- Keep the main character visually consistent.
- scene_description describes visible action, environment, lighting, and composition.
- image_prompt is a concise prompt suitable for a text-to-image model.
- Do not put dialogue in image_prompt.
- Return only data matching the requested schema.
""".strip()

    response = _client().models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicOutline,
            temperature=0.9,
            max_output_tokens=3000,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty outline.")
    return ComicOutline.model_validate_json(response.text)
