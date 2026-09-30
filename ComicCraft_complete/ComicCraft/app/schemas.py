from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PromptRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    story_prompt: Annotated[str, Field(min_length=5, max_length=1200)]
    character_name: Annotated[str, Field(min_length=1, max_length=80)]
    setting: Annotated[str, Field(min_length=1, max_length=120)]
    tone: Annotated[str, Field(min_length=1, max_length=50)]
    art_style: Annotated[str, Field(min_length=1, max_length=80)]

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def reject_control_characters(cls, value: str) -> str:
        if any(ord(ch) < 32 and ch not in "\n\t" for ch in value):
            raise ValueError("Input contains unsupported control characters.")
        return value


class ImageTestRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    prompt: Annotated[str, Field(min_length=5, max_length=1200)]


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: list[PanelOutline] = Field(min_length=5, max_length=5)


class PanelStory(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str


class ComicStory(BaseModel):
    panels: list[PanelStory] = Field(min_length=5, max_length=5)


class LayoutPanel(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str
    image_url: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str
