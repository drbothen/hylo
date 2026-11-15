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
