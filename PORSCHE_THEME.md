# Automotive-inspired profile theme

The Porsche-inspired design uses the approved photographic artwork as self-contained SVG image panels. It is not a live 3D viewer or an official Porsche page.

- Hero: sports coupe and developer introduction.
- Asymmetric lower section: technology stack on the left, three real GitHub links on the right.
- Native text navigation jumps to Profile, Projects, and Stack.
- Accessible text fallback includes the introduction, technologies, and SNS links.
- Existing Elysium, Cyberpunk, and automatic theme behavior remains available.

Set `theme.txt` to `porsche`, then run `python porsche.py && python build_readme.py` (Python 3 + Pillow). The approved artwork is stored as `assets/porsche/approved-design.webp`. SVG viewports preserve its layout and embed the image without external dependencies.

The existing theme-switch workflow accepts `porsche` through manual dispatch or an owner-authored `theme:porsche` issue. The PR selects Porsche as the active theme after merge.

Validation: README generation for all four modes; local image paths, SNS and project destinations, XML parsing, and `git diff --check`. GitHub table styling can introduce borders and spacing compared with the original design preview. Activity and language cards show explicitly dated 2026-10-06 snapshots; the contribution card links to the live service. The two-column section scales on mobile; the text fallback remains available below it.

## Motion and physical cards

All custom Porsche panels have a slow reflected-light sweep and a red edge accent. CSS disables sweeps for `prefers-reduced-motion`. The hero uses a six-second animated WebP, with a static SVG source for reduced motion and a linked H.264 MP4. It is camera and exposure motion applied to a still, not generated driving footage or a real-time 3D scene.

`bash render_porsche_motion.sh` rebuilds both motion files using ffmpeg and Pillow. Regular workflow runs reuse the committed media. `porsche_panels.py` rebuilds the two instrument-style statistics panels and four physical repository cards.

The activity numbers come from the supplied screenshot; language percentages were verified against the public GitHub Readme Stats response. Both are labeled snapshots and do not claim to refresh live. Repository names, languages and descriptions were checked against GitHub REST. Update the snapshot values and date together when refreshing.

The blank material was generated using the built-in image generator. Prompt: one blank photographed automotive instrument panel with machined titanium bevels, black carbon fiber, smoked-glass center, tiny red LEDs, no text or numbers. Asset: `assets/porsche/panel-material.webp`. Text and statistics are overlaid by SVG code.
