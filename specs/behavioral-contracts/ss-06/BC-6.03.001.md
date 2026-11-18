---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-19T17:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md
  - semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
input-hash: "4c53355"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-06"
capability: "CAP-009"
legacy_id: "BC-SL-089"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation D04: subagent corpus family added to the Python-written goldens with --subagent oracle argv (OD-155)"
  - "1.2.2 2026-11-18: ADV-P4 remediation D10 - -update relocated to ./internal/parity (corpus-owning package, canonical layout)"
  - "2026-11-19T00:25:00Z (1.2.3) ADV-P5 remediation D29 — -update per-OS write path defined: .windows.golden variants are written by an -update run ON Windows; a Linux run never fabricates them; metadata records the writing OS"
  - "2026-11-19T17:00:00Z (1.2.4): ADV-P7 remediation D14 - subagent cases identified by the ARCH-07 `subagent` case-id family (the -sub shorthand noted as the same family), not a bare id suffix; oracle argv text unchanged"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.03.001: Row goldens A/B/C (Tier B, Python-written, OS-specific variants)

> Byte notation used below: `\e` = ESC (0x1B); `\n` = LF (0x0A). All other characters are literal UTF-8.

## Description

Three full-refresh fixtures pin the complete status line output end to end, as
committed Tier B goldens — plus the subagent family (ADV-P3-D04): every subagent
corpus case — the `subagent` family of the ARCH-07 case-id grammar
`<family>-<nnn>[-<variant>]` (the older "-sub" shorthand denotes the same family;
pass-7 D14; BC-6.02.002/003) — is refreshed with the oracle argv
`[<python>, "-s", <abs>/legacy/dgx_statusline.py, "--subagent"]` (OD-155, superseding
OD-14) and its committed goldens are Python-written the same way, so the
legacy-parity half of the agent-panel mode is Tier-A/Tier-B verifiable:

- golden A: the cloud lane with plan-window limits and cold-start cost colors, plus a
  fresh row 2;
- golden B: the local lane, ⛏ shows `n/a`;
- golden C: the local lane with a stale row 2.

The golden bytes are always written by the Python oracle (`-update`), never by Go.
Go must reproduce them on every OS without Python installed. OS-dependent cases carry a
`*.windows.golden` variant.

## Preconditions

1. **Fixture** (P3r2 §A1):
   - `NOW = 1794615009.0`, `TZ=UTC`, `backends[0].model_prefixes = claude-sonnet`
     (legacy `LOCAL_MODEL_PREFIXES=claude-sonnet`), `COLUMNS` unset.
   - Session cache seeded with `proc_start = NOW-112000` and 6 history points
     `t = NOW-12 … NOW-2`, `v = 150,170,190,200,204,202`, `k=0.9`, `f=4.2`.
2. **stdin:**
   - `session_id "sess-golden-1"`;
   - `model {id, display_name}`: A uses display name `Opus 5.5` with an id not starting
     with `claude-sonnet`; B and C use `Sonnet 5.5` with an id starting with
     `claude-sonnet`;
   - `workspace.project_dir = {{.CaseDir}}/home-lab`, with `.git/HEAD` =
     `ref: refs/heads/main`, created at test time;
   - `context_window {used_percentage 43.4, context_window_size 1000000}`;
   - `prompt_cache.hit_ratio 0.94`;
   - `cost {total_lines_added 31, total_lines_removed 4, total_duration_ms 26700000,
     total_api_duration_ms 6711428.57, total_cost_usd 32.62}`;
   - golden A only: `rate_limits {five_hour {31, NOW+9690}, seven_day {44, NOW+15510}}`.
3. **Transcript** (6 lines, generated):
   - user prompt string (21 chars) at NOW-100;
   - assistant `m1` (thinking 400 chars) at NOW-98, and `m1` again (tool_use input
     `{"command":"ls -la"}`) at NOW-88, both with usage `in 200 / cw 30000 / cr 0 / out 1200`;
   - user tool_result of 3000 chars at NOW-80;
   - `m2` (text 29 chars; usage `100/60000/0/50`) at NOW-70;
   - `m3` (text 1500 chars; usage `300/900/60100/800`) at NOW-60.
4. **Metrics sample**, served by the fake VictoriaMetrics for A and B:
   - running 3, waiting 0, kv 0.92, host share 0.0;
   - gen_rate1m 204.4, gen_rate5m 190;
   - ttft p95 4.2 with n30m 57, preempt 0;
   - last local-lane request NOW-400;
   - wall 1400 W, tariff 0.24, GPU 1059 W, temp 66;
   - up vllm/lmcache 1;
   - usd/MTok 0.09, rate_mtok_month 12.0 (golden C: 45.0).
   For golden C the cache holds a sample 40 s old with `fetch_ts = NOW-10`, and the
   metrics mode is `down`.

## Postconditions

1. **Golden A, row 1** (198 visible columns, 12 segments) is exactly:

   ```text
   \e[105;30;1m ◨ ANTH \e[0m\e[2m · \e[0m\e[97mOpus 5.5\e[0m\e[2m · \e[0m\e[90m⎇ main\e[0m\e[2m · \e[0m\e[90mhome-lab\e[0m\e[2m · \e[0m\e[38;2;159;204;30m▰\e[38;2;182;204;30m▰\e[38;2;204;202;30m▰\e[38;2;204;179;30m▰\e[90m▱\e[90m▱\e[90m▱\e[90m▱\e[90m▱\e[90m▱\e[0m 43%\e[0m\e[2m/1.0M\e[0m\e[2m · \e[0m\e[36m▤60%\e[0m \e[32m❙32%\e[0m \e[35m◈ 8%\e[0m\e[2m · \e[0m\e[36m♻\e[0m 94%\e[2m · \e[0m\e[90m5h31%\e[0m \e[90m->2h41m\e[0m  \e[90m7d44%\e[0m \e[90m->4h18m\e[0m\e[2m · \e[0m\e[32m▲31\e[0m\e[2m/\e[0m\e[31m▼4\e[0m\e[2m · \e[0m\e[90m⏱ 7h25m\e[0m\e[2m·1h51m\e[0m\e[90m ⌂1d07h\e[0m\e[2m · \e[0m\e[90m↑\e[0m\e[97m152k\e[0m\e[2m[\e[0m\e[97min600\e[0m \e[33m✍91k\e[0m \e[36m⟳60k\e[0m\e[2m]\e[0m\e[90m ↓\e[0m\e[97m2k\e[0m \e[2m\e[33m↻1\e[0m\e[2m · \e[0m\e[33m$32.62\e[0m\e[90m $17.5/h\e[0m
   ```

2. **Row 2, fresh** (identical for A and B; 81 columns, 7 segments) is exactly:

   ```text
   \e[32m◉\e[0m\e[2m · \e[0m\e[32mr3·q0\e[0m\e[2m · \e[0m\e[36mKV▰▰▰▰ 92%\e[0m\e[2m · \e[0m\e[90m»\e[0m\e[90m5\e[0m\e[90mt/s\e[0m\e[2m · \e[0m\e[90m▣\e[0m\e[97m204\e[0m\e[90mt/s\e[0m \e[38;2;38;93;104m▆\e[38;2;44;108;121m▇\e[38;2;51;124;138m█\e[38;2;57;139;155m█\e[38;2;63;154;172m█\e[38;2;70;170;190m█\e[38;2;140;235;255m█\e[0m\e[2m · \e[0m\e[90m◔4.2s\e[0m\e[2m · \e[0m\e[97m⚡1059W\e[0m\e[90m·\e[0m\e[33m1400W\e[0m\e[90m 66°\e[0m\e[90m 34¢/h\e[0m
   ```

3. **Golden B, row 1** (173 columns, 11 segments) is golden A row 1 with four changes:
   - the pill is `\e[106;30;1m ◨ DGX \e[0m`;
   - the model is `\e[97mSonnet 5.5\e[0m`;
   - the limits segment and its preceding separator are removed (no `rate_limits`,
     empty cache);
   - `\e[90m ⛏n/a\e[0m` is appended after `\e[90m $17.5/h\e[0m`, because
     rate_mtok_month 12 < 30.4.
4. **Golden C**:
   - Row 1 is golden B row 1 with the tail `\e[90m ⛏0.01\e[0m` instead of `⛏n/a`
     (174 columns).
   - Row 2, stale (86 columns, 8 segments), is exactly:

   ```text
   \e[33m◉\e[0m\e[2m · \e[0m\e[32mr3·q0\e[0m\e[2m · \e[0m\e[36mKV▰▰▰▰ 92%\e[0m\e[2m · \e[0m\e[90m»\e[0m\e[90m5\e[0m\e[90mt/s\e[0m\e[2m · \e[0m\e[90m▣\e[0m\e[90m204\e[0m\e[90mt/s\e[0m\e[2m · \e[0m\e[90m◔4.2s\e[0m\e[2m · \e[0m\e[97m⚡1059W\e[0m\e[90m·\e[0m\e[33m1400W\e[0m\e[90m 66°\e[0m\e[90m 34¢/h\e[0m\e[2m · \e[0m\e[2m(~40s old)\e[0m
   ```

5. **stdout totals.** Each output is row 1, `\n`, row 2, `\n`:

   | Golden | Bytes | Row 1 width | Row 2 width |
   |---|---|---|---|
   | A | 1,179 | 198 | 81 |
   | B | 1,120 | 173 | 81 |
   | C | 999 | 174 | 86 |

   Exit code 0 for all three. These figures were re-derived from the strings above
   and match P3r2 §A1.
6. **Tier B write rule.**
   - `go test ./internal/parity -update` writes these goldens by running the
     oracle (BC-6.01.001) on the OS the variant targets, never from Go output (the
     `-update` flag lives in
     `./internal/parity`, the package that owns the corpus — ADV-P4-D10 layout).
     Per-OS write path (ADV-P5-D29): the ubuntu and macOS variants are written by an
     `-update` run on that OS (CI-adjacent developer runs); the
     `<name>.windows.golden` variants (PC 8) are written by an `-update` run ON
     Windows (a windows-2025 runner or workstation executing the same flag) — an
     `-update` run on Linux writes only the Linux (and, when its flavors match, the
     shared) golden files and never fabricates a `.windows.golden`. Golden metadata
     records the writing OS and the resolved CPython patch version (RK-4).
   - `-update` without a valid oracle interpreter fails; it never falls back to writing
     Go's output.
   - Golden metadata records the resolved CPython patch version (RK-4).
7. **Tier B match rule.** On ubuntu-24.04, macos-15 (arm64) and windows-2025, Go's
   output for each golden case must equal the committed golden byte for byte. Python
   is not required.
8. **OS-specific variants.** A case whose legacy output depends on `os.path` flavor has
   a committed `<name>.windows.golden`, also Python-written, on a Windows oracle run.
   The example is a root-directory project label (`posixpath.normpath("/")` → `/` vs
   `ntpath` → `\`, BC-SL-059). On Windows, Go is compared to the `.windows.golden`
   when it exists, otherwise to the default golden. Goldens A/B/C are OS-independent
   and have no Windows variant.

## Invariants

1. Goldens are never edited by hand and never regenerated from Go.
2. `.gitattributes` carries `testdata/** -text`, so Windows checkouts keep golden bytes
   (LF, no CRLF rewrite).
3. Goldens contain no machine paths, only the basename `home-lab` (BC-6.02.001).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Windows checkout with `core.autocrlf=true` | `testdata/** -text` keeps LF; Go output matches |
| EC-002 | `-update` with `HYLO_PARITY_PYTHON` unset | Test fails (`parity: -update requires the oracle`); no golden is written |
| EC-003 | Oracle patch version changes (3.11.7 → 3.11.x) and a golden shifts | The diff is visible in review together with the metadata version change (RK-4) |
| EC-004 | Root-path project on Windows | Go compared to `.windows.golden` (`\` label); on POSIX to the default golden (`/`) |
| EC-005 | Golden C: TTL expired (`fetch_ts = NOW-10` > TTL 4), the fetch fails | Yellow `◉`, the sparkline dropped, the box number grey, `(~40s old)` appended |
| EC-006 | `COLUMNS=80` production-shaped variant of golden A | 2 rows, widths [78, 56], 701 bytes (trim covered by BC-1.01.010) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Golden A fixture | stdout = A row 1 + `\n` + fresh row 2 + `\n` (1,179 bytes), exit 0 | happy-path |
| Golden B fixture | 1,120 bytes; no limits segment; `⛏n/a` tail | happy-path |
| Golden C fixture (stale cache, metrics `down`) | 999 bytes; row 2 stale form above | edge-case |
| Go output differs by one byte from committed A golden on macos-15 | Tier B FAIL with byte offset | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-010 | Go renders goldens A/B/C byte-identical to the Python-written committed files on all three OSes | golden test (Tier B) |
| VP-010 | No code path writes a golden from Go output | table test on the `-update` path |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:main (SL:1200-1235), render_lane (SL:440-637), render_telemetry / render_telemetry_fields (SL:693-835) |
| Legacy contract | BC-SL-089 (P3r2 §A1 fixture, golden strings, segment widths, byte totals; P3r4 §7.3 row) |
| Decisions | D4 (golden tests are the P1 exit criterion); OD-104 (CPython 3.11.x oracle); design §5.1 Tier B, §4 S8; research Q3c (`*.windows.golden`, `testdata/** -text`) |
| Parity class | byte-exact |
| L2 Capability | CAP-009, CAP-010, CAP-011 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/statusline/testdata/goldens/` (BC-COMPONENT-MAP: internal/statusline/testdata/goldens (Tier B, Python-written) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-1.01.010 — related to: trim breakpoint matrix computed from these golden rows (BC-SL-090)
- BC-1.02.003 — related to: project label `basename(normpath)`
- BC-1.02.022 — related to: POSIX/NT `normpath` root-path outputs behind the `*.windows.golden` variant (BC-SL-059)
- BC-1.05.008 — related to: cost-colour goldens (BC-SL-101)
- BC-6.01.001 — depends on: oracle interpreter for `-update`
- BC-6.03.002 — composes with: Tier A live comparison of the same cases

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/statusline/testdata/goldens (Tier B, Python-written) (Tier B golden store) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-010 — golden byte-equality properties above

---

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` |
| **Confidence** | high (fixture run through the whole of `main()` in Phase 0, P3r2 §A1) |
| **Extraction Date** | 2026-11-14 (P3r2); re-checked 2026-11-15 |

#### Evidence Types Used

- **documentation**: P3r2 §A1 golden strings and totals (byte counts and widths re-derived from the strings in this stage; the oracle was not re-run in this stage)
- **inferred**: fake-VM replacement of the P3r2 in-process `fetch_sample` fake (same sample values)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes (stdin, transcript, caches, metrics HTTP, stdout) |
| **Global state access** | reads global (env-derived constants) |
| **Deterministic** | yes, under the pinned clock, seeded caches and fake metrics |
| **Thread safety** | n.a. (one refresh per process) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

The Go port renders through the pure core plus effect script (design §3.1); goldens
exercise the whole effect script end to end, so they stay at the process level.
