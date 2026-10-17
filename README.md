# BeliefWeaver project page

[**Website**](https://wuxiyang1996.github.io/beliefweaver_page/) · [Paper](https://arxiv.org/abs/2610.18082) · [Video](https://wuxiyang1996.github.io/beliefweaver_page/assets/beliefweaver-short.mp4)

Project page for *Failure Recovery via Belief Updates and World Modeling for Long-Horizon Agents*. Includes an interactive method overview, paper results, and a 63-second narrated video.

## Preview and publish

```bash
python -m http.server 8080
```

Open http://localhost:8080. No build or package installation is required.

GitHub Pages serves the root of `main`, matching the deployment structure of [SABER_page](https://github.com/wuxiyang1996/SABER_page). Push page edits to `main` to publish. `.nojekyll` enables plain static hosting.

- `index.html`, `styles.css`, `app.js`: webpage and interactive diagrams/results.
- `assets/`: method figure, short MP4, English captions, and video poster.
- `media-source/`: editable narration and reproducible video scripts; see its [README](media-source/README.md).

The experimental code lives separately in [beliefweaver](https://github.com/wuxiyang1996/beliefweaver), currently private. Its link is labeled accordingly on the page.

## Attribution

Research facts and results come from Wu et al., [arXiv:2610.18082v1](https://arxiv.org/abs/2610.18082v1), especially Tables 1 and 4. They are paper-reported values, not new experiment runs. Teacher API cost excludes executor, student-serving, and training costs.

`assets/beliefweaver-overview.png` reproduces Figure 1 under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Original figure](https://arxiv.org/html/2610.18082v1/neo_framework_cropped.png). Copyright remains with the paper authors.

Page organization is inspired by [SABER](https://wuxiyang1996.github.io/SABER_page/); the implementation, schematic, and video animations are original. The video uses English synthetic narration and burned-in captions. Fonts use Google Fonts (DM Sans and Manrope), with system fallbacks.

Original website and video-generation code: [Apache-2.0](LICENSE). The paper figure retains its CC BY 4.0 license.
