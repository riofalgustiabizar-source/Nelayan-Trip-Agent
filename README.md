# Nelayan Trip Agent

> An autonomous AI agent for Indonesia's traditional small-boat fishers — plans the trip before launch, watches the boat at sea, and closes the loop at the auction dock.

**Status:** concept stage · pre-MVP. The landing page and scripted demo are the artifact today; field probes (M1) come next.

---

## Why this exists

1.6 million Indonesian small-boat fishers run 2–4 day trips on 7 GT wooden boats, where:

- Misreading the wind burns 80 L of diesel for nothing (~Rp 1.2M wasted per trip).
- Landing at the wrong hour gets brokered 30% under TPI auction price.
- 60% of these fishers live below the national poverty line.

This is exactly the kind of audience generic AI assistants don't reach: offline-first reality, voice-first ergonomics (wet hands, sun glare), regional dialects (Bugis/Mandar/Madura), and a unit-economics constraint where every API call has to justify itself in liters of diesel.

## Three-phase agent loop

| Phase | What the agent does | Tool calls |
|---|---|---|
| **01 · Pre-trip** | Pulls BMKG forecast, surface currents, tide. Cross-refs with the fisher's voice-logged catch history. Outputs launch window, fuel estimate, recommended bearings. | `bmkg.fetchForecast`, `copernicus.getCurrents`, `catchHistory.recall`, `fuelCalc` |
| **02 · At sea** | Scheduled SMS heartbeats home. Weather-change alerts via SMS gateway. Voice-logged catch capture mid-trip — no keyboard. | `gps.read`, `sms.send`, `whisper.transcribe`, `bmkg.weatherChange` |
| **03 · Post-trip** | Watches TPI auction prices across 3+ nearby ports. Recommends optimal landing dock + window. Drafts WhatsApp message to broker. Logs trip P&L. | `tpi.scrape`, `fuelCalc.detourCost`, `wa.draft` |

Most of this work — fetch, format, schedule, log — belongs on a small, fast, cheap model. **~82% of calls route to the cheap tier.** Heavy reasoning fires only when the trip needs it.

## Cost-tier routing

```
┌────────────────────────────── 100% ──────────────────────────────┐
│                                                                  │
│  cheap tier                                       smart tier     │
│  ████████████████████████████████████████████░░░░░░░░░░░░░░░░░░  │
│  82%  fetch · format · log · schedule             18%  reason    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

Cheap tier: BMKG forecast fetch, SMS formatting, fuel math, TPI price polling, voice-memo logging.
Smart tier: forecast-vs-history cross-reference, abort-vs-continue under weather shift, landing-window tradeoff between fuel cost and TPI price spread.

## What exists today

- `index.html` — multilingual landing page (EN / ID / 中) with persona, agent loop, cost-tier viz, architecture sketch, honest framing, roadmap.
- `demo/` — scripted interactive demo of the 3-phase loop. Pick a scenario, hit run, watch the agent fire tool calls + phone-side output.
- `docs/ARCHITECTURE.md` — offline-first device runtime + cloud orchestrator sketch.
- `scripts/bmkg_probe.py` — small live probe against BMKG public weather API, proving the data pipe is real.
- `LICENSE` — MIT.

## What's intentionally not in scope

- **Sonar integration.** Smallholder boats don't carry it. Catch-spot prediction comes from the fisher's own voice-logged history, not hardware.
- **Sat-phone hardware.** We rely on cheap GSM SMS gateways with offline-first cache, not Iridium.
- **Marine safety authority claims.** This is a planning + ops assistant. BMKG, BASARNAS, and the harbour master remain the authorities.

## Biggest open risk

Connectivity at sea is genuinely unreliable. We treat this as a **design constraint** (offline-first cache + SMS fallback + on-device decision logic) rather than a problem to "solve later." If the agent can't work with 30% of trip-time offline, it doesn't ship.

## Local preview

```bash
# from repo root
python3 -m http.server 8000
# then open http://localhost:8000/
```

To run the BMKG probe (live API, no auth):

```bash
python3 scripts/bmkg_probe.py --area "Sulawesi Selatan"
```

## Roadmap

- **M0 · Concept** ✓ — landing, loop, demo, docs.
- **M1 · Field probe** ← *here* — two real fishers in Pangkep test the pre-trip plan against an actual launch decision. Voice log + paper diary.
- **M2 · Closed beta** — 10 boats, full 3-phase loop on a phone, SMS fallback live.
- **M3 · Koperasi rollout** — 100 boats via a fishing co-op partner, TPI integration shipping daily P&L.

## Project structure

```
nelayan-trip-agent/
├── index.html            # landing page (EN/ID/CN)
├── assets/
│   ├── style.css         # maritime dark theme
│   └── i18n.js           # language toggle
├── demo/
│   ├── index.html        # scripted demo of 3-phase loop
│   ├── demo.css
│   └── demo.js
├── docs/
│   └── ARCHITECTURE.md   # offline-first runtime sketch
├── scripts/
│   └── bmkg_probe.py     # live BMKG public-API probe
├── README.md
└── LICENSE
```

## License

MIT — see [LICENSE](./LICENSE).
