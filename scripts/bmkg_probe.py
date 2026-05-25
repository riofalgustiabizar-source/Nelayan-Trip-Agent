#!/usr/bin/env python3
"""BMKG public weather API probe.

Pulls live forecast data for a coastal coordinate (or province admin code) from
BMKG's public JSON API and prints a 24-hour summary — proving the data pipe
the Nelayan Trip Agent depends on is real, free, and accessible.

Endpoint reference:
    https://api.bmkg.go.id/publik/prakiraan-cuaca

Usage:
    python3 bmkg_probe.py                                   # default: Sulawesi Selatan province
    python3 bmkg_probe.py --adm1 35                         # Jawa Timur
    python3 bmkg_probe.py --adm4 73.06.10.1001              # village-level (Gowa, Sulsel)
    python3 bmkg_probe.py --json                            # raw JSON output

Common adm1 codes:
    31 DKI Jakarta · 32 Jawa Barat · 33 Jawa Tengah · 35 Jawa Timur
    51 Bali · 53 NTT · 73 Sulawesi Selatan · 81 Maluku · 91 Papua
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

API_BASE = "https://cuaca.bmkg.go.id/api/df/v1/forecast/adm"


def fetch(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nelayan-trip-agent/0.1 (BMKG probe)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fmt_dt(iso: str) -> str:
    """BMKG returns 2026-05-25T20:00:00Z — render as 'Tue 20:00'."""
    try:
        d = datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")
        return d.strftime("%a %H:%M")
    except (ValueError, IndexError):
        return iso[:16]


def summarize_location(loc_block: dict[str, Any]) -> dict[str, Any]:
    """Flatten one location's 9-step forecast into a small summary row."""
    loc = loc_block.get("lokasi", {})
    cuaca_lists = loc_block.get("cuaca", [])
    samples: list[dict[str, Any]] = []
    for day_list in cuaca_lists:
        for s in day_list:
            samples.append(s)

    return {
        "kotkab": loc.get("kotkab") or loc.get("kecamatan") or "?",
        "lat": loc.get("lat"),
        "lon": loc.get("lon"),
        "samples": samples[:8],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe BMKG public weather API.")
    ap.add_argument("--adm1", default="73", help="Province code (default 73=Sulsel)")
    ap.add_argument("--adm4", default=None, help="Village-level code, e.g. 73.06.10.1001")
    ap.add_argument("--json", action="store_true", help="Raw JSON output")
    ap.add_argument("--limit", type=int, default=8, help="Locations to print")
    args = ap.parse_args()

    if args.adm4:
        params = {"adm4": args.adm4}
    else:
        params = {"adm1": args.adm1}

    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    print(f"→ fetching {url}", file=sys.stderr)

    try:
        payload = fetch(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0

    top = payload.get("lokasi", {})
    province = top.get("provinsi") or "?"
    data = payload.get("data") or []

    locations = [summarize_location(blk) for blk in data]

    print(f"\nBMKG live forecast — {province} ({len(locations)} locations)\n")
    print(f"{'Location':<22} {'Now':<26} {'+9h':<26} {'°C':<5} {'Wind':<8}")
    print("-" * 92)

    for loc in locations[: args.limit]:
        s = loc["samples"]
        if not s:
            continue
        now = s[0]
        plus = s[3] if len(s) > 3 else now
        wind = f"{now.get('ws','?')} km/h"
        temp = str(now.get("t", "?"))
        now_lbl = (now.get("weather_desc_en") or now.get("weather_desc") or "?")[:24]
        plus_lbl = (plus.get("weather_desc_en") or plus.get("weather_desc") or "?")[:24]
        print(
            f"{loc['kotkab']:<22} {now_lbl:<26} {plus_lbl:<26} {temp:<5} {wind:<8}"
        )

    print(
        "\nNote: live BMKG data. Nelayan Trip Agent crosses this with Copernicus "
        "Marine currents and the fisher's voice-logged catch history.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
