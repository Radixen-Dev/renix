# scheduler.md — Proactive Initiation Node

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Purpose

The `scheduler` node is a separate graph entry point for Renix-initiated conversations. It is triggered by an APScheduler job running in a background thread in `main.py`.

When fired, it constructs a `proactive_message` from the configured prompt and any available context (time of day, recent conversation summary), then returns this as a state update. The graph transitions directly to `orchestrator`, which generates a natural spoken message from it.

---

## Configuration

All scheduler behaviour is controlled in `config.yaml`:

```yaml
orchestrator:
  proactive_enabled: true          # Master on/off toggle
  proactive_schedule: "0 * * * *"  # Cron expression (hourly default)
  proactive_prompt: "..."          # The instruction passed to the orchestrator
```

Setting `proactive_enabled: false` disables all proactive turns with no code changes.

---

## State Contract

| Direction | Field | Value |
|---|---|---|
| Output | `proactive_message` | Constructed prompt string |
| Output | `transcript` | `None` (explicitly cleared) |
| Output | `intent` | `None` (explicitly cleared) |

---

## Flow

```
APScheduler job fires → graph.invoke(entry="scheduler") →
  scheduler node → orchestrator → respond → listen
```

The `listen` node is NOT called in a proactive turn. The loop returns to `listen` after `respond` completes, restoring the normal reactive watch.
