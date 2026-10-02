# Privacy policies

Public privacy policies of the Android games published by mxstex, served by GitHub Pages
from the `main` branch root:

| app | page | source text |
| --- | --- | --- |
| Gravity (`com.mxstex.gravity`) | https://mxstex.github.io/privacy/gravity/ | `gravityAndroid/docs/privacy-policy.md` |
| Gravity 3D (`com.mxstex.gravity3d`) | https://mxstex.github.io/privacy/gravity3d/ | `gravityAndroid3d/docs/privacy-policy.md` |

The text belongs to each app's repository, next to the code and manifest it describes.
This repository only publishes it: with the app repositories checked out beside it,
`python build.py` renders both pages and `python build.py --check` fails when a page is
out of date. `index.html` is the hand-written landing page linking both policies;
`privacy-policy.html` (the first, 2D-only page) redirects to `gravity/`.
`.nojekyll` makes Pages serve the files as they are.

Published 2026-09-27: GitHub Pages serves `main` / root (build `88f9dff`). Both URLs return HTTP 200 and exactly match the committed generated HTML. Play Console entry remains a separate owner action.
