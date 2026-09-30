from google import genai
from google.genai import types

from app.config import settings
from app.schemas import ComicOutline, ComicStory


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to your .env file."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def generate_story(
    outline: ComicOutline,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicStory:
    outline_json = outline.model_dump_json(indent=2)

    prompt = f"""
Expand this five-panel comic outline into a polished comic script.

Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Outline:
{outline_json}

For every panel provide:
- panel_number
- title
- scene_description
- caption: short ambient/environmental text
- narration: concise story narration
- dialogue: dialogue spoken by characters; use an empty string if none is appropriate
- image_prompt: a strong visual prompt that keeps character identity and scene continuity consistent.

Keep the story suitable for a general audience. Do not place speech bubbles or written words inside the generated image prompt.
Return exactly five panels matching the schema.
""".strip()

    response = _client().models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicStory,
            temperature=0.85,
            max_output_tokens=5000,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty story.")
    return ComicStory.model_validate_json(response.text)
