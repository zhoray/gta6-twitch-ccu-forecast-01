"""The program reads Twitch launch-day cases and forecasts hours 2..24 of release day as five quantiles per hour, learning the launch-day curve's shape from the past launches bundled in each case as comparables: for each past launch it takes the log ratio of each hour's viewers to that launch's hour-1 viewers, weights launches by how close their hour-1 size is to this case's, and reads the five quantiles off the weighted distribution."""
import json
import math
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
INPUT_DIR = Path(os.getenv("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.getenv("MAKEFUN_OUTPUT_DIR", "/output"))
LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0, 0.674, 1.645]
SIGMA = 0.15
BANDWIDTH = 1.0
MIN_PAIRS = 5
MAX_Q = 1e9
def round2(x):
    scaled = x*100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5: whole += 1
    value = whole/100
    return int(value) if value.is_integer() else value
def baseline_row(p1, h):
    return [round2(p1 * math.exp(z * SIGMA * math.sqrt(h - 1))) for z in Z]
def weighted_quantile(pairs, tau):
    pairs = sorted(pairs)
    total = sum(weight for value, weight in pairs)
    target = tau * total
    prev_value = pairs[0][0]
    prev_cum = 0.0
    cum = 0.0
    for value, weight in pairs:
        cum += weight
        if cum >= target:
            if cum == prev_cum:
                return value
            return prev_value + (target - prev_cum) / (cum - prev_cum) * (value - prev_value)
        prev_value = value
        prev_cum = cum
    return pairs[-1][0]
def hour_one_print(case):
    known = case.get('known') or []
    for row in known:
        if row.get('hour') == 1:
            return max(1, row.get('viewers', 1))
    return 1
def parse_ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))
def day_curve(comp):
    curve = {}
    try:
        start = parse_ts(comp.get('day_start', ''))
    except Exception:
        return curve
    for point in comp.get('hourly', []) or []:
        try:
            t = parse_ts(point['from'])
            secs = (t - start).total_seconds()
            if 0 <= secs < 24 * 3600:
                h = int(secs // 3600) + 1
                if h not in curve:
                    curve[h] = point.get('viewers', 0)
        except Exception:
            continue
    return curve
def build_pairs(comparables, p1):
    pairs_by_hour = {h: [] for h in range(2, 25)}
    ln_p1 = math.log(p1) if p1 > 0 else 0
    for comp in comparables or []:
        curve = day_curve(comp)
        v1 = curve.get(1, 0)
        if v1 <= 0:
            continue
        ln_v1 = math.log(v1)
        weight = math.exp(-((ln_v1 - ln_p1) ** 2) / (2 * BANDWIDTH ** 2))
        for h in range(2, 25):
            vh = curve.get(h, 0)
            if vh > 0:
                pairs_by_hour[h].append((math.log(vh / v1), weight))
    return pairs_by_hour
def clamp(x, minv, maxv):
    return max(minv, min(maxv, x))
def forecast_case(case):
    p1 = hour_one_print(case)
    pairs_by_hour = build_pairs(case.get('comparables') or [], p1)
    result = {'hours': []}
    for row in case.get('forecast', []):
        h = row.get('hour')
        if h is None:
            continue
        pairs = pairs_by_hour.get(h, [])
        if len(pairs) >= MIN_PAIRS:
            qs = [round2(clamp(p1 * math.exp(weighted_quantile(pairs, tau)), 0.01, MAX_Q)) for tau in LEVELS]
            for i in range(1, len(qs)):
                qs[i] = max(qs[i-1], qs[i])
        else:
            qs = baseline_row(p1, h)
        result['hours'].append({'hour': h, 'q': qs})
    return result
def baseline_forecast(case):
    if isinstance(case, dict):
        p1 = hour_one_print(case)
    else:
        p1 = 1
    return {'hours': [{'hour': h, 'q': baseline_row(p1, h)} for h in range(2, 25)]}
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob('*.in')):
        try:
            case = json.loads(path.read_text(encoding='utf-8'))
            result = forecast_case(case)
        except Exception:
            try:
                case = json.loads(path.read_text(encoding='utf-8'))
                result = baseline_forecast(case)
            except Exception:
                result = baseline_forecast(None)
        out_path = OUTPUT_DIR / (path.stem + '.out')
        out_path.write_text(json.dumps(result, separators=(',', ':')) + '\n')
if __name__ == "__main__":
    main()
