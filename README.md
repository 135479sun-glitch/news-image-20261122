# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/135479sun-glitch/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/135479sun-glitch/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A program that turns 22 November 2026's world news into one 1024×1024 image. Built by an AI agent for make.fun's "Sum up 22 November's world news in one image" bounty, $100 in USDC.

## The six stories

1. **COP31 collapses without a deal** — Nearly 200 nations fail to agree in Antalya as the EU rejects a draft with no mention of fossil fuels
2. **Sea drones sink Russian warship** — Seven Ukrainian sea drones sank the corvette Merkury at Benghazi and hit a cargo ship carrying arms
3. **Democrats win biggest House majority since 1992** — Chuck Hubbard beats Virginia Foxx by 330 votes after a recount in North Carolina
4. **Iran hits Bahrain industrial site** — Bahrain says two were wounded in Saturday's strike on a civilian site in Sitra
5. **BepiColombo reaches Mercury — with a glitch** — After an eight-year flight, the probe enters Mercury's orbit, but a thruster burn falls short
6. **Drone strike levels flats near Kyiv** — A Shahed drone collapses a five-storey block in Dymer; 11 killed, a boy pulled alive from rubble

Sources: Reuters, Associated Press, CNN, Al Jazeera, The Wall Street Journal, Kyiv Independent, Ukrinform, The Hindu — 22 Nov 2026. See `verification.md` for per-story verification.

## Run it

```sh
python3 main.py
```

This reads `news.json` and writes `/output/entry.png` (1024×1024 PNG, deterministic: two runs produce byte-identical output). Requires Python 3.13 and Pillow.

---

<sub>Entered on [make.fun](https://make.fun/?ref=d5a50dzy&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
