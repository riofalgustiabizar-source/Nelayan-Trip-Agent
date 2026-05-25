# Architecture — Nelayan Trip Agent

> Offline-first device runtime backed by a cloud orchestrator. The phone caches everything; the cloud is a sync target, not a hard dependency.

## Design constraints

- **Connectivity at sea is unreliable.** 30%+ of trip-time will have no usable signal. The agent must still make decisions and log data.
- **Voice-first.** Wet hands, sun glare, gloves. Keyboard interaction is a fallback, not a default.
- **Cost per inference matters.** Every smart-tier call has to justify itself in rupiah. The router routes ~82% of calls to a cheap model.
- **Regional dialects.** Bugis, Mandar, Makassar, Madura. STT must accept them; TTS must speak them.

## Two-tier runtime

```
┌──────────────────────────────────────────────────────────────────┐
│                       FISHER'S PHONE (offline-first)             │
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│   │ voice in/out │ ◀▶ │ on-device    │ ◀▶ │ SMS fallback     │   │
│   │ (whisper-id, │    │ cache (catch │    │ (GSM gateway,    │   │
│   │  TTS local)  │    │ history,     │    │  satellite)      │   │
│   │              │    │ last         │    │                  │   │
│   │              │    │ forecast,    │    │                  │   │
│   │              │    │ trip P&L)    │    │                  │   │
│   └──────────────┘    └──────┬───────┘    └────────┬─────────┘   │
│                              │                     │             │
└──────────────────────────────┼─────────────────────┼─────────────┘
                               │ sync when online    │ always-on
                               ▼                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                       CLOUD ORCHESTRATOR                         │
│                                                                  │
│   ┌────────────────┐    ┌────────────────┐    ┌──────────────┐   │
│   │  scheduler     │ ─▶ │  router        │ ─▶ │  cheap LLM   │   │
│   │  (cron + queue)│    │  (cost-tier    │    │  (~82% calls)│   │
│   │                │    │   classifier)  │    │              │   │
│   └────────────────┘    └────────┬───────┘    └──────────────┘   │
│                                  │                               │
│                                  └──▶ ┌──────────────┐           │
│                                       │  smart LLM   │           │
│                                       │  (~18% calls)│           │
│                                       └──────────────┘           │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │  tools                                                  │    │
│   │   • bmkg.fetchForecast           • tpi.scrape           │    │
│   │   • copernicus.getCurrents       • wa.draft / wa.send   │    │
│   │   • sms.send (Twilio / local)    • koperasi.api         │    │
│   │   • fuelCalc                     • catchHistory         │    │
│   └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## Phase-by-phase data flow

### Pre-trip

1. Fisher opens the agent the night before launch. Connectivity assumed.
2. Cloud scheduler is woken: pulls BMKG 72h forecast, Copernicus current vectors, tide tables.
3. On-device cache supplies the last 10 trips' catch history (voice-logged).
4. Smart-tier call: cross-reference forecast-vs-history → propose bearing + launch window.
5. Cheap-tier calls: format the plan into voice + SMS to the fisher's wife. Cache the plan on the phone for offline reference.

### At sea

1. Phone is the source of truth. Cloud is reachable only intermittently.
2. **Heartbeat loop** (every 4h): GPS read → SMS to family → log on device. Cheap tier only; runs even with no LLM uplink.
3. **Weather-change watcher**: BMKG push (when online) or SMS-pulled forecast every 2h triggers a smart-tier abort-vs-continue decision.
4. **Voice catch log**: 3–5 second mic recording → on-device whisper-id (or queued for cloud) → append to catch history → confirm via TTS.

### Post-trip

1. As phone regains stable signal: cloud orchestrator scrapes TPI auction prices across 3+ nearby ports.
2. Smart-tier call: revenue-at-port-X minus fuel-detour-cost vs revenue-at-port-Y. Pick winner.
3. Cheap-tier call: draft a WhatsApp message to the broker with haul list and ETA. Fisher reviews and sends.
4. Cheap-tier call: append trip P&L (fuel in, hauls out, broker price) to local ledger + cloud sync.

## Cost-routing classifier

A small classifier decides cheap-vs-smart per call. Heuristics:

- **Cheap tier always:** any call that's a fetch, a format, a schedule, an arithmetic computation, or a structured-data log.
- **Smart tier triggers:** abort-vs-continue under weather shift; cross-reference forecast vs catch history; landing-window tradeoff (fuel cost vs price spread); first-time-novel situation flagged by the classifier.

The classifier itself is a 2-line prompt against the cheap tier — recursion is fine because it's measured at <50ms tail.

## SMS fallback protocol

When the phone has no IP connectivity, the agent falls back to a thin SMS protocol:

- **Outbound** (always available via GSM): `HEARTBEAT <lat> <lon> <fuel%>` → SMS gateway → cloud relay → family.
- **Inbound** (cloud → fisher): condensed forecast / TPI alert in <160 chars, prefixed with `NTA:`.

This is intentionally dumb. The fisher should be able to read every byte we send, even if the agent is offline.

## On-device cache schema

```
catch_history.sqlite
  trips(id, started_at, ended_at, fuel_in_l, dock, revenue_idr)
  catches(trip_id, species, kg, lat, lon, recorded_at)

last_forecast.json
  fetched_at, hours, payload[…]

tide_table.json
  port, days[…]
```

Cache is the source of truth offline. Cloud sync is best-effort, idempotent, append-only.

## Privacy & ownership

- The catch history is the fisher's. We do not sell it, we do not aggregate it without opt-in.
- Family GPS heartbeats are sent only to numbers the fisher whitelists.
- Voice clips are processed on-device by default; cloud transcription is opt-in for accuracy gains.

## What we'll prove in M1 field probe

- BMKG forecast accuracy in Pangkep waters vs the fisher's own gut call (paper diary).
- Whisper-id accuracy on Bugis-accented Bahasa Indonesia.
- SMS gateway round-trip latency and cost per heartbeat.
- Whether the abort-vs-continue smart call actually saves fuel vs the status quo.
