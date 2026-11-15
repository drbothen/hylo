# Owner decision list (Phase 0 gate) — hylo-legacy
**Status (2026-11-14):** all 64 issued items DECIDED, plus OD-95 (config/cache/state paths) DECIDED; log in `specs/owner-decisions-log-2026-11-14.md`. Numbering: IDs declared unused stay free; next free OD is OD-96, next free CONV-ABS is 95.

- **Purpose:** every owner decision (OD) issued during Phase 0, ready for one sitting. Each item has a one-line question, the component, the
  phase where it first matters, lettered options, **one** recommendation with a one-line reason, and the evidence location.
- **Scope:** OD-01..OD-94 as issued: **64 items** (2 ruled, 62 pending). Unused or reserved IDs are skipped: OD-44, OD-49, OD-62..65,
  OD-67..73, OD-77..93. Next free ID: OD-95.
- **Answer format:** "OD-06 a", or "A: all recommended" to accept a whole section. "Labeled judgment call" is a valid answer for any
  rationale (policy 16).
- **Rec type:** **KEEP** = keep legacy behavior for parity (D4) through cutover. **DEVIATE** = an approved deviation from legacy behavior (incl.
  Windows-only and failure-mode deviations). **NEW** = no legacy behavior to keep (process, naming, harness or new hylo function).
- **Evidence paths** are relative to `.factory/semport/hylo-legacy/`; `hylo-legacy-` is abbreviated `hl-`. Later amendments are listed after
  the origin. The definitive synthesis is `hl-pass-8-deep-synthesis.md`.
- D1-D16 are settled (policy 12). Nothing below reopens them. Where an item touches a decision's wording (OD-10, OD-14), it asks for a
  clarification only.

## Summary

| Group | Items | KEEP (parity) | DEVIATE | NEW | Ruled | Bites first |
|---|---:|---:|---:|---:|---:|---|
| A. Security and correctness | 12 | 3 | 9 | 0 | 2 (OD-24, OD-27) | P2, P3 |
| B. Parity scope (legacy quirk vs approved deviation) | 19 | 10 | 9 | 0 | 0 | P1, P2, P3 |
| C. hylo architecture (proxy lifecycle, ledger sharing, HTTP/2, timeouts) | 13 | 2 | 8 | 3 | 0 | P3, P4 |
| D. Config and naming | 10 | 6 | 2 | 2 | 0 | P1 |
| E. Threshold rationales (OD-55, OD-57 as 8 answers) | 2 | 1 | 0 | 1 | 0 | P1 |
| F. Plan gaps | 8 | 1 | 2 | 5 | 0 | P1, P3, P4, P6 |
| **Total** | **64** | **23** | **30** | **11** | **2** | — |

The 30 DEVIATE recommendations include the 2 rulings (OD-24, OD-27). Most of the others change failure behavior that recorded inputs do not
reach, so the parity diff does not see them.

**Needed before P1 starts** (status line): OD-01, OD-02, OD-03, OD-05, OD-14, OD-21, OD-30, OD-32, OD-55, OD-56, OD-57 (bulk row + groups
A, B, C, G), OD-58, OD-59, OD-61, OD-74.

---

## A. Security and correctness

| ID | Question | Component | Bites | Options | Recommendation | Type | Evidence |
|---|---|---|---|---|---|---|---|
| **OD-06** | When the backend key file is unreadable, may the request still go to the backend (legacy sends the client's own credentials)? | proxy | P3 | (a) fail closed: local 502 + routing-error event; (b) reproduce legacy | **(a)**: legacy leaks the user's Anthropic credentials to the backend over plain HTTP (`dgx_proxy.py:91-95` after `:161-163`) | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; synthesis §10 L0-01 |
| **OD-07** | Should client `x-api-key`, `Authorization` and cookies be stripped on the local lane before the backend key is added? | proxy | P3 | (a) strip all client credentials; (b) reproduce (forward everything except `Authorization`) | **(a)**: the same credential hygiene D16 applies to the UI; nothing on the backend needs them | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; synthesis L0-02 |
| **OD-08** | Malformed fields (P-R1..R3) silently send a would-be local request to Anthropic. Reproduce? | proxy | P3 | (a) reproduce in replay and also emit a routing-error event; (b) reproduce silently; (c) fail the request | **(a)**: keeps parity and makes the silent re-lane visible on the event stream (not the ledger, D7) | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2 (origin P2r2 #7) |
| **OD-11** | One poison ledger line crash-loops the exporter under KeepAlive. Fix? | exporter | P2 | (a) skip and count bad lines; (b) reproduce the crash | **(a)**: one bad line takes the dashboards down indefinitely; exposition bytes on good input stay identical | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; BC-EX-021 |
| **OD-24** | Proxy listens on all interfaces and admits LAN clients | proxy | — / P3 | — | **RULED 2026-11-14:** legacy LAN risk accepted until cutover; hylo binds loopback by default, non-loopback is opt-in config with a warning (HY-BIND-1/3/4) | DEVIATE (ruled) | `hl-pass-2-deep-domain-r5.md` §0.2, §1 |
| **OD-25** | No correlation key in the ledger: how does the P3 replay pair requests and replies? | proxy, ledger | P3, P7 | (a) composite near-key now (`session, path, model_req, req_bytes` + timing), internal `flow_id` on the event stream, `flow_id` + UTC offset in the P7 schema; (b) add `flow_id` to the ledger now | **(a)**: D7 forbids a ledger change before P7; the near-key works on both lanes and ambiguous pairs are reported | KEEP | `hl-pass-2-deep-domain-r4.md` §3.3; r5 C-6 |
| **OD-26** | On a bad config reload, what does the proxy do (legacy degrades to plain pass-through)? | proxy, config | P3, P6 | (a) keep the last good config, emit an error event, never pass through; (b) reproduce | **(a)**: silent pass-through moves local traffic and its billing to the cloud | DEVIATE | `hl-pass-2-deep-domain-r4.md` §2.1; r5 §0.1 |
| **OD-27** | Exporter binds `0.0.0.0:9210`, unauthenticated | exporter | — / P2 | — | **RULED 2026-11-14:** legacy risk accepted; hylo exporter binds loopback, wider bind opt-in with a warning (HY-BIND-5; exporter inclusion confirmed) | DEVIATE (ruled) | `hl-pass-2-deep-domain-r5.md` §0.2; r6 §3 |
| **OD-33** | One idle connection stalls every exporter scrape (single thread, no socket timeout). Fix? | exporter | P2 | (a) concurrent server with read-header and idle timeouts; (b) reproduce | **(a)**: availability fix with unchanged exposition bytes (HY-BIND-6) | DEVIATE | `hl-pass-2-deep-domain-r5.md` §2.4, §3.2 |
| **OD-34** | Loopback is not authentication: other local accounts can use the proxy and the backend key. Add a per-launch proxy credential? | proxy, run | P3, P4 | (a) optional credential, off by default; verify first that Claude Code honors credentials in `HTTPS_PROXY`; (b) always on; (c) none | **(a)**: protects multi-user hosts without changing default behavior; adoption depends on the verification | KEEP | `hl-pass-2-deep-domain-r5.md` §1.4, §3.2 |
| **OD-41** | Upstream TLS policy: (a) trust anchor, (b) per-backend `ca_file`/`client_cert`, (c) legacy keychain root at cutover, (d) ciphers | proxy, ca | P3, P4, P6 | trust anchor: (a1) OS store + per-backend `ca_file`; (a2) embedded Mozilla snapshot (legacy = certifi); per-backend keys: (b) yes in P6; keychain: (c) `hylo doctor` detects, `hylo ca` offers removal; ciphers: (d) Go defaults, TLS 1.2 minimum as a named constant | **(a1) + (b) + (c) + (d)**: verification is never optional (HY-TLS-1); only TLS-inspection networks and private-CA backends behave differently from legacy | DEVIATE | `hl-pass-2-deep-domain-r7.md` §3, §1.3 T-1; r8 §4, §6 |
| **OD-45** | A decision-log or hook-log write that fails can abort routing or the hook decision. In Go? | proxy, hook | P3, P4 | (a) diagnostic writes never change a routing, ledger or hook outcome (covers both logs, incl. H-09); (b) reproduce the abort | **(a)**: a log write must never change behavior; affected inputs are classified "legacy note-abort" in the replay | DEVIATE | `hl-pass-3-deep-behavioral-contracts-r6.md` §2.3; r7 (H-09) |

## B. Parity scope (keep a legacy quirk vs approved deviation)

| ID | Question | Component | Bites | Options | Recommendation | Type | Evidence |
|---|---|---|---|---|---|---|---|
| **OD-03** | Session ids appear raw in cache file names; sanitize? | status line | P1 | (a) sanitize on Windows only; (b) never; (c) everywhere | **(a)**: Windows rejects some characters; macOS/Linux stay byte-identical | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; BC-SL-052/070/078 |
| **OD-09** | Block types outside the six (e.g. `document`) are silently dropped on the local lane | proxy | P3, P6 | (a) parity now; after cutover a config rule routes such requests to Anthropic; (b) route to Anthropic now | **(a)**: parity first; the post-cutover rule fixes the silent loss | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; BC-PX-012 |
| **OD-12** | Hook crash H-04 (a final failed Kev call after a success) | hook | P4 | (a) fix and document as a deviation; (b) reproduce | **(a)**: a crash returns no decision at all; production-reachable | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; BC-HK-022 |
| **OD-15** | Exporter parity oracle: pin `/usr/bin/python3` 3.9.6 with an empty, launchd-like env? | exporter | P2 | (a) pin 3.9.6; (b) use 3.11.7 | **(a)**: that is the interpreter production runs; parsing differs by version (T-133) | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2 |
| **OD-16** | Client cancels are counted as local-lane errors (4 of 23 in production) | proxy, exporter | P2, P3 | (a) reproduce through cutover, add a `reason` field after; (b) stop counting cancels now | **(a)**: the error metric is a D7 surface; fix it with the P7 redesign | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; r6 §3 |
| **OD-18** | Response-hook crash paths P-S1..P-S4 | proxy | P3 | (a) reproduce the ledger effects of P-S1..S3, approved deviation for P-S4; (b) reproduce all four | **(a)**: S1-S3 are visible in the ledger (D7); P-S4 loses the failed-request capture for no benefit | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; P3r2, P3r3 |
| **OD-21** | Where D4-EX-2 detects the CP-T05 shape | status line | P1 | (a) skip at the opening line; (b) skip at the closing line | **(a)**: also prevents BC-SL-100's poisoned cache | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; BC-SL-098 |
| **OD-22** | Exporter reads naive local `t`, so a DST change produces a false idle | exporter | P2, P7 | (a) accept through cutover, offset or epoch in P7; (b) fix now | **(a)**: the fix needs a schema change (D7) | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; BC-EX-020 |
| **OD-23** | Hook-log tallies can be misattributed (tags inside model text) | exporter | P2, P7 | (a) reproduce in P2, structured hook log in P7; (b) fix now | **(a)**: tallies are a D7 surface | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; BC-EX-019 |
| **OD-28** | Upstream-error **text** in the Go proxy (mitmproxy and OS strings) | proxy | P3 | (a) emit mitmproxy's fixed strings for the deterministic causes (incl. TLS failures, `connection cancelled`, shutdown and inactivity cuts) and declare the text out of byte parity; (b) byte parity for all text | **(a)**: no metric reads the text; OS strings cannot be reproduced across platforms | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; r6 §3; r7 §3, §4.2 |
| **OD-29** | Exporter exposition: hand-written byte-identical vs a Prometheus client library | exporter | P2 | (a) hand-written during parity; (b) library | **(a)**: the irregular HELP/TYPE layout and duplicate series are part of the bytes | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; BC-EX-025 |
| **OD-30** | Numeric session ids create duplicate keys in `cost-history.json` | status line | P1 | (a) known difference: Go writes one key per sid; (b) reproduce | **(a)**: non-production shape; reproducing it requires emulating Python dict quirks | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; BC-SL-079 |
| **OD-31** | Backfill writes NaN usd and has history-shape quirks | backfill | P6 | (a) keep for the one-off tool; `hylo cost backfill` skips non-finite usd; (b) reproduce | **(a)**: NaN in history poisons the percentile colours | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; BC-BF-012 |
| **OD-32** | How Go reads a legacy-written poisoned mix cache (`cur.out` non-numeric) | status line | P1 (shadow week) | (a) treat as no open turn (`cur = null`) when `cur.t0` is a number; (b) crash like legacy | **(a)**: the `t0` condition keeps parity on the `t0`-null form Go itself writes | DEVIATE | `hl-pass-3-deep-behavioral-contracts-r4.md` §5, §1.2 (CONV-ABS-15) |
| **OD-35** | SSE lines longer than 64,000 bytes are not scanned by the tap | proxy | P3 | (a) configurable cap, default 64,000; (b) hard-code | **(a)**: parity default, config per D15 | KEEP | `hl-pass-3-deep-behavioral-contracts-r4.md` §5, §2.2 |
| **OD-39** | Exporter rebuilds only when the ledger size changes (post-read `stat`), so hook-log changes lag | exporter | P2 | (a) record the consumed offset and rebuild when either file changes; harness scrapes after quiescence; (b) reproduce exactly | **(a)**: single-scrape expositions are unchanged; removes stale tallies | DEVIATE | `hl-pass-3-deep-behavioral-contracts-r5.md` §3.1; BC-EX-027 |
| **OD-43** | `bridge_ws_*` events key on a host never seen in production; real Remote Control uses other channels | proxy, ledger | P3, post-P5 | (a) reproduce the dead rule through cutover, then (b) add events for the real channels under new names; (c) drop both after cutover | **(a) then (b)**: cheap, keeps D7, and makes Remote Control visible later | KEEP | `hl-pass-2-deep-domain-r8.md` §2, §6 |
| **OD-60** | An exported `ARGS` variable is prepended to the `claude` argv (zsh accident) | launcher | P4 | (a) do not reproduce (approved deviation); (b) reproduce | **(a)**: no intended behavior; `hylo run` builds argv explicitly | DEVIATE | `hl-pass-5-deep-conventions.md` §E; ENV-43 |
| **OD-76** | Legacy ⌂ is off by 3,600 s for windows started in the repeated DST hour (libc `mktime`) | status line, platform | P1 | (a) deviation: report the true start; (b) emulate libc | **(a)**: the legacy value is wrong and the harness seeds `proc_start` | DEVIATE | `hl-pass-5-deep-conventions-r2.md` §E, §A.1 |

## C. hylo architecture (proxy lifecycle, ledger sharing, HTTP/2, timeouts)

| ID | Question | Component | Bites | Options | Recommendation | Type | Evidence |
|---|---|---|---|---|---|---|---|
| **OD-17** | Upstream connection management (eager CONNECT couples the lanes; no retry on a stale keep-alive) | proxy | P3 | (a) approved failure-mode deviation: lazy per-lane connects, reconnect or backoff, never couple lanes; (b) reproduce mitmproxy's model | **(a)**: an Anthropic outage should not block local requests; the h2 sticky failure is reachable only by non-Claude-Code clients, which D14 removes | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; r7 §3 (HY-PROTO-1); r8 §6 (CONV-ABS-25) |
| **OD-19** | Launcher port race and the unwired coordinator | launcher | P4 | (a) out of parity scope; hylo binds its own listener (state file + lock); (b) reproduce | **(a)**: the coordinator cannot work on the host and the race disappears with one proxy per user | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; `hl-pass-0-deep-inventory-r3.md` §2.2 row 19 |
| **OD-37** | Proxy inactivity ceiling: legacy cuts any flow silent for 600 s, below the 30-minute client timeout | proxy | P3 | (a) deviation: routed lanes in-flight timeout ≥ client API timeout (HY-TIMEOUT-1); pass-through no total cap and no idle cut while streaming (HY-PASS-1); idle cut only for connections with no flow (HY-BIND-6); (b) reproduce 600 s | **(a)**: the cut fired once in production on a live MCP stream, with no ledger trace | DEVIATE | `hl-pass-2-deep-domain-r6.md` §3 (as OD-35), `r7` §3 (renumbered), `r8` §6 |
| **OD-38** | In-flight flows at proxy exit (legacy records them on SIGTERM, not on SIGHUP/SIGKILL) | proxy | P3, P4 | (a) treat SIGHUP like SIGTERM (Windows: console close via `internal/platform`), drain for a bounded deadline, then one error event per remaining flow; (b) reproduce | **(a)**: a shared proxy must not lose flows when a window closes; event names unchanged (D7) | DEVIATE | `hl-pass-2-deep-domain-r6.md` §3 (as OD-36), `r7` §3, §2 |
| **OD-42** | Upstream connect timeout (legacy has none) | proxy | P3 | (a) config key `backend.connect_timeout`, default none until cutover, then a finite labeled judgment value; (b) finite from day one | **(a)**: parity through cutover, then a bound | KEEP | `hl-pass-2-deep-domain-r7.md` §3, §1.4 T-4 |
| **OD-50** | Shared-proxy lifecycle: when does the per-user proxy stop, and how do upgrades reach it? | proxy, run | P4 | (a) run while any `hylo run` client is registered, stop after a configurable idle period, restart on demand, drain before upgrades (OD-38), never fall back to pass-through; (b) never stop; (c) stop when the last `hylo run` exits | **(a)**: bounded resource use without surprising stops | NEW | `hl-pass-1-deep-architecture.md` §C.1 |
| **OD-51** | Per-window routing config under one proxy (legacy windows could each set `DGX_UPSTREAM`, key, ledger) | proxy, run | P4, P6 | (a) per-user profile by default, per-client selection by header as a P6 option; (b) per-client from P4 | **(a)**: windows without overrides get identical routing; document that per-window overrides stop working at cutover | DEVIATE | `hl-pass-1-deep-architecture.md` §C.1 |
| **OD-52** | Shadow-week ledger topology: hylo writes the same file as the Python proxies, or a separate one? | ledger | P3 | (a) same file, one `write()` per line, diff partitioned by the shadow window's `session` values; keep a path key so a separate file stays possible; (b) separate file | **(a)**: dashboards stay complete and the diff stays clean | KEEP | `hl-pass-1-deep-architecture.md` §C.1 |
| **OD-53** | Persistent flow-level diagnostic log (legacy: mitmdump stdout, the only source for several Phase-0 findings) | proxy, events | P3 | (a) on by default, metadata only, size-capped with rotation; (b) off by default; (c) none | **(a)**: keeps the post-mortem source without bodies on disk (D16) | NEW | `hl-pass-1-deep-architecture.md` §C.1 |
| **OD-54** | Pass-through buffering: legacy buffers every non-SSE pass-through response in full, no cap | proxy | P3 | (a) relay pass-through as it arrives; buffer only where the router must read the body, with `proxy.max_buffered_body_bytes` (none through cutover, then a judgment value); (b) reproduce | **(a)**: not observable in byte parity; removes unbounded memory | DEVIATE | `hl-pass-4-deep-nfr.md` §E; CONV-ABS-44 |
| **OD-56** | Semantics of every `*timeout_s` key (legacy: per socket operation; Go: total deadline) | config, status line, hook, proxy | P1, P3, P4 | (a) total deadline equal to the legacy value, documented on each key; (b) emulate per-operation timeouts | **(a)**: not observable on recorded inputs; a total deadline is the safer bound | DEVIATE | `hl-pass-4-deep-nfr.md` §E (F-6) |
| **OD-66** | How the shared proxy is detached from the window that starts it | run, proxy, platform | P4 | (a) `hylo run` spawns it detached (new session/process group, stdio to a log), state file + lock as orphan guard; (b) per-OS user service; (c) legacy child model | **(a)**: works on all three OSes without an installer; (b) can be added as opt-in later | NEW | `hl-pass-1-deep-architecture-r2.md` §B.3, §C.1 |
| **OD-94** | hylo listener HTTP/2 posture | proxy | P3 | (a) HTTP/1.1 only on both legs (explicit `Protocols` settings, ALPN test, warning if a client offers h2); (b) mirror h2 like legacy | **(a)**: Claude Code offers only `http/1.1`; removes 9 h2 tuning rows; Go would otherwise negotiate h2 upstream by default | DEVIATE | `hl-pass-4-deep-nfr-r5.md` §A.7; fact sheet `hl-pass-4-deep-nfr-r7.md` §B.5 |

## D. Config and naming

| ID | Question | Component | Bites | Options | Recommendation | Type | Evidence |
|---|---|---|---|---|---|---|---|
| **OD-01** | Config key naming and the `HYLO_*` derivation rule | config | P1 | (a) derive mechanically: `HYLO_` + upper snake of the dotted key, generated from the registry; (b) hand-picked names | **(a)**: no collisions over 136 keys; one rule to document | NEW | `hl-pass-2-deep-domain-r5.md` §3.2; `hl-pass-5-deep-conventions-r3.md` §B.1 |
| **OD-02** | Status-line glyphs as config | status line | P1 | (a) `statusline.glyphs.*` with legacy defaults; (b) named constants | **(a)**: D15; terminals differ in glyph support | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2 |
| **OD-04** | One `paths.hook_log` key for the hook (writer) and the exporter (reader)? | hook, exporter | P2, P4 | (a) one key, legacy default path; (b) two keys | **(a)**: the two must agree for the tallies to work | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2 |
| **OD-05** | Boolean grammar for env values | config, launcher | P1, P4, P6 | (a) legacy per-variable predicates for `DGX_*`, typed booleans for `HYLO_*`; (b) legacy everywhere; (c) typed everywhere | **(a)**: parity on the alias path, sane values on the new path | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; CV-10 |
| **OD-13** | Price tables (one wrong Haiku price, no Haiku > 100K tier, missing families, exact-label pricing leaves variants unpriced) | backfill, cost | P6 | (a) prices in config keyed by model pattern, legacy values for parity; (b) keep the legacy table | **(a)**: D15 lists prices as config; patterns price variant ids | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2 (C-9) |
| **OD-48** | User label on Windows (`whoami` gives `DOMAIN\user`, which lands in ledger and metric labels) | launcher | P4, P6 | (a) strip the domain, keep the override; (b) keep `DOMAIN\user`; (c) require explicit config on Windows | **(a)**: one label form across OSes; macOS/Linux unchanged | DEVIATE | `hl-pass-0-deep-inventory.md` §6 |
| **OD-59** | Env-value parse quirks on `DGX_*` (https on port 80, schemeless ignored, `nan`/`inf`, negative slices, crashing values) | config | P1-P4 | (a) reproduce for both `DGX_*` and `HYLO_*`; (b) reproduce on `DGX_*` only, validate `HYLO_*` at load; (c) validate both | **(b)**: parity where it is measured; new names fail fast with a message | KEEP | `hl-pass-5-deep-conventions.md` §E, §A |
| **OD-61** | `~` in env-provided paths (legacy expands only defaults) | config | P1-P4 | (a) literal for every source; (b) literal on `DGX_*`, expanded for config-file and `HYLO_*` values; (c) expand everywhere | **(b)**: parity on the alias path; removes a footgun (the plist already shows it) | KEEP | `hl-pass-5-deep-conventions.md` §E; CV-11 |
| **OD-74** | Approve the harmonized key table built on OD-01 | config | P1 | (a) approve as is (`run.preflight.enabled`/`timeout_s`, `paths.failed_capture_dir`, `DGX_PROFILE` → `--profile`); (b) also per-leaf env overrides for maps and comma lists for lists; (c) also reserve `HYLO_PROFILE` now | **(a) plus comma-list encoding from (b)**: no legacy env sets a map; decide `HYLO_PROFILE` in the P4 design | NEW | `hl-pass-5-deep-conventions-r2.md` §E, §C.3 |
| **OD-75** | Out-of-domain timeout values (`DGX_KEV_TIMEOUT` ≤ 0/NaN disables Kev; huge values crash the hook) | config, hook | P4 | (a) reproduce both on `DGX_*`, reject on `HYLO_*`; (b) keep "disabled" on the alias path, reject the overflow range at load on every path; (c) reject all | **(b)**: "0 disables Kev" is a plausible intent; reproducing a crash has no user value | DEVIATE | `hl-pass-5-deep-conventions-r2.md` §E; PR-22 |

## E. Threshold rationales

| ID | Question | Component | Bites | Options | Recommendation | Type | Evidence |
|---|---|---|---|---|---|---|---|
| **OD-55** | Four thresholds are inert at legacy defaults (T-003, T-008, T-009, T-007's effect on gap pruning), and the WIDGETS Health-dot text does not describe default behavior | status line, docs | P1 | (a) keep all four as config keys with a "reachable only when …" note, reproduce exactly, correct the WIDGETS sentence (public doc, owner-gated); (b) drop the inert keys | **(a)**: D15 + D4; the doc should say "green while the latest fetch succeeded; yellow from the first failed fetch" | KEEP | `hl-pass-4-deep-nfr.md` §E; F-1..F-4 |
| **OD-57** | Rationale sign-off for 45 thresholds (policy 16): answer the 8 rows below | all | P1-P4 | per row below | per row below | NEW | `hl-pass-4-deep-nfr-r7.md` §B.4 |

**OD-57 answer rows.** Each row is one answer. The suggested wording is what goes into the key's comment and the docs if you accept it.

| Row | Thresholds | Question | Options | Recommendation |
|---|---|---|---|---|
| **E-0 bulk (18)** | T-003, T-005, T-007, T-008, T-009, T-022, T-025, T-038 (covers T-039), T-050, T-060, T-061, T-064, T-076, T-081, T-088, T-094, T-101, T-119 | Accept all 18 rationales as derived by Phase 0 (one yes/no)? | (a) yes; (b) review individually | **(a)**: each is structural (derived from other values or code), already written out in P4r7 §B.2; T-088 reads "half the per-call timeout counts as slow; judgment" |
| **E-A retention and staleness (3)** | T-004 300 s, T-010 1,800 s, T-035 1.15 × window | Rationale? | (a) suggested wording; (b) your own; (c) a measurement | **(a)** "judgment: 5 min of last-known telemetry; 30 min of plan limits between Claude Code reports; 15 % slack before a reset time counts as bogus" |
| **E-B layout and aesthetics (4)** | T-014 72 cols, T-030 heat HSV, T-046 sparkline colours, T-117 subagent formats (only if OD-14 keeps the path) | Rationale? | (a) "judgment (presentation)"; (b) your own | **(a)** |
| **E-C byte and size budgets (5)** | T-054 512 KiB step, T-059 2,000 chars per image, T-065 64,000 B, T-067 50 M chars, T-085 6,000 chars | Rationale? | (a) suggested wording; (b) your own | **(a)** "judgment: parse step / image estimate / runaway-line guard / disk guard / Kev context budget" |
| **E-D diagnostic text clips (4)** | T-068 600, T-069 300, T-086 400/800, T-089 160/100 | Rationale? | (a) "judgment: log readability"; (b) your own | **(a)** |
| **E-E retention counts (3)** | T-066 20 files, T-074 3 backups, T-077 50 sessions | Rationale? | (a) "judgment: bounded disk / label cardinality"; (b) your own | **(a)** |
| **E-F hook heuristic tuning (3)** | T-090 > 20, T-091 < 200, T-092 12 / 4 and 2 % | Rationale? | (a) "judgment, tuned on observed fake stops"; (b) your own | **(a)** |
| **E-G timeouts and cadence (5)** | T-098 4 s refresh (with T-001), T-100 4 s preflight, T-075 30 s / 0.5 s, T-026 1 s per `ps` call, T-083 2.5 s per socket operation | Rationale? | (a) "judgment"; (b) a kev-4b latency figure for T-083 if you have one | **(a)**, with a kev-4b figure for T-083 if one exists (the basis today is Kev-0.8B only) |

Row count check: 18 + (3 + 4 + 5 + 4 + 3 + 3 + 5 = 27) = 45 thresholds.

## F. Plan gaps

| ID | Question | Component | Bites | Options | Recommendation | Type | Evidence |
|---|---|---|---|---|---|---|---|
| **OD-10** | `count_tokens` for local models goes to the backend, but D13's wording names only `POST /v1/messages` | proxy | P3 | (a) keep the behavior and clarify D13's text to name `/v1/messages/count_tokens`; (b) send `count_tokens` to Anthropic | **(a)**: the behavior is live (5/5 answered 200); only the wording needs a clarification, not a new decision | KEEP | `hl-pass-2-deep-domain-r5.md` §3.2; r3 §4.3; BC-PX-035 |
| **OD-14** | Is `--subagent` / `subagentStatusLine` in Go scope? | launcher, status line | P1, P4 | (a) not ported: `hylo run` does not emit `subagentStatusLine`, BC-SL-097 and CP-A stay OOS; (b) a toggle, default on, for parity | **(a)**: PLAN §3 lists custom agent-panel rows as a non-goal, and Claude Code 2.1.323 removed the setting. Note: the Phase-0 artifacts recommended (b); please confirm | DEVIATE | `hl-pass-2-deep-domain-r5.md` §3.2; coverage audit §5; `docs/PLAN.md` §3 |
| **OD-20** | P6 telemetry backend contract (VictoriaMetrics series the status line expects); the evaluator is unknown | status line | P6 | (a) accept P2r3 §2.3 as the requirement, evaluator as a doc note; (b) defer to P6 | **(a)**: it is the only written contract for row 2 | NEW | `hl-pass-2-deep-domain-r5.md` §3.2; r3 §2.3 |
| **OD-36** | `hylo cost backfill` has no phase in PLAN §7 and no package in §6 | backfill | P6 | (a) schedule in P6 with the cost basis, under the package that owns `cost-history.json` (`internal/statusline` or a shared `internal/cost`), keep the legacy script runnable until then; (b) P1 with the status line; (c) drop | **(a)**: it belongs with the configurable cost basis | NEW | `hl-pass-3-deep-behavioral-contracts-r4.md` §5 |
| **OD-40** | Does P3's "identical routing decisions" mean the decision-log text, or the lane decisions compared as data? | proxy | P3 | (a) lane decisions as data, log text OOS, optionally a semantic check of the decision lines; (b) byte-compare the decision log | **(a)**: no consumer reads the log; the ledger and rewritten requests already carry the decision | NEW | `hl-pass-3-deep-behavioral-contracts-r5.md` §5.2 |
| **OD-46** | Where the UserPromptSubmit language reminder lives | launcher, hook | P4 | (a) the same literal shell command in `--settings`; (b) a `hylo hook prompt` subcommand with the text from config; (c) drop after cutover | **(b)**: one binary, no shell quoting, the same on every OS; output stays JE under BC-LN-009 | DEVIATE | `hl-pass-0-deep-inventory.md` §6 |
| **OD-47** | Proxy venv pin and location for the P3 parity oracle (no venv, no lock file in the tree) | harness | P3 | (a) commit a pinned requirements file under `legacy/` and gitignore `legacy/.mitmenv/` and `legacy/.proxy-state/`; (b) pin in the harness directory and symlink; (c) leave unpinned | **(a)**: the replay oracle is reproducible only with the exact mitmproxy and certifi versions; the ignores prevent committing a venv to a public repo | NEW | `hl-pass-0-deep-inventory.md` §6 |
| **OD-58** | Harness clock design | harness | P1-P4 | (a) the research shim plus masking every `strftime`-derived field; (b) the extended shim: mode 1 (frozen) for P1-P3, mode 2 for the hook's early-stop cases | **(b)**: fewer masked fields, and it is the only way to test the Kev early stop | NEW | `hl-pass-5-deep-conventions.md` §E, §B.2 (CONV-ABS-47/48) |

---

## Cross-references

- Synthesis lessons that depend on these answers: L0-01 (OD-06), L0-02 (OD-07), L0-03 (OD-41), L0-04 (OD-37, OD-42, OD-56), L0-05 (OD-25,
  OD-52), L0-06 (OD-24, OD-27, OD-34), L0-07 (OD-26), L0-08 (OD-11, OD-33), L0-10 (OD-45), L0-11 (OD-94), L0-12 (OD-21, OD-32).
- BCs whose parity status waits on an answer (35): see `hl-pass-3-deep-behavioral-contracts-r4.md` §7.3, "Parity" column values `OD-NN`, plus
  BC-EX-027 (OD-39), BC-PX-046/049 (OD-37), BC-PX-047 (OD-41), BC-PX-048 (OD-45).
- Thresholds whose class depends on OD-94: T-124, T-140..T-147 (`hl-pass-4-deep-nfr-r7.md` §B.2.4).
