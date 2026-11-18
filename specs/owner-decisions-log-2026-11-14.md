<!-- Phase 0 gate decisions by the owner, 2026-11-14. Options and evidence: semport/hylo-legacy/hylo-legacy-owner-decisions.md -->
# Owner decision log (Phase 0 gate, 2026-11-14)

| OD | Decision | Notes |
|---|---|---|
| OD-01 | (a) mechanical HYLO_ + upper-snake of dotted key, generated from the registry | with build-time collision test + unknown-HYLO_* warning; key renames = breaking change with one-release alias |
| OD-02 | (a) statusline.glyphs.* table, legacy defaults | validate: 1 code point + 1 column each; sparkline key = exactly 8 ordered glyphs; themes may layer on later |
| OD-03 | (b) keep legacy as-is (raw sid in session cache, sanitized mix cache) | revisit only if Windows complains; real ids are UUIDs |
| OD-05 | typed booleans (true/false/1/0/yes/no, else error); HYLO_* + config file only; NO DGX_* aliases | owner 2026-11-14: "no one is using this yet", no backwards compatibility. Amends D15 text + P6 row in PLAN.md. Moots OD-59 alias part and OD-01's one-release-alias note. Cutover needs a one-page DGX_*→config migration table + example config.yaml |
| OD-14 | (a) do not port --subagent / subagentStatusLine | BC-SL-097, CP-A01..A03, PR-15 stay OOS; Phase 0 spec kept for a future request |
| OD-21 | (a) skip at the opening line carrying the bad value (CP-T05) | prevents BC-SL-100 poisoned cache; inputs excluded from parity diff, covered by BC-SL-099 tests |
| OD-30 | (a) known difference: Go writes one key per sid | non-production shape; table test pins string-form key |
| OD-32 | (a) poisoned legacy mix cache: treat as no open turn when cur.t0 is a number; keep raw value when t0 null | per CONV-ABS-15/BC-SL-103 |
| OD-55 | (a) keep T-003/T-007/T-008/T-009 as config keys with "only takes effect when..." notes; reproduce exactly; fix WIDGETS Health-dot sentence | PUBLIC DOC EDIT PENDING: docs/STATUSLINE-WIDGETS.md health dot -> "green while the latest fetch succeeded; yellow from the first failed fetch" |
| OD-56 | (a) every *_timeout_s key = total deadline equal to the legacy value, documented per key | doctor may measure latency vs deadline |
| OD-57 E-0 | (a) accept all 18 derived rationales (T-003,005,007,008,009,022,025,038,050,060,061,064,076,081,088,094,101,119) as written in P4r7 §B.2 | T-088 labeled judgment |
| OD-57 E-A | (a) judgment: T-004 "5 min of last-known telemetry before giving up"; T-010 "30 min of plan limits between Claude Code reports"; T-035 "15% slack before a reset time counts as bogus" | may upgrade T-010 to measured from anth_ratelimit gaps later |
| OD-57 E-B..E-G | (a) accept all 6 rows as proposed; T-117 dropped (OD-14); T-065 comment adds derived SSE-tap chunking basis; T-069 comment adds "frozen by D7" | OD-57 complete |
| Class 3 (17) | accept all: KEEP OD-08(+D16 routing-error event),09,16,22,23,29,35,43; FIX OD-12,18(S4 only),19,28,31,39,54,76; OD-15 exporter oracle = /usr/bin/python3 3.9.6 empty env | |
| Class 4 (5) | accept all: OD-04 one paths.hook_log key; OD-13 prices in config by model pattern, legacy defaults, corrected in P6; OD-48 strip Windows domain + override; OD-47 commit pinned requirements under legacy/ + gitignore legacy/.mitmenv/ and .proxy-state/; OD-58 extended clock shim (mode 1 frozen P1-P3, mode 2 stepped for hook early-stop) | |
| Class 7 (5) | accept all: OD-10 keep behavior + reword D13 to name /v1/messages/count_tokens; OD-20 adopt P2r3 §2.3 series list as P6 backend contract; OD-36 backfill in P6 (owner pkg of cost-history), legacy script runnable until then; OD-40 routing decisions = lane decisions as data, log text OOS; OD-46 hylo hook prompt subcommand, text from config | PUBLIC DOC EDITS PENDING: PLAN D13 wording, backfill in P6/§6, P3 routing-decision meaning |
| OD-06 + OD-07 | fail closed on unreadable backend key (local 502 + routing-error event); strip all client credentials (Authorization, x-api-key, Cookie...) on the local lane before adding the backend key | P3; per-backend passthrough only as explicit P6 config |
| OD-41 | (a1) OS store + per-backend ca_file; (b) per-backend ca_file/client_cert in P6; (c) doctor detects legacy mitmproxy CA in login keychain, hylo ca offers removal; (d) Go default ciphers, TLS1.2 min as named constant | HY-TLS-1 verification always on; HY-TLS-3 no implicit SSLKEYLOGFILE |
| OD-26 | (a) bad reload keeps last good config + loud error event; never pass-through; bad config on first start refuses to start | |
| OD-34 | (a) optional per-launch proxy credential, off by default; build only after verifying Claude Code honors creds in HTTPS_PROXY; fallback = peer-uid check (P4) | doctor may suggest on multi-user hosts |
| OD-11 + OD-33 | (a) exporter skips and counts bad ledger lines (log + doctor, no new metric per D7); (a) concurrent server with read-header + idle timeouts (HY-BIND-6) | exposition bytes unchanged on good input |
| OD-45 | (a) diagnostic writes (decision log, hook log) never change routing, ledger or hook outcomes; failures surfaced as error events/doctor | replay classifies "legacy note-abort" inputs; ledger encoder must match Python invalid-UTF-8 handling |
| OD-37 + OD-42 | (a) routed lanes in-flight timeout >= client API timeout (HY-TIMEOUT-1); pass-through: no total cap, no idle cut while streaming (HY-PASS-1); idle cut only for connections with no flow (HY-BIND-6); (a) backend.connect_timeout key, none until cutover then finite judgment value | TCP keepalive upstream; D16 shows open streams |
| OD-25 | (a) P3 replay pairs by composite near-key (session,path,model_req,req_bytes + timing) and reports ambiguous pairs; internal flow_id on event stream (D16); P7 adds flow_id + UTC offset to ledger | D7 respected |
| OD-94 | (a) HTTP/1.1 only, set explicitly on listener and upstream transports (Server.Protocols / Transport.Protocols); proxy.http2.enabled config key default off | T-124, T-140..147 -> N/A; test asserts negotiated protocol on both legs |
| OD-17 | (a) lazy per-lane upstream connects after routing; reconnect/backoff on stale keep-alive only when nothing was sent; never couple lanes | approved failure-mode deviation |
| OD-66 + OD-50 + OD-38 | (a) hylo run spawns proxy detached (own session/pgroup, stdio to log), state file + lock orphan guard; (a) runs while any hylo run client registered, stops after configurable idle period, restarts on demand, drains before upgrades, never pass-through; (a) SIGHUP=SIGTERM (Windows console close via internal/platform), bounded drain, one error event per remaining flow, D7 names | per-OS user service = later opt-in |
| OD-51 | (a) one per-user profile by default; per-window profile selection (header set by hylo run --profile) as P6 option; document per-window env overrides end at cutover | |
| NO SHADOW WEEK | owner 2026-11-14: full cutover, no shadow week | PUBLIC DOC EDIT PENDING: PLAN P3 exit criterion drops the shadow week (replay only). Live checks happen in P4 (full session per OS, Remote Control); P5 keeps Python runnable 2 weeks for rollback. Q-b still needed for rollback; OD-32 still needed once at first run |
| OD-52 | MOOT (no shadow week): hylo is the only ledger writer after cutover | paths.ledger stays config |
| OD-53 | (a) persistent per-flow diagnostic log, on by default, metadata only (no bodies/headers), size-capped with rotation, private state dir with user-only perms, query strings dropped by default | level/cap config, can be disabled |
| Class 2 (4) | accept all: OD-59 HYLO_*/config values typed + validated, fail fast naming the key (alias half moot); OD-60 ARGS leak not reproduced (hylo run builds argv); OD-61 expand ~ in every path value; OD-75 explicit hook.kev.enabled switch + hook.kev.timeout_s must be >0 and < 30 s hook limit, else load error | logged late (accepted earlier in session) |
| Class 3 IDs (explicit) | OD-08 OD-09 OD-16 OD-22 OD-23 OD-29 OD-35 OD-43 (keep) ; OD-12 OD-18 OD-19 OD-28 OD-31 OD-39 OD-54 OD-76 (fix) ; OD-15 (oracle) | see Class 3 row |
| OD-24 / OD-27 | RULED earlier: legacy LAN exposure accepted until cutover; hylo binds loopback by default (HY-BIND) | |
| OD-74 | (a) approve harmonized key table (run.preflight.enabled/timeout_s, paths.failed_capture_dir, DGX_PROFILE -> --profile) + comma-list encoding for list values in env; maps config-file only; HYLO_PROFILE decided in P4 profile design | |
| OD-95 (new, from consistency audit F-01) | (a) keep PLAN paths, built explicitly in internal/platform: ~/.config/hylo, ~/.cache/hylo, ~/.local/state/hylo honoring XDG_CONFIG_HOME/XDG_CACHE_HOME/XDG_STATE_HOME on macOS+Linux; %APPDATA%/%LOCALAPPDATA% on Windows; HYLO_CONFIG / --config override; hylo config path prints paths | |

<!-- Phase 1 market-intel review rulings by the owner, 2026-11-15 -->

| OD-96 | (a) P1 success criterion = the owner's own daily use (byte parity on the owner's setup) | community adoption is a P6 concern, not a P1 gate |
| OD-97 | (a) README positioning "lane-aware with backend telemetry and owned-hardware cost" + honest Alternatives section, approved in principle | written at P6 |
| OD-98 | (a) no stdin `version` session-cache key until after parity | D4; session cache schema stays legacy (mixv6 marker, raw-sid session cache name) |
| OD-99 | (a) `7d_oi` Fable-only claim stays a watch note | no work scheduled |
| OD-100 | feature_type = cli | brownfield-design-system-extract skipped (condition not met) |

<!-- Porting-tension rulings by the owner, 2026-11-15 (brownfield/porting-decision.md §8) -->

| OD-101 | (a) tension 5 (cache location): hylo uses its real OD-95 location from P1 on — ~/.cache/hylo honoring XDG_CACHE_HOME on macOS+Linux, %LOCALAPPDATA%\hylo on Windows, built in internal/platform; paths.cache_dir remains a config key | owner rationale: "cut over is instant", so there is never a dual-writer period and nothing to flip later; explicit owner exception to D15's "defaults equal legacy/ until cutover" for this one key. PUBLIC DOC EDIT PENDING (PLAN D15 text) — not committed to public main until the owner asks |
| OD-102 | (a) tension 1 (BC-SL-087 vs OD-05): any invalid setting (malformed number, non-typed boolean, bad URL/enum) renders a one-line status line `hylo: config error: <key>=<value> (<reason>)`, exit 0, details on stderr, via the degraded-ladder output path | approved deviation **D4-EX-3** (legacy crashes at import: traceback, exit 1, blank status line); excluded from the parity diff; one table test per key class (number, boolean, URL, enum); `hylo config validate` exits non-zero for the same errors. PUBLIC DOC EDIT PENDING (PLAN lists of approved differences) |
| OD-103 | (a) tension 2 (helper-package granularity): parity helpers are ONE Go package `internal/pyfmt` with four files — number formatting/rounding, json.dumps bytes, code-point string ops, strftime/localtime | either shape satisfies risk R3 (§8 tension 2); owner picked the research-Q2 single-package fold over pass-8's four-helper naming |
| OD-104 | (a) tension 3 (oracle pin): P1 parity oracle = CPython 3.11.x; the harness never discovers Python from PATH — the interpreter is an explicit harness setting; CI installs 3.11 on all three OSes | verified locally 2026-11-15: the launcher runs `python3` from PATH; an interactive terminal resolves it to CPython 3.11.7, while a login/non-interactive shell resolves a newer interpreter. Resolves research open question O1; the P2 exporter keeps its separate 3.9.6 oracle (OD-15) |
| OD-105 | (a) tension 4 (approved differences inside a byte-parity phase): the parity harness carries a named exclusion list — D4-EX-1 (⌂ on Windows), D4-EX-2 (wrong-shape transcript lines), D4-EX-3 (config-error line) | each excluded case must match its own expected output in dedicated table tests; an exclusion without a test fails the harness; no blanket exclusions |
| OD-106 | (a) cost history after OD-101: a documented one-time copy of cost-history.json from the legacy cache dir to hylo's cache dir at cutover, as a P5 acceptance criterion | no import code in hylo; `hylo cost backfill` (P6) can rebuild from the ledger |

<!-- Semport-tension rulings by the owner, 2026-11-15 (semport/hylo-legacy/statusline-target-design.md §7.1 T1-T10; resolutions appended to the design doc) -->

| OD-107 | (T1, T6, T7) no live use of `hylo statusline` in real sessions before the instant P5 cutover. AMENDS OD-96: the P1 success criterion is byte parity on the owner's real recorded inputs (local, git-ignored captures/ — copies of real transcripts and status line stdin), plus the synthetic fixture corpus in CI; daily live use starts at cutover. The harness replays sequences of stdin snapshots from a captured session, not only single frames. P1 config = HYLO_* env + built-in defaults; the config-file layer and its YAML dependency arrive in P4 (research Q5), completing D15's file -> env -> default order before cutover | `hylo config validate` and `hylo config path` ship in P1 (OD-102, OD-95). T1 and T7 are moot under this ruling; T6 confirmed |
| OD-108 | (T4) CI passes the absolute interpreter path reported by setup-python (OD-104: the harness never discovers Python from PATH) | the research Q7 recipe (`HYLO_PARITY_PYTHON=python`) is superseded |
| OD-109 | (T5) the oracle runs with `-s`, never `-I` — `-I` ignores PYTHONPATH and would silently disable the sitecustomize clock shim (OD-58) | the harness constructs the child environment from scratch (no inherited vars); a canary test fails the harness if the shim did not load |
| OD-110 | (T2) every owner-ruled byte difference gets a named entry in the OD-105 exclusion list with its own table tests: D4-EX-1/2/3 plus OD-30 (single string key for the numeric session id), OD-76 + the native process probe on macOS/Linux (true start in the repeated DST hour; ⌂ where legacy's localized `ps` fails), and Go cleaning up temp files legacy leaks (excluded only from the cache-file comparison, since stdout is unaffected) | still no blanket exclusions |
| OD-111 | (T3) `routing.local_model_prefixes` default = `claude-sonnet` (production always sets it via the launcher; one key, one default) | parity cases for an unset prefix set an explicit empty value |
| OD-112 | (T8) any unknown flag on `hylo statusline` (incl. a leftover `--subagent`) renders the one-line error format `hylo: unknown flag ...`, exit 0; never blank, never non-zero (same rule as D4-EX-3) | Go stdlib `flag` with `ExitOnError` (exit 2, blank line) must be adapted to this contract |
| OD-113 | (T9) add `statusline.theme.*` config keys for the SGR palette, pill codes and separator (SL:127-134) with the legacy values as defaults | D15 names colors explicitly |
| OD-114 | (T10) every config key states its type and range with rationale in the schema (D15) | config errors (D4-EX-3) include: TTL `nan`/`inf`/negative, `4_0`-style underscores, Unicode digits, unknown TRACE values, non-http(s) metrics URL; TTL `0` (always fetch) stays valid |

<!-- Phase 1 scope rulings by the owner, 2026-11-15 (create-brief discovery; recorded in specs/product-brief.md) -->

| OD-115 | (a) Phase 1 scope ruling: the product brief and the L2 domain spec are product-level (they describe all of hylo); the PRD, behavioral contracts, verification properties and architecture detail produced in this Phase 1 cycle specify P1 (the status line) only; later phases enter the pipeline individually via Feature Mode | discovery done with the owner; grounds the greenfield-pipeline sub-workflow scoping |
| OD-116 | (a) personas: PRIMARY = the owner — a Claude Code subscriber with a dedicated vLLM-class local inference server on the LAN, who wants some models served locally inside the same session; SECONDARY (arrives in P6) = other Claude Code users with local inference (llama.cpp, Ollama, LM Studio, SGLang) who want hybrid routing without losing Remote Control | product-brief.md "Who Is It For?" |
| OD-117 | (a) success targets: (1) parity P1-P3 = 0 unexplained byte/decision diffs vs legacy/ (named exclusion list only, OD-105/OD-110); (2) status line p95 render <= 25 ms on the owner's Mac excluding the metrics HTTP wait, vs the measured legacy baseline (median 84.5 ms) — labeled JUDGMENT CALL (≈3× faster; static binary removes interpreter start); (3) cutover P5 = 100% of the owner's windows on hylo, 0 rollbacks in the 2-week rollback window — labeled judgment call; (4) proxy overhead P3 = deferred until the prototype is measured, number set in Feature Mode | targets (2) and (3) are the two labeled judgment calls; product-brief.md Success Criteria |

<!-- Domain-spec validation rulings by the owner, 2026-11-15 (specs/domain-spec/owner-validation-list.md VALID-01..13; rulings carried inline in the shards; next free OD-131) -->

| OD-118 | (VALID-01, terms) (a) the qualified readings in ubiquitous-language §3 are canonical for the overloaded terms: plan window / client window / process-age window (⌂); session id (raw/sanitized cache-key forms per OD-03) | adopted as proposed |
| OD-119 | (VALID-02, terms) (a) cloud lane/server-tools — a sub-outcome of the cloud lane (routing R4), not a third lane | adopted as proposed |
| OD-120 | (VALID-03, terms) (a) Backend = the server, local lane = the lane; pass-8 L0 items already use backend.* config keys | adopted as proposed |
| OD-121 | (VALID-04, entities) (a) client-view lane is a distinct derived value object; widgets state which view they render; the proxy decision stays authoritative for ledger/BC8 history | adopted as proposed |
| OD-122 | (VALID-05, HIGH) (a) P4 web UI and P6 terminal UI are live + in-memory ring buffer only (exact flow_id correlation, EVT-14); ledger-backed history waits for P7's schema (flow_id + UTC offset, OD-25) — near-key history inherits retry ambiguity (DI-006); ring-buffer size is a config key (D15); the UI states where its history begins | adopted; HIGH |
| OD-123 | (VALID-06, HIGH) (a) N backends in config from the start (name, url, protocol flavor, credential, CA, routing rules); P1-P5 run with exactly one entry, validated — zero or more than one entry is a config error until P6; P6 activates the fleet (CAP-018). For P1 the status line's metrics URL and model-prefix keys live under the backend entry (backends[0].metrics_url, backends[0].model_prefixes), not as top-level singletons — SUPERSEDES OD-111's top-level key placement; OD-111's claude-sonnet default stands | adopted; HIGH |
| OD-124 | (VALID-07, entities) (a) cost history is a status-line-owned shared artifact: the status line owns the format; backfill and the one-time cutover copy (OD-106) honor the format as guests | adopted as proposed |
| OD-125 | (VALID-08, HIGH) (a) DI-007 (the status line never reads the ledger file) is in force: live per-request data may reach the status line only via exporter metrics or the D16 event feed — ADOPTED FOR NOW WITH A REVISIT FLAG; REVISIT at P7 (ledger redesign; allowing ledger-backed widgets then would amend DI-007 and add a BC7←BC4 dependency); revisit flag recorded in invariants.md next to DI-007 | adopted for now; REVISIT at P7 |
| OD-126 | (VALID-09, invariants) (a) legacy usage capture (SSE tap only; a non-streamed local reply contributes no usage event) preserved through parity (P1-P5); revisit at P6 with per-backend rules (small, config-gated) | adopted as proposed |
| OD-127 | (VALID-10, invariants) (a) opt-in cloud failover when the local lane fails stays out of the domain model for now; adopt (if ever) as P6 opt-in config, visible on the status line, with the billing caveat | adopted as proposed |
| OD-128 | (VALID-11, state machines) (a) proxy registration = launch-time claim + periodic heartbeat in the state file; liveness = heartbeat freshness; exact mechanism is a P4 architecture detail; domain commitment: a client can die without taking the proxy down | adopted as proposed |
| OD-129 | (VALID-12, state machines) (a) connect-on-demand for pass-through too, same never-couple rule; no eager upstream connect anywhere | adopted as proposed |
| OD-130 | (VALID-13, telemetry) (a) OWNER AMENDMENT: treat +Inf/-Inf telemetry samples as unknown, like a stale sample (defensive parse); a real capture of one metrics response from the owner's backend (read-only) is taken only after the owner confirms the backend soak has been scored; until then the defensive rule stands | adopted with owner amendment |

<!-- PRD subsystem-breakdown ruling by the owner, 2026-11-15 (create-prd stage-1 allocation; BC id scheme and three-stage writing; next free OD-132) -->

| OD-131 | (a) PRD subsystem breakdown approved: ACTIVE in this PRD — S1 Status line (HIGH; ss-01 input/output contract, ss-02 row-1 widgets, ss-03 transcript parsing, ss-04 row-2 telemetry + metrics client, ss-05 cost history + colors, ss-06 session caches), S2 Configuration (HIGH), S3 Platform (MEDIUM), S4 CLI (MEDIUM), S5 pyfmt (HIGH), S6 Parity harness (HIGH); RESERVED for later phases — S7 exporter (P2), S8 proxy & routing (P3), S9 ledger (P3), S10 launcher/hook/doctor/CA (P4), S11 UIs (P4/P6), S12 multi-backend (P6). BC ids are BC-S.SS.NNN carrying a legacy_id back-reference to the BC-SL contracts; the PRD is written in three stages (allocation / parallel create / integrate) | PENDING OWNER ITEM: module-criticality.md tiers S1 and S5 as CRITICAL (coverage >= 95%) while this ruling says HIGH — reconcile with the owner; neither document changed yet |

<!-- PRD open-question rulings by the owner, 2026-11-15 (prd.md §10 OQ-1..OQ-14 resolved; OQ-3 deferred; next free OD-146) -->

| OD-132 | (a) `config path` prints config/cache/state (OD-95) | |
| OD-133 | (a) window-age process name becomes config key `statusline.window_age.process_name`, default "claude" | D15 |
| OD-134 | (a) OD-114 config-error classes extended with theme "not an SGR parameter list" | |
| OD-135 | (a) S1 and S5 criticality CRITICAL (coverage >= 95%); amends OD-131 labels | resolves the OD-131 pending criticality item |
| OD-136 | (a) CP-X03 degraded-line write failure -> Go exits 0 | named exclusion `cp-x03` in the OD-105 list, with its own table test |
| OD-137 | (a) durations beyond int64 byte-exact via `math/big` | at the two duration-format sites |
| OD-138 | (a) NaN usd in cost history pinned to legacy bytes | from the CPython 3.11 oracle |
| OD-139 | (a) symlinked-binary process name deferred to the per-OS probe test | ruling only if names differ |
| OD-140 | (a) dedicated boolean-parsing BC | BC-2.02.006 |
| OD-141 | (a) six pyfmt helper BCs | BC-5.01.004/005/006, BC-5.02.005/006, BC-5.04.003 |
| OD-142 | (a) json.dumps oracle table regenerated by script from CPython 3.11 | row 53 = 38 bytes |
| OD-143 | (a) turn-table row T13 confirmed by the oracle, stays | 20 rows |
| OD-144 | (a) relative/empty XDG_* ignored | Windows %LOCALAPPDATA%\hylo\cache and \state subdirs |
| OD-145 | (a) harness names/timing/test names/seed paths delegated to the architect | decided in create-architecture |

<!-- Architecture rulings by the owner, 2026-11-15/16 (create-architecture; next free OD-150) -->

| OD-146 | (a) architecture sections approved: ARCH-00 overview, 01 binary/CLI, 02 configuration, 03 status line, 04 data/files, 05 platform, 06 pyfmt, 07 parity harness, 08 build/CI/release, 09 reserved boundaries P2-P7 | |
| OD-147 | (a) inert key statusline.window_age.ps_timeout_s removed | |
| OD-148 | (a) parity fixtures stay with the subject package; runner internal/parity is generic (AD-13) | |
| OD-149 | (a) Tier C exit = one clean nightly fuzz run on all three OSes, 30 min per OS | owner judgment call |

<!-- CI/CD ruling by the owner, 2026-11-16 (next free OD-151) -->

| OD-150 | (a) phase-1-cicd-setup lands via branch ci/phase-1-setup in a worktree; the owner reviews before commit; branch protection on main applied only after the first green CI run, requiring the checks lint (gofmt + vet), test (ubuntu-24.04), test (macos-15), test (windows-2025), gitleaks (full history), with admin bypass (enforce_admins false) | |

<!-- CI/CD merge rulings by the owner, 2026-11-16 (next free OD-152) -->

| OD-151 | (a) PR #1 merged with admin override (squash) by owner instruction; GitHub's squash commit carried the owner's personal email as author; owner approved rewriting that one commit with the no-reply identity and force-pushing main (owner ran the push; 570a0fc -> fd031da, same tree and parent), then applying branch protection per OD-150 | |

<!-- Consistency-audit fix rulings by the owner, 2026-11-17 (consistency audit report cycles/phase-1-spec-crystallization/consistency-audit-2026-11-17.md; next free OD-155) -->

| OD-152 | (CA-04) (a) mint an ASM/R register pair instead of waiving the gate criteria — specs/prd-supplements/assumptions-register.md (ASM-001..006) and specs/prd-supplements/risk-register.md (R-001..007) | adopted as proposed |
| OD-153 | (CA-03) (a) the 14 S6 parity-harness BCs keep capability CAP-009 with a stated rationale (verification machinery proving CAP-009 byte parity; governed by DI-012); no new L2 capability added | adopted as proposed |
| OD-154 | (a) fix all remaining consistency-audit findings (CA-01..CA-12) in one burst before phase-1-gate | adopted as proposed |
<!-- Phase-1d pass-2 owner rulings, 2026-11-17 (adversarial spec review pass 2 NOT_CONVERGED, 116 findings; next free OD-160). Open item closed 2026-11-17: owner confirmed both GitHub email settings on ('Keep my email addresses private', 'Block command line pushes that expose my email') -->

| OD-155 | (a) reopen OD-14 (a): port `--subagent` / subagentStatusLine agent-panel rows in P1 now, before Phase 2 stories, with a config off switch | Claude Code 2.1.326 restored the setting; supersedes OD-14 (a) |
| OD-156 | (a) OverflowError handling split by source: transcript-borne overflow skips the line (extends D4-EX-2, like Q-c); stdin/metrics overflow at render follows catalogued crash paths and reproduces the 29-byte degraded line (like O2); ints beyond int64 in `_fmt_lines` via `math/big` (extends OD-137) | rules the pass-1 held question (C01/B05/B06) |
| OD-157 | (a) OD-130 (±Inf telemetry treated as unknown) takes effect after cutover (P6); P1 keeps legacy behavior | rules the pass-1 held question (A2-01 + VP-030) |
| OD-158 | (a) S1/S5 gate is line coverage >= 95% (OD-135 as written); mutation kill rate >= 95% is a Phase 6 target, reported but not gating P1 | rules the pass-1 held question (A08) |
| OD-159 | (a) Go reads files as UTF-8 on all OSes, as a named deviation | like D4-EX-1; rules the pass-1 held question (B08/C06) |

<!-- Phase-1d pass-2 remediation rulings by the owner, 2026-11-17 (owner chose the recommended option each time; next free OD-166). Closed exclusion set after OD-160/OD-161: 10 ids — D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161 -->

| OD-160 | (a) foreign-cache shapes (ruling Q-b, CP-C01..C10) get the named exclusion id OD-160 in the closed set; vectors relying on hand-edited caches are Go table tests, not byte-parity | adds OD-160 to the closed exclusion set (now 10 ids) |
| OD-161 | (a) an integer `transcript_path` is treated as no transcript; hylo never reads or closes a descriptor it did not open | adds OD-161 to the closed exclusion set (now 10 ids) |
| OD-162 | (a) every config key has a valid range derived from legacy semantics; keys whose non-default behavior cannot be defined have range = default only; out-of-range values are config errors (number-range class) | |
| OD-163 | (a) a save removes only the temp file it created when its write or rename fails (OD-110 as ruled); no sweeping of other temps | |
| OD-164 | (a) int64 overflow and the Duration ceiling are D4-EX-3 number-range cases (covered by OD-114) | |
| OD-165 | (a) `hylo config path` prints effective paths (overrides applied) | |

<!-- Phase-1d pass-3 remediation rulings by the owner, 2026-11-18 (owner chose the recommended option each time; next free OD-169) -->

| OD-166 | (a) a cost value (`usd` or `api_ms`) that cannot convert to float is not recorded in the cost history; the current refresh still degrades (OD-156); prevents a cross-session sticky crash | named deviation under OD-156 |
| OD-167 | (a) a transcript-borne overflow skips the offending line AND drops the in-flight turn, so later lines parse normally (refines OD-156 / D4-EX-2) | |
| OD-168 | (a) a config error in `--subagent` mode prints zero bytes on stdout and the error on stderr (the main status line still shows the D4-EX-3 line) | |

<!-- Phase-1d pass-4 remediation rulings by the owner, 2026-11-17 (owner chose the recommended option each time; next free OD-176). Closed exclusion set after OD-169: 11 ids — D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166 -->

| OD-169 | (a) OD-166's cost-history divergence gets its own closed-set exclusion id `OD-166`. The closed set becomes 11 ids: D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166. Scope: cost-history bytes written after a refresh whose `usd` or `api_ms` could not convert to float; nothing else. It needs its own table test and a VP-012 closure row. Remove every "rides D4-EX-2" and "named deviation under OD-156" wording for this case. | rules ADV-P4-A16, A2-04, C2-03 |
| OD-170 | (a) hylo carries its own Unicode 14.0 tables (decimal digit Nd, printable, whitespace, and any other class pyfmt consults), generated from CPython 3.11.7 `unicodedata` by a committed generator script run under `go generate`. pyfmt never consults Go's `unicode` package for these classes. A version constant (`14.0.0`) and a test pin the tables to the oracle; CI fails if the generated file is stale. P6 may move to current Unicode. | rules ADV-P4-D14 |
| OD-171 | (a) hylo resolves its local zone through `internal/platform`, honouring `TZ` on every OS (load the named zone; fall back to the OS zone when `TZ` is unset or unparseable). The parity harness pins `TZ=UTC` for both binaries; the Windows leg runs the naive local-time cases with no skip (remove VP-026's `posix-only` tag). Table test: TZ unset / `UTC` / IANA name / unparseable. Documented limitation: POSIX-style TZ strings (e.g. `EST5EDT`) may differ from MSVC on Windows; parity cases use `TZ=UTC` only. | rules ADV-P4-A2-06, D21 |
| OD-172 | (a) `cp-x03` extends to `--subagent` row writes: a stdout write failure while printing rows stops writing and exits 0 (no degraded line attempt). No new id. | rules ADV-P4-C13 |
| OD-173 | (a) The lane-pill words become config keys `statusline.pill.label_local` (default `DGX`), `statusline.pill.label_cloud` (default `ANTH`), `statusline.pill.label_unknown` (default `?`). Drop the D7 citation. Range: non-empty, no control bytes, display width 1..16 (judgment call: keeps the pill short). | rules ADV-P4-B16 |
| OD-174 | (a) Rename `cost.basis_min_shown_usd` to `statusline.cost.display_floor_usd`; delete the disclaimers. | rules ADV-P4-B21 |
| OD-175 | (a) `statusline.queue.yellow` is ratified as a P1 Bool key, default `true` = legacy rule (yellow when queue > 0 or preempt > 0); `false` = never yellow. Replace the phantom "2026-11-18 owner ruling" citation with OD-175. | rules ADV-P4-D26 |

<!-- Phase-1d pass-5 remediation rulings by the owner, 2026-11-18 (owner chose the recommended option each time; next free OD-181) -->

| OD-176 | (a) Convergence keeps the full VSDD standard: every finding of every severity is fixed each pass, and convergence needs three consecutive passes with only cosmetic findings. No severity gate, no scope freeze. | process question after pass 5 |
| OD-177 | (a) Refines OD-171 to libc semantics on every OS: `TZ` unset → OS zone; `TZ` empty or unparseable → UTC. | rules ADV-P5-A2-06, D23 |
| OD-178 | (a) A seventh D4-EX-3 class **Text** covers composite-shape, pill-label, glyph and empty-text errors, with exact reason strings in the vocabulary and its own table test `TestD4EX3_Text`. Canonical D4-EX-3 tests become `TestD4EX3_Boolean`, `_Enum`, `_URL`, `_Number`, `_Text`. | rules ADV-P5-D05, A06 |
| OD-179 | (a) The reroute-all markers become the List key `statusline.lane.reroute_all_prefixes` (default `["claude", "claude-"]`, legacy). Range: every entry non-empty, no control bytes. | rules ADV-P5-B09 |
| OD-180 | (a) A metrics URL with userinfo reproduces legacy: no sample (the dead rung); no exclusion id. | rules ADV-P5-C2-03 |

<!-- Phase-1d pass-6 remediation rulings by the owner, 2026-11-18 (owner chose the recommended option each time; next free OD-188). Closed exclusion set after OD-181: 12 ids — D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166, OD-181 -->

| OD-181 | New closed-set exclusion id `OD-181` "metrics transport beyond plain http": non-http(s) redirect targets (hylo: no sample) and TLS trust-store differences for https (hylo: OS trust store). Parity cases use plain http only; table tests pin hylo's behaviour. Closed set = 12 ids. | C2-07, C2-08 |
| OD-182 | VP Go blocks are non-normative: each is labelled "Illustrative sketch (non-normative, not compiled; OD-182)". Normative VP content = property statement, oracle, method, inputs, pass/fail rule, reviewed at full severity. A sketch that contradicts its property is a defect in the sketch; sketch-only defects (syntax, API spelling) are cosmetic. A property that is only clear from its sketch is a HIGH defect against the statement. Phase 3 test-writers write real tests from the property. | A2 sketch class |
| OD-183 | OD-159 (UTF-8 everywhere) extends to stdin and stdout: hylo reads and writes UTF-8 on every OS. The Windows oracle gets exactly one extra variable, `PYTHONIOENCODING=utf-8` (stdio only; `PYTHONUTF8` stays forbidden). Stated in BC-6.01.002, ARCH-07, VP-034, BC-1.01.008, with a table test that it changes stdio encoding only. | A03 |
| OD-184 | Glyph columns are measured in legacy's render width (code points, the count legacy's layout uses): every `statusline.glyphs.*` / `statusline.subagent.glyphs.*` member is exactly 1 code point, except `statusline.glyphs.sparkline` = exactly 8 ordered code points. The East-Asian-Width validation width (OD-170 tables) applies only to the pill-label 1..16 bound (OD-173). | A04, D02, D03 |
| OD-185 | OD-104 stands: CI installs Python 3.11.x (latest patch); the exact-3.11.7 pin from pass-5 call 6 is withdrawn. Because measured constants (JSON depth limits, Unicode 14.0 tables) were taken on 3.11.7, the harness self-checks them against the resolved oracle at start (measure the depth boundaries and `unicodedata.unidata_version`; fail closed on any mismatch, printing the resolved version), and golden metadata records the resolved patch. | A02, D16 |
| OD-186 | The `temp-file` exclusion's scope is widened by ruling to cover the Windows sharing-violation rename-retry outcome (hylo may persist a write legacy would not). The retry delay becomes config key `statusline.cache.rename_retry_delay_ms` (Int, default 10, range 1..1000, judgment call). Attempt count: state one number consistently (initial attempt + retries) in ARCH-04, VP-018 and the BC. | A09 |
| OD-187 | VP-036: the >512 KB timing-fixture exemption is conditional per the brief: it applies only when that fixture misses the 25 ms target, and its use is reported. | A2-19 |

<!-- Phase-1d pass-7 remediation rulings by the owner, 2026-11-18 (owner chose the recommended option each time; next free OD-193) -->

| OD-188 | The Windows rename retry count becomes config key `statusline.cache.rename_retry_limit` (Int, default 2, range 0..10, judgment call), beside `statusline.cache.rename_retry_delay_ms`. Total attempts = 1 + limit. | rules ADV-P7-A19, A2-07 |
| OD-189 | The dead-backend marker word reuses `statusline.pill.label_local` (OD-173). New Text keys with legacy defaults: `statusline.labels.vllm_down` (`vLLM down`), `statusline.labels.lmcache_down` (`LMCache down`), `statusline.subagent.name_fallback` (`?`). | rules ADV-P7-C2-07, C11 |
| OD-190 | Extends OD-183: hylo writes LF line endings on every OS (UTF-8 + LF). The Windows oracle's LF normalization is named beside `PYTHONIOENCODING=utf-8`, not hidden in the shim. | rules ADV-P7-A2-19 |
| OD-191 | The >512 KB timing fixture (OD-187) gets a ceiling: exempt from the 25 ms p95 target, but the gate fails if its p95 exceeds 100 ms (judgment call: 4x the target, well under the refresh interval). | rules ADV-P7-A2-18 |
| OD-192 | ASM-007 (Claude Code 2.1.326 subagentStatusLine payload) must be validated by an owner capture into git-ignored `captures/` before Phase 2 writes the S1.07 stories; the rest of Phase 2 is not blocked. | rules ADV-P7-A22 |

<!-- Phase-1d pass-8 remediation rulings by the owner, 2026-11-18 (owner chose the recommended option each time; next free OD-194) -->

| OD-193 | OD-158 stands unchanged: the P1 >=95% line-coverage gate covers S1 (`internal/statusline`, `internal/cost`) and S5 (`internal/pyfmt`) only. `internal/parity` (S6) coverage is reported, not gated. Pass-7 call 12's addition of `internal/parity` to the gate is withdrawn. | ADV-P8-A04 |

<!-- Phase-1d pass-11 owner ruling, 2026-11-18 (minted centrally with the pass-11 remediation plan; next free OD-195) -->

| OD-194 | Every word a person reads as a label becomes a Text config key under `statusline.labels.*`, default = the legacy bytes; punctuation and unit marks (`->`, `·`, `/`, `[`, `]`, `?`, the dead-rung ` ?`, ` <1%`) stay named format constants with a "why not config" note. Range for the new keys = the label rule: non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-173 judgment call). | ADV-P11-C2-03. Nine keys minted centrally (defaults = the exact legacy word; sites in legacy/dgx_statusline.py): `statusline.labels.old` = `old` (SL:700), `rate` = `r` (SL:741), `queue` = `q` (SL:741), `kv` = `KV` (SL:761), `host` = `host` (SL:762, `↺host`), `tps` = `t/s` (SL:781/783), `max` = `max` (SL:797), `idle` = `idle` (SL:834), `na` = `n/a` (SL:631). Agent 2 registers them in interface-definitions with env names per the `EnvName` rule; agent 8 adds them to BC-2.01.004's registry; agent 7 names them in the consuming BCs' postconditions. |
