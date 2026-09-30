from pathlib import Path

from PIL import Image

from app.schemas import ComicStory, PanelStory
from app.services.layout_builder import build_comic_layout
from app.config import settings


def test_layout_builder(tmp_path):
    image_paths = []
    for number in range(1, 6):
        path = tmp_path / f"{number}.png"
        Image.new("RGB", (100, 100), "white").save(path)
        image_paths.append(str(path))

    # layout_builder requires paths inside static_dir, so create test files there.
    real_paths = []
    for number in range(1, 6):
        path = settings.panels_dir / f"test-{number}.png"
        Image.new("RGB", (100, 100), "white").save(path)
        real_paths.append(str(path))

    try:
        story = ComicStory(
            panels=[
                PanelStory(
                    panel_number=i,
                    title=f"Panel {i}",
                    scene_description="Scene",
                    caption="Caption",
                    narration="Narration",
                    dialogue="Dialogue",
                    image_prompt="Prompt",
                )
                for i in range(1, 6)
            ]
        )
        layout = build_comic_layout(story, real_paths)
        assert len(layout) == 5
        assert layout[0].image_url.startswith("/panels/")
    finally:
        for path in real_paths:
            Path(path).unlink(missing_ok=True)
