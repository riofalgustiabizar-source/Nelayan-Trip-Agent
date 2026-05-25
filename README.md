<div align="center">

# 🌊 Nelayan Trip Agent

**An autonomous AI agent for Indonesia's traditional small-boat fishers.**
*Plans the trip before launch. Watches the boat at sea. Closes the loop at the auction dock.*

[![Live Demo](https://img.shields.io/badge/live-demo-2d6c8a?style=for-the-badge&logo=safari&logoColor=white)](https://riofalgustiabizar-source.github.io/Nelayan-Trip-Agent/)
[![Try the Agent](https://img.shields.io/badge/try-the%20agent-ffb84d?style=for-the-badge&logo=openai&logoColor=white)](https://riofalgustiabizar-source.github.io/Nelayan-Trip-Agent/demo/)
[![Status](https://img.shields.io/badge/status-concept%20stage%20%C2%B7%20pre--MVP-67c79a?style=for-the-badge)](#roadmap)
[![License: MIT](https://img.shields.io/badge/license-MIT-9aafc4?style=for-the-badge)](./LICENSE)

</div>

---

## 🔗 Live

| | |
|---|---|
| 🪟 **Landing page** | <https://riofalgustiabizar-source.github.io/Nelayan-Trip-Agent/> |
| 🛟 **Interactive demo** | <https://riofalgustiabizar-source.github.io/Nelayan-Trip-Agent/demo/> |
| 🌐 **Languages** | English · Bahasa Indonesia · 简体中文 |
| ⚙️ **Live LLM mode** | Bring your own OpenAI-compatible key (MiMo · OpenAI · Groq · xAI · Together · Custom) |

---

## 🎣 Why this exists

**1.6 million** Indonesian small-boat fishers run 2–4 day trips on 7 GT wooden boats — the underserved tail of one of the world's largest fishing nations.

| Pain | Cost |
|---|---|
| 🌬️ Misreading the wind | ~80 L diesel burned for nothing · **Rp 1.2M wasted per trip** |
| 🐟 Landing at the wrong hour | Brokered **30% under** TPI auction price |
| 💸 60% live below the national poverty line | A bad trip is rent + groceries gone |

This is exactly the audience generic AI assistants don't reach:

- 📡 Offline-first reality (4G drops 18+ km out)
- 🎙️ Voice-first ergonomics (wet hands, sun glare on cheap screens)
- 🗣️ Regional dialects (Bugis · Mandar · Madura)
- ⛽ Unit economics where every API call has to justify itself in liters of diesel

---

## 🧭 Three-phase agent loop

<table>
<tr>
<th>Phase</th>
<th>What the agent does</th>
<th>Tools</th>
</tr>
<tr>
<td><strong>01 · Pre-trip 🌅</strong></td>
<td>Pulls BMKG forecast, surface currents, tide. Cross-refs the fisher's voice-logged catch history. Outputs launch window, fuel estimate, recommended bearing.</td>
<td><code>bmkg.fetchForecast</code><br><code>copernicus.getCurrents</code><br><code>catchHistory.recall</code><br><code>fuelCalc</code></td>
</tr>
<tr>
<td><strong>02 · At sea 🌊</strong></td>
<td>4-hour SMS heartbeats home. Weather-change alerts on the same gateway. Voice-logged catch capture mid-trip — no keyboard.</td>
<td><code>gps.read</code><br><code>sms.send</code><br><code>whisper.transcribe</code><br><code>bmkg.weatherChange</code></td>
</tr>
<tr>
<td><strong>03 · Post-trip 🏝️</strong></td>
<td>Watches TPI auction prices across 3+ nearby ports. Recommends optimal landing dock + window. Drafts the WhatsApp message to the broker. Logs trip P&amp;L.</td>
<td><code>tpi.scrape</code><br><code>fuelCalc.detourCost</code><br><code>wa.draft</code></td>
</tr>
</table>

---

## ⚖️ Cost-tier routing

Most of the work — fetch, format, schedule, log — belongs on a small, fast, cheap model.

```
┌────────────────────────────── 100% ──────────────────────────────┐
│                                                                  │
│  cheap tier                                       smart tier     │
│  ████████████████████████████████████████████░░░░░░░░░░░░░░░░░░  │
│  82%  fetch · format · log · schedule             18%  reason    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

> 🟢 **Cheap tier** — BMKG forecast fetch · SMS formatting · fuel math · TPI price polling · voice-memo logging.
>
> 🟡 **Smart tier** — forecast-vs-history cross-reference · abort-vs-continue under weather shift · landing-window tradeoff between fuel cost and TPI price spread.

This is the unit-economics shape that lets us fit inside a smallholder's reality. It's also a natural fit for a tiered model family that bills cheap calls cheaply.

---

## ✨ What makes this build legible

- 🌅 **Hand-drawn maritime SVGs** — boat at dawn, persona portrait, system architecture. No raster, no CDN fonts, render instant on 2G.
- 🌐 **Trilingual landing** — EN / ID / CN, lang toggle persists across sessions.
- 🛟 **Interactive demo** — pick a scenario, watch the agent fire tool calls + phone-side replies.
- ⚙️ **Bring-your-own-LLM mode** — paste an OpenAI-compatible key, the demo's natural-language replies become live.
- 🛰️ **Live data probe** — `scripts/bmkg_probe.py` hits Indonesia's public weather API and proves the data pipe is real.
- ✅ **Honest framing** — concept-stage, pre-MVP, scope cuts spelled out. No over-claim.

---

## 🚫 What's intentionally not in scope

- **Sonar integration.** Smallholder boats don't carry it. Catch-spot prediction comes from the fisher's own voice-logged history, not hardware we know they can't afford.
- **Sat-phone hardware.** We rely on cheap GSM SMS gateways with offline-first cache, not Iridium.
- **Marine safety authority.** This is a planning + ops assistant. BMKG, BASARNAS, and the harbour master remain the authorities.

---

## ⚠️ Biggest open risk

> **Connectivity at sea is genuinely unreliable.**
>
> We treat this as a **design constraint** — offline-first cache, SMS fallback, on-device decision logic — not a problem to "solve later." If the agent can't work with 30% of trip-time offline, it doesn't ship.

---

## 🛰️ Live BMKG probe (no auth required)

```bash
python3 scripts/bmkg_probe.py --adm1 73 --limit 6
```

Hits `cuaca.bmkg.go.id/api/df/v1/forecast/adm` — Indonesia's public weather API, no key needed. Returns 24+ forecast points across South Sulawesi, including Pangkep where Pak Yusuf launches from.

---

## 🗺️ Roadmap

| Stage | What | When |
|:---:|---|---|
| **M0** ✅ | Concept · landing · loop · demo · docs | Today |
| **M1** ⏳ | Field probe — 2 real fishers in Pangkep test the pre-trip plan against an actual launch decision (voice log + paper diary) | Next |
| **M2** | Closed beta — 10 boats, full 3-phase loop on a phone, SMS fallback live | Q3 |
| **M3** | Koperasi rollout — 100 boats via a fishing co-op partner, TPI integration shipping daily P&L | Q4+ |

---

## 📁 Project structure

```
nelayan-trip-agent/
├── index.html              # landing page (EN/ID/CN, hero + persona + arch)
├── assets/
│   ├── style.css           # maritime dark theme
│   ├── i18n.js             # language toggle (persistent)
│   ├── hero.svg            # boat-at-dawn illustration
│   ├── persona.svg         # Pak Yusuf portrait
│   ├── architecture.svg    # phone ↔ cloud system diagram
│   └── favicon.svg
├── demo/
│   ├── index.html          # interactive 3-phase demo
│   ├── demo.css
│   └── demo.js             # scripted runtime + live LLM mode
├── docs/
│   └── ARCHITECTURE.md     # offline-first runtime + orchestrator
├── scripts/
│   └── bmkg_probe.py       # live BMKG public-API probe
├── README.md
└── LICENSE
```

---

## 📜 License

MIT — see [LICENSE](./LICENSE). Free to study, fork, and ship.

---

<div align="center">

*Built for Pak Yusuf and 1.6 million others.*
*The boat doesn't wait for a roadmap.* ⚓

</div>
