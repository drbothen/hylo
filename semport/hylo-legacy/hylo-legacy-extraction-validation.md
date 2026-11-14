# Extraction Validation Report: hylo-legacy

- producer: validate-extraction (fresh-context checker)
- timestamp: 2026-11-14
- scope: `.factory/semport/hylo-legacy/hylo-legacy-pass-0-inventory.md` … `hylo-legacy-pass-6-synthesis.md` (7 files) vs source `$HOME/Dev/hylo/legacy/` (11 files)
- method: full static read of every source file (`dgx_statusline.py`, `dgx_proxy.py`, `dgx_ledger_exporter.py`, `auto_continue.py`, `claude-dgx`, `dgx-proxy-coordinator.sh`, `dgx_preflight.py`, `tools/backfill_cost_history.py`, both plists, `ROLLBACK.md`); every citation in the pass files traced to its line; independent recomputation of all numeric claims with `wc -l`, `git rev-list`, `grep -c`. Nothing in `legacy/` was executed or modified.

## Phase 1 — Behavioral Verification

| Pass | Items Checked | Verified | Inaccurate | Hallucinated | Unverifiable |
|------|--------------|----------|------------|-------------|--------------|
| 0: Inventory / architecture | 31 (file manifest, symbol table, dead code, entry points, anomalies) | 30 | 1 | 0 | 0 |
| 1: Architecture | 47 (components, stdin/transcript field tables, VM query verbatim, 27 metric families, files/paths, interfaces) | 47 | 0 | 0 | 0 |
| 2: Domain model | 41 (23 entities, 12 ledger events + 1 historical alias, 9 vocabularies, field orders, state machines) | 41 | 0 | 0 | 0 |
| 3: Behavioral contracts | 136/136 BCs + ~40 edge sub-claims (required sample was 40; full census taken, all 9 components covered) | 136 | 0 | 0 | 0 |
| 4: NFRs / thresholds | 105 thresholds (value + file:line) + 8 doc-rationale deep checks + 3 rollup counts | 105 | 0 | 0 | 0 |
| 5: Conventions / inventories | 40 env vars, 55 determinism rows, 13 conventions | 94 | 1 (wording) | 0 | 0 |
| 6: Synthesis | 8 owner-decision quirks, 11 cross-pass inconsistencies, 10 porting risks | 18 | 1 (wording, same as pass 5) | 0 | 0 |

Citation spot-check (all line numbers verified exactly): pass 0 symbol table (all ~50 function/class line anchors exact, incl. `heat` 144, `_mix_counts` 999, `_finish_turn` 988, `cmd_trust_*` 625/648/676/702, `_build_parser` 737); pass 3 evidence columns (e.g. BC-SL-041 `:315-359`, BC-PX-020 `:254-282`, BC-PX-031 `:761`, BC-LN-006 `:114-115`, BC-EX-004 `:200`, BC-HK-008 `:64-91`, BC-BF-003 `:78-80`, BC-CO-001 `:14-24`, BC-PF-002 `:25-41`, BC-SV-002 `:4-17`) — every range opens on the claimed construct.

Verbatim-freeze checks (D7):
- Pass 2 LEDGER SCHEMA: all 12 events verified against `ledger()` call sites with field insertion order intact — `bridge_ws_connect` (:100), `anth_request` (:117-141, incl. trailing `lane`), `dgx_request` (:143-154, `model_served` captured pre-rewrite), `anth_reply` (:236-245), `anth_usage` (:246-253), `dgx_reply` (:272-274, `status`/`duration_s` before attribution), `dgx_usage` (:275-282, conditional `cache_read_tok`), `bridge_ws_close` (:213), `*_upstream_error` (:322-323), `ws_closed` (:536, dead), `anth_ratelimit` (:188); historical `anthropic_reply` read by exporter (:206). Encoding claims (separators, `ensure_ascii`, local-time `t`, OSError swallow) all match `dgx_proxy.py:56-62`.
- Pass 1 §4.6 MetricsQL query: reconstructed string matches `dgx_statusline.py:102-123` byte-for-byte (all 16 series names, `up{job=~"vllm|lmcache"}`, both `label_set(alias(...))` arms, `safe=''` quoting at :165).
- Pass 1 §4.7 Prometheus: 27 metric families verified verbatim incl. irregular ones — `dgx_llm_anthropic_request_duration_seconds_count` TYPE-without-HELP (:326), `dgx_llm_session_tokens_in/out/errors` under a `dgx_llm_session_tokens` HELP (:378-387), `ttl="5m"/"1h"` labels (:345-346), conditional `dgx_llm_last_{dgx,anthropic}_request_timestamp_seconds` (:367-374), `session="…"` truncated to 8 chars (:382), `text/plain; version=0.0.4` (:401), `0.0.0.0:9210` (:414), 404 on non-`/metrics` (:272-273).

## Phase 2 — Metric Verification

| Claim | Claimed | Recounted | Delta | Command |
|-------|---------|-----------|-------|---------|
| Total legacy files | 11 | 11 | 0 | `find legacy -type f \| wc -l` |
| Total lines | 3181 | 3181 | 0 | `find legacy -type f -exec cat {} + \| wc -l` |
| Per-file lines (all 11) | 1245/764/414/275/185/50/41/121/13/18/55 | same | 0 | `wc -l legacy/*` |
| Python files | 6 | 6 | 0 | `find legacy -name '*.py'` |
| Test files | 0 | 0 | 0 | `find legacy -iname '*test*'` |
| BCs in pass 3 | 136 (53+31+17+13+11+2+2+5+2) | 136 | 0 | table census |
| Thresholds in pass 4 | 105 (T-001..T-105) | 105 | 0 | table census |
| "UNKNOWN — owner to confirm" rows | 52 | 52 | 0 | `grep -c 'T-[0-9].*UNKNOWN' pass-4` (raw phrase hits = 54 incl. header + totals lines) |
| Env-var inventory inputs | 40 | 40 | 0 | table census |
| Ledger event types written | 11 | 11 | 0 | distinct `ledger(` event literals (plus dead `ws_closed` + read-only `anthropic_reply`) |
| Exporter metric families (synthesis I3) | 27 | 27 | 0 | name census of `dgx_ledger_exporter.py:289-398` |
| Commits touching `legacy/` | **18** | **19** | **+1** | `git rev-list --count HEAD -- legacy` — **FIXED in pass 0** |
| `LOCAL_MODEL_PREFIXES` "three different defaults" | 3 distinct | 3 defaults, 2 distinct values (`claude-sonnet` ×2, `""` ×1) | — | `grep -n LOCAL_MODEL_PREFIXES legacy/*` — **REWORD in pass 5/6** |

## Errors Found and Fixed

| # | File | Original | Actual | Fix |
|---|------|----------|--------|-----|
| 1 | pass 0 (§ Git provenance) | "18 commits touch `legacy/`" | 19 (`git rev-list --count HEAD -- legacy`; first `510c337`, last `220e96c` both correct) | Changed 18 → 19; validation banner added |
| 2 | pass 5 (§2 note) + pass 6 (Key Finding 4) | "three **different** defaults" for `LOCAL_MODEL_PREFIXES` | Three consumer defaults but only **two distinct values** (proxy `claude-sonnet`, backfill `claude-sonnet`, statusline `""`; launcher additionally forces `claude-sonnet`) | Reworded in both files; validation banner added |

No other factual error was found in ~250 checked claims. Cosmetic nits noted, intentionally not fixed: pass 1 §4.5 hook row bundles "up to 3 tries" into the `:94-121` citation (loop lives at `:124-138`, correctly cited elsewhere in the same pass); pass 5 determinism omits `dgx_statusline.py:889` (`time.time()` in the out-of-scope `--subagent` path, which the extraction itself declares out of scope).

## Completeness Sweeps (task item 3)

- ENV inventory: complete. Every `os.environ` read in all 6 Python files maps to a pass-5 row (31 reads, all matched); no `os.getenv` anywhere; all zsh `${VAR:-default}` knobs in `claude-dgx`/coordinator accounted for, as are launcher-exported outputs (`HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`, `API_TIMEOUT_MS`, `CLAUDE_CODE_AUTO_MODE_SERVER`, `PYTHONUNBUFFERED`, `ANTHROPIC_BASE_URL` unset). Nothing missed.
- Determinism inventory: complete. All `time.time` (21 sites), `datetime.fromisoformat/strptime` (4), `subprocess` (proxy trust CLI, statusline `ps`, hook dead `claude -p`), network calls (`urlopen` hook :113, opener statusline :168, `socket.create_connection` preflight :23), `Path.home`/`expanduser`, `os.getppid/getpid`, `mkstemp` randomness, glob ordering, naive-local-TZ parses — each appears with correct file:line. Single omission is the out-of-scope subagent `now_ms` (`:889`).
- Hallucination sweep (task item 5): zero. Every module, file, function, env var, ledger event, metric name and threshold named in the seven passes exists in `legacy/` with the cited line/proximity. Verified examples of the subtlest claims: `_bridge_dur` is only ever read (`:213`), `_ws_started` never set (`:529-534`), `opus_verdict`/`KEV_MESSAGES`/`fetch_sample(sid8)`/`STALE_SEC` all dead as claimed, coordinator referenced only by itself.

## Owner-Decision Quirks (task item 4)

| Quirk | Verdict | Exact evidence |
|-------|---------|----------------|
| `dgx_llm_anthropic_requests_total` account label always `unknown` | CONFIRMED | `dgx_proxy.py:117-127` writes `anth_request` without `account`; exporter `:161-163` defaults `ev.get("account") or "unknown"` |
| `dgx_llm_anthropic_request_duration_seconds_{sum,count}` always 0 | CONFIRMED | `anth_usage` is written without `duration_s` (`dgx_proxy.py:246-253`); exporter `:179-182` sums a field never present → `0.000`/`0` |
| Import-time crash on non-numeric `DGX_SL_TTL`/`DGX_SL_ROWS` | CONFIRMED | Module-level `float(...)`/`int(...)` at `dgx_statusline.py:74-75`, outside the `__main__` guard (:1238-1245); same pattern in hook (:33-36) and exporter (:24-25) |
| Trust `remove`/`rotate` crash at `dgx_proxy.py:761` | CONFIRMED (one nuance) | `:761` is `_build_parser().parse_args(sys.argv[2:]).func(None)`; `rotate` touches `args.force` unconditionally (:703), `remove` only when a keychain entry exists (:684) — crash mechanism exactly as described |
| `profile.env` read after proxy start | CONFIRMED | mitmdump spawned at `claude-dgx:75`; `source "$PROFILE"` at `:114-115` → profile env reaches `claude`/statusline/hook but not the running proxy |
| Three different `LOCAL_MODEL_PREFIXES` defaults | REFINED | Three consumer defaults, two distinct values (proxy/backfill `claude-sonnet`, statusline `""`), launcher forces a fourth site; wording fixed in pass 5/6 |
| `x-api-key` not stripped on the backend lane | CONFIRMED | DGX rewrite only sets `Authorization` (:164), pops `anthropic-beta` (:165); `x-api-key` and other Anthropic headers forwarded |
| Coordinator never invoked | CONFIRMED | `grep -rn coordinator legacy/` → only self-references in `dgx-proxy-coordinator.sh:2-3`; `flock` also confirmed absent from this macOS host (`/usr/bin/flock` missing), as BC-CO-001 notes |

Doc-sourced threshold rationales (task item 2, deep checks): `T-001` "match refreshInterval" = WIDGETS Tunables `DGX_SL_TTL` row verbatim; `T-012` 30.4 MTok = review #11.1; `T-019` "p75 $0.13 from probes" = review #11 revisit; `T-028` 85%→~117K before ~967K = review #5.1; `T-034` "70 = pace, 90 = throttling imminent" = review #12.3; `T-056` "normal max 4,145; smallest rebuild 61,901" = review #10 revisit; `T-082` 0.40 tuned 2026-11-10 after 0.487 = `claude-dgx:150-151`; `T-003` 15 s scrape plausibility = review #16.1. Also corroborated: 9,927-request ledger claim (BC-PX-006, review #1), 93/106 split (BC-SL-034, #10.2), 1.36 MB / 28-of-200 (BC-SL-032, #6.5), sparkline "≈48 s" (I4, WIDGETS).

## Unverifiable Items

| Item | Reason |
|------|--------|
| mitmproxy runtime behaviors (header iteration order, `response` firing on streamed bridge flows, hook-exception handling by mitmdump) | not observable statically; extraction marks these LOW/UNVERIFIED consistently |
| Stop-hook `additionalContext` acceptance by Claude Code (BC-HK-013) | external contract; extraction flags it UNVERIFIED |
| `flock`, `security`, `openssl`, `pgrep` behavior in the trust CLI/coordinator | macOS-shipped-tool behavior; static read only (flock absence verified on this host) |
| BC-PX-006's "9,927 requests consistent" | historical measurement recorded in the review doc, not reproducible from the tree (the number itself exists in the doc) |

## Refinement Iterations: 2/3

Iteration 1: full source read + all-citation trace (no errors beyond commit count). Iteration 2: independent metric recounts + env/determinism/hallucination sweeps + doc corroboration (found the "three defaults" wording; applied both fixes; re-checked cross-references after editing — no orphaned references). Stopped at 2: convergence reached, further passes yielded no deltas.

## Confidence Assessment

- Overall extraction accuracy: ~99% (2 corrections across ~250 checked claims; 100% of pass-3 BC citations, 100% of frozen-format checks)
- Recommendation: **TRUST**

## Verdict

**PASS-WITH-FIXES** — two minor corrections applied (commit count; "three different defaults" wording); the extraction is faithful to the source, including every frozen ledger field order, metric name/label, threshold value and quirk tested.
