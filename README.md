# GTA VI Launch-Day Twitch Forecaster

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/zhoray/gta6-twitch-ccu-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/zhoray/gta6-twitch-ccu-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[GTA VI launch-day forecaster on make.fun — gta6-twitch-ccu-forecast-01](https://make.fun/bounty/gta6-twitch-ccu-forecast-01)

This script forecasts Twitch viewership for GTA VI launch day by reading launch-day cases from the input directory, which include the first-hour print and comparable past launches. It outputs five quantiles (5th, 25th, 50th, 75th, and 95th percentiles) for each hour from 2 to 24.

The method normalizes each comparable's release-day curve by its own hour-1 viewers, then applies a Gaussian kernel weighting based on the log distance of hour-1 sizes (bandwidth 1.0) to emphasize similar-scale launches. Quantiles are extracted from this weighted distribution and scaled by the current case's hour-1 print. For sparse hours or unparseable cases, it falls back to a persistence baseline (flat from hour 1 with 0.15 sqrt-hour log spread), ensuring a valid forecast is always produced.

To run it, execute `python3 main.py` with the environment variables MAKEFUN_INPUT_DIR and MAKEFUN_OUTPUT_DIR set appropriately. It uses only standard library, with no network dependencies.
