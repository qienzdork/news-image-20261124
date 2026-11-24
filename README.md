[![competition](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/c/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/qienzdork/news-image-20261124/rank.svg)](https://make.fun/c/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/qienzdork/news-image-20261124/reward.svg)](https://make.fun/c/news-image-20261124)

# Tuesday 24 November 2026 — World News in One Image

One 1024×1024 front-page image summing up Tuesday 24 November 2026 in six
panels: Ukraine says it sank a Russian warship off Libya; the COP31 climate
talks collapse with no deal in Antalya; Nvidia reinstates Jensen Huang as CEO
and shares jump 33%; a factory fire in Cikande, Indonesia kills 24 with about
30 still missing; Carlos Alcaraz wins his first ATP Finals crown in Turin; and
Game 1 of the World Chess Championship begins in Geneva between Gukesh and
Sindarov.

`main.py` is pure Python standard library (zlib, struct) — it draws the image
with a built-in 5×7 bitmap font and encodes the PNG by hand. No third-party
dependencies, no network. It is fully deterministic: running it twice produces
byte-identical output. Run it with `OUTPUT_DIR=/tmp/out python3 main.py`.
