from pathlib import Path

from app.config import settings
from app.schemas import ComicStory, LayoutPanel


def build_comic_layout(story: ComicStory, image_paths: list[str]) -> list[LayoutPanel]:
    if len(story.panels) != 5:
        raise ValueError("Comic layout requires exactly five story panels.")
    if len(image_paths) != 5:
        raise ValueError("Comic layout requires exactly five generated images.")

    layout: list[LayoutPanel] = []

    for panel, image_path in zip(story.panels, image_paths, strict=True):
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Generated image does not exist: {path}")

        try:
            public_path = "/" + path.relative_to(settings.static_dir).as_posix()
        except ValueError as exc:
            raise ValueError("Image path must be inside the static directory.") from exc

        layout.append(
            LayoutPanel(
                panel_number=panel.panel_number,
                title=panel.title,
                image_url=public_path,
                scene_description=panel.scene_description,
                caption=panel.caption,
                narration=panel.narration,
                dialogue=panel.dialogue,
                image_prompt=panel.image_prompt,
            )
        )

    return layout
