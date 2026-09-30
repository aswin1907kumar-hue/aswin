from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000

    gemini_api_key: str | None = None
    gemini_outline_model: str = "gemini-3.8-flash"
    gemini_story_model: str = "gemini-3.8-flash"

    image_generation_mode: str = "demo"
    hf_token: str | None = None
    hf_model_id: str = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    image_width: int = 512
    image_height: int = 512
    image_steps: int = 20
    image_guidance_scale: float = 7.0
    image_cpu_offload: bool = False
    image_seed: int = 42

    max_story_prompt_length: int = 1200
    max_character_name_length: int = 80
    max_setting_length: int = 120
    max_tone_length: int = 50
    max_art_style_length: int = 80

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def base_dir(self) -> Path:
        return BASE_DIR

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "app" / "templates"

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panels_dir(self) -> Path:
        path = self.static_dir / "panels"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def exports_dir(self) -> Path:
        path = self.static_dir / "exports"
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
