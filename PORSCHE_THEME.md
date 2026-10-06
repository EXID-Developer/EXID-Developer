# Automotive-inspired profile theme

The Porsche-inspired design uses the approved static artwork as self-contained SVG image panels. It is not a live 3D viewer or an official Porsche page.

- Hero: sports coupe and developer introduction.
- Asymmetric lower section: technology stack on the left, three real GitHub links on the right.
- Native text navigation jumps to Profile, Projects, and Stack.
- Accessible text fallback includes the introduction, technologies, and SNS links.
- Existing Elysium, Cyberpunk, and automatic theme behavior remains available.

Set `theme.txt` to `porsche`, then run `python porsche.py && python build_readme.py` (Python 3 + Pillow). The approved artwork is stored as `assets/porsche/approved-design.webp`. SVG viewports preserve its layout and embed the image without external dependencies.

The existing theme-switch workflow accepts `porsche` through manual dispatch or an owner-authored `theme:porsche` issue. The PR selects Porsche as the active theme after merge.

Validation: README generation for all four modes; local image paths, SNS and project destinations, XML parsing, and `git diff --check`. GitHub table styling can introduce borders and spacing compared with the original design preview. External statistics keep their existing availability dependencies. The two-column section scales on mobile; the text fallback remains available below it.
