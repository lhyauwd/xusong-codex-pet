from __future__ import annotations

import json
import os
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
ENV_ROOT = os.getenv("JY_SKILL_ROOT", "").strip()
SKILL_CANDIDATES = [
    ENV_ROOT,
    str(PROJECT_ROOT / ".agent" / "skills" / "jianying-editor"),
    str(PROJECT_ROOT / ".trae" / "skills" / "jianying-editor"),
    str(PROJECT_ROOT / ".claude" / "skills" / "jianying-editor"),
    str(PROJECT_ROOT / "skills" / "jianying-editor"),
    str(Path.home() / ".codex" / "skills" / "jianying-editor"),
]

SCRIPTS_PATH = next(
    (
        Path(candidate).resolve() / "scripts"
        for candidate in SKILL_CANDIDATES
        if candidate and (Path(candidate).resolve() / "scripts" / "jy_wrapper.py").exists()
    ),
    None,
)

if SCRIPTS_PATH is None:
    raise ImportError("Could not find jianying-editor/scripts/jy_wrapper.py")

sys.path.insert(0, str(SCRIPTS_PATH))

from jy_wrapper import JyProject  # noqa: E402


def main() -> None:
    source = (PROJECT_ROOT / "release" / "xusong-actions-douyin-silent.mp4").resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    drafts_root = os.getenv("JY_PROJECTS_ROOT", "").strip() or None
    project = JyProject(
        "xusong-actions-douyin",
        width=1080,
        height=1920,
        drafts_root=drafts_root,
        overwrite=True,
    )
    segment = project.add_media_safe(
        str(source),
        start_time="0s",
        duration="15.3s",
        track_name="xusong-actions",
    )
    if segment is None:
        raise RuntimeError(f"Failed to add video asset: {source}")

    result = project.save()
    print(
        json.dumps(
            {
                "ok": True,
                "code": "ok",
                "reason": "",
                "data": {
                    "project": project.name,
                    "draft_path": result["draft_path"],
                    "source": str(source),
                    "resolution": [1080, 1920],
                    "video_tracks": 1,
                    "audio_tracks": 0,
                },
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
