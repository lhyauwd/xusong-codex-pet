# xusong Codex Pet

`xusong` is a Codex-compatible v2 animated pet inspired by a chibi singer-songwriter concept. The package includes all nine standard Codex animation states and sixteen look directions.

## Animation states

| State | Pet action |
| --- | --- |
| `idle` | Holds GROMI calmly |
| `running-right` | Moves to the right while singing |
| `running-left` | Moves to the left while singing |
| `waving` | Waves hello |
| `jumping` | Offers GROMI with the interaction text "借你" |
| `failed` | Reacts to a failed task |
| `waiting` | Waits and waves |
| `running` | Writes a song at a desk |
| `review` | Sings with a purple microphone |

## Install

Copy `pet/` to the Codex pet directory as `xusong`:

```text
%USERPROFILE%\.codex\pets\xusong\
```

The folder must contain `pet.json` and `spritesheet.webp` together. Restart Codex or open a new task after installing.

## Douyin video

The `release/` directory contains:

- `xusong-actions-douyin-preview.mp4`: preview with an original, royalty-safe backing track.
- `xusong-actions-douyin-silent.mp4`: silent master for adding music from Douyin's licensed music library.
- `douyin-caption.txt`: suggested caption, title, cover text, and tags.

The repository intentionally does not redistribute commercial recordings. For a Xu Song song, add it inside Douyin from the platform's licensed music library when publishing.

## JianYing draft

After JianYing Pro is installed, generate an editable 1080x1920 draft containing the silent publishing master:

```powershell
$env:JY_SKILL_ROOT="$HOME\.codex\skills\jianying-editor"
python scripts/create_jianying_draft.py
```

The draft deliberately contains no commercial audio. Open it in JianYing for final timing or text adjustments, export the video, then add a Xu Song track from Douyin's licensed music library during publishing.

## Packages

Local release builds are written to `dist/`:

- `xusong-pet.zip`: minimal Codex pet installation package.
- `xusong-codex-pet-release.zip`: pet, videos, scripts, documentation, and publishing copy.
- `SHA256SUMS.txt`: integrity hashes for both archives.

The ZIP files are Git-ignored to keep the repository lean. Publish them as GitHub Release assets when distributing a version.

## Build

The build script reads the nine QA GIFs exported by the pet workflow and renders a 1080x1920 H.264 video.

```powershell
$env:PYTHONPATH="<path-to-jianying-python-runtime>"
python scripts/render_douyin.py --preview-dir "<path-to-pet-qa-previews>" --output-dir release
```

## Validation

The packaged atlas is `1536x2288`, uses `192x208` cells, sets `spriteVersionNumber` to `2`, and passed the Hatch Pet v2 atlas validator without errors or warnings.

The machine-readable result is committed at `dist/validation-xusong.json`.

## License and likeness

Code and packaging metadata are released under the MIT License. Character artwork and likeness-related rights are not granted by the MIT License. Do not imply endorsement by Xu Song, GROMI's rights holders, OpenAI, or Douyin.
