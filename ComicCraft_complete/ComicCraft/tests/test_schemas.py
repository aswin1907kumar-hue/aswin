import pytest
from pydantic import ValidationError

from app.schemas import PromptRequest


def test_prompt_request_accepts_valid_input():
    payload = PromptRequest(
        story_prompt="A fox discovers a secret library.",
        character_name="Finn",
        setting="Forest",
        tone="Dramatic",
        art_style="Anime",
    )
    assert payload.character_name == "Finn"


def test_prompt_request_rejects_empty_story():
    with pytest.raises(ValidationError):
        PromptRequest(
            story_prompt="",
            character_name="Finn",
            setting="Forest",
            tone="Dramatic",
            art_style="Anime",
        )
