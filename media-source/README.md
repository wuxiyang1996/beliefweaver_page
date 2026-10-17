# BeliefWeaver short video

A ~63-second, 1280×720, 30 fps motion-graphic research overview. English narration
uses the local Microsoft Zira Desktop synthetic voice. Captions are burned in;
the matching `.vtt` supports accessible transcript/caption integrations.

All graphics are original schematics, not recordings of benchmark runs. Based on
*Failure Recovery via Belief Updates and World Modeling for Long-Horizon Agents*.
Results are attributed to Table 1 of [arXiv:2610.18082v1](https://arxiv.org/abs/2610.18082v1):
48.6% Terminus-2, 53.7% BeliefWeaver, and 58.4% SFT + OPD across 113 tasks.
These are Overall Final scores (test-pass fractions or graded rewards), not
necessarily binary task success rates. No paper figures are reused in the video.
The source code release has not independently reproduced these figures.

## Render

Requires Python 3.12+, Windows with Microsoft Zira Desktop, and Segoe UI fonts.
The encoder comes from `imageio-ffmpeg`; no system ffmpeg install is needed.

```powershell
python -m pip install -r media-source/requirements.txt
python media-source/render_video.py --work-dir C:/temp/beliefweaver-video --synthesize
```

Generated delivery files are `assets/beliefweaver-short.mp4`,
`beliefweaver-short.vtt`, and `video-poster.jpg`. Audio, timing metadata, preview
frames, contact sheet, and verification logs stay in the work directory. Run
with `--preview-only` to inspect layouts before encoding. The narration and
caption wording are editable in `narration.json`.

The renderer uses no online speech service, model API, benchmark logs, or paper
figure assets. Voice/font availability can change rendering on another machine.
