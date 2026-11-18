---
document_type: remediation-plan
phase: 1d
pass: 11
date: 2026-11-18
source: adversarial-reviews/pass-11.md, adversarial-reviews/ADV-P11-INDEX.md
---

# Pass-11 remediation plan (canonical rulings and calls)

Read with the Rules section of `pass-4-remediation-plan.md` and the gates of passes 9-10 (YAML parse after every edit; for-all properties derived from every PC/EC/exception and walked against legacy; state only what you measured, bracketing boundaries on both sides; ASCII wire goldens; cite ARCH and BC files by section/ID + PC/EC/Inv/row, never line numbers; synthetic values on the pre-push hook allowlist; edit only your file set, list out-of-set hits). A canonical vector's expected hylo output that is derived by reasoning (hylo does not exist yet) must be walked line by line against the legacy code that sets each field (pass-11 C01 lesson).

## Owner ruling (2026-11-18)

| ID | Ruling | Source |
|---|---|---|
| OD-194 | Every word a person reads as a label becomes a Text config key under `statusline.labels.*`, default = the legacy bytes; punctuation and unit marks (`->`, `·`, `/`, `[`, `]`, `?`, the dead-rung ` ?`, ` <1%`) stay named format constants with a "why not config" note. Range for the new keys = the label rule: non-empty, no control bytes, valid UTF-8, display width 1..16 (OD-173 judgment call). | ADV-P11-C2-03 |

Next free OD: OD-195.

**OD-194 key names (minted centrally; agents copy, never invent):** `statusline.labels.old`, `statusline.labels.rate`, `statusline.labels.queue`, `statusline.labels.kv`, `statusline.labels.host`, `statusline.labels.tps`, `statusline.labels.max`, `statusline.labels.idle`, `statusline.labels.na`. Each default is the exact legacy WORD only; surrounding spaces, digits and punctuation stay in the format. Orchestrator-derived defaults and sites (legacy/dgx_statusline.py): `old` = `old` (SL:700, `(~{age:.0f}s old)`), `rate` = `r` and `queue` = `q` (SL:741, `r{r:.0f}·q{q:.0f}`), `kv` = `KV` (SL:761), `host` = `host` (SL:762, `↺host`), `tps` = `t/s` (SL:781 and SL:783), `max` = `max` (SL:797, `◔max {val}`), `idle` = `idle` (SL:834, `☾ idle {age}`), `na` = `n/a` (SL:631, `⛏n/a`). Agent 2 registers them in interface-definitions with env names per the `EnvName` rule (e.g. `HYLO_STATUSLINE_LABELS_OLD`); agent 8 adds them to BC-2.01.004's registry; agent 7 names them in the consuming BCs' postconditions. If an agent finds another label word in legacy, report it (do not mint a name).

## Orchestrator calls (binding; checked against the OD log)

1. **OD-190 applied literally (A2-02, A2-09):** on the Windows legs the comparator converts the ORACLE's stdout CRLF to LF openly, before the byte comparison; hylo's bytes are never converted (hylo writes LF itself). The shim does no newline reconfigure. BC-6.03.002 (PC1 and EC-006), VP-034 and VP-009/VP-011 state exactly this; BC-6.01.002 names the conversion beside `PYTHONIOENCODING=utf-8`.
2. **temp-file case (D01):** the canonical `temp-file` case declares a fake process table (oracle: a fake `ps` on PATH through the existing conditional fake-PATH machinery; Go: a `ProcStarter` fake), so it needs no `proc_start` seed and never consults the real process tree. It is the fake-PATH machinery's first P1 consumer; BC-6.01.002's "no P1 consumer" note is updated.
3. **Case metrics URL (D02):** when a case sets the metrics URL, the case value is used on BOTH sides (oracle `DGX_SL_VM_URL` and hylo `HYLO_BACKENDS_0_METRICS_URL`), and the validator admits a case metrics URL only as a placeholder that resolves to the fake server (optionally with a path suffix). One value per key.
4. **Defaults in env spelling (A09, D08):** every Default cell in interface-definitions (and BC-2.01.004's registry) is the exact env spelling, parseable by the key's grammar: e.g. `claude,claude-` (List), `[0.75,0.95]`, `{"cc":300000,"other":1800000}`, `[80,100]`. Build check (c) parses each Default with its key's grammar.
5. **Stdin field list (A01):** interface-definitions' and prd.md's "objects read" list equals the fields legacy actually reads — derive from every `.get(` on the stdin document and its sub-objects in `legacy/dgx_statusline.py`; remove fields legacy never reads, add the missing ones.
6. **Coverage gate manifest (A02, A03):** the committed manifest lists the gated packages present in the repo and grows as each lands; `G == 0` is allowed while none of the three gated packages exists, whatever other `internal/` packages exist. State that Go measures statement coverage and how the per-package figure is computed from the `-coverpkg` profile; Tier B and machinery tests do count.
7. **gitleaks rev set (A04):** the scanned rev set equals the compared rev set: scan with log options naming exactly `main` and `factory-artifacts`, and compare with `git rev-list --count` over the same two refs.
8. **Tier A selector (A07):** define the oracle-dependent test set by one mechanism (a named build tag or `-run` pattern) that includes every test needing the Python oracle (Tier A corpus, the shim canary, the four-cache swap, and any other); the plain test step, coverage and release exclude exactly that set.
9. **Startup wiring (A08):** a `CacheDir` error at startup leaves the render running with a load-empty / save-no-op cache store (BC-3.01.001 EC-004), not a config error; `Env.Loc` comes from `LocalZone`, and its error disposition follows BC-3.01.001.
10. **VP-021 (A2-03):** derive the percentile property from BC-1.05.005 exactly: NaN-bearing histories (EC-009), the usd list vs the rate list, the per-src `api_ms` gate, self-exclusion of the current sid.
11. **CP-O07 vector (C01):** `lu` is null in the expected hylo cache (legacy sets `lu` only on a user line, SL:1085); state the three timestamps; close the code span.
12. **VP-031 fallback order (C2-01):** the `gen_rate5m` fallback `v` is inserted AFTER `k` and `f` (SL:344-345); the key-order table includes the fallback cases; BC-1.04.003 names the four series.
13. **Windows naive-time domain (D06):** the domain is left-closed at 1970-01-02T00:00:00 local wall (probe `u1 − 86400 = 0` is inside MSVC's domain under TZ=UTC); state it once and consistently in BC-5.04.001, BC-5.04.002 and BC-6.04.003; drop any contradictory zone-offset wording unless measured.
14. **CP-S IDs (B01):** CP-S02, S03, S04, S05, S08 and S10 are named in their owning ECs and defined in error-taxonomy's CP-S table (id, site, owner BC/EC); ARCH-03 cites the taxonomy.
15. **Oracle self-check (B08):** OD-185's harness self-check adds a probe that `posixpath.normpath('a\0b')` and `ntpath.normpath('a\0b')` keep the NUL (orchestrator-measured on 3.11.7: both return `'a\x00b'`).
16. **Everything else** as reported, routed below.

## Agent file sets and findings (routed by file)

| Agent | Role | Files | Findings |
|---|---|---|---|
| 1 | architect | specs/architecture/*, specs/cicd-setup.md | A02, A03, A04, A07, A08, A10 (ARCH-06 subagent wire site), A11 (ARCH-08), A12; B01 (ARCH-03 cites taxonomy); B08 (ARCH-07 self-check list); D03 (ARCH-08 toolchain status consistent with BC-6.04.001) |
| 2 | product-owner | specs/prd.md, specs/prd-supplements/*, specs/owner-decisions-log-2026-11-14.md | OD-194 entry + registry rows; A01, A03 (nfr/module-criticality), A05, A06, A09, A10 (prd §8), A11 (nfr); B01 (taxonomy CP-S table), B05 (separator range), B07; D03 (prd title row); D17 |
| 3 | architect | VP-001..VP-020 | A2-01 (VP-018), A2-02/A2-09 (VP-009, VP-011), A2-04 (VP-014), A2-07 (VP-003/VP-004), A2-10 (VP-010); B08 (VP-006 if it lists the self-check); C2-07 (VP-020) |
| 4 | architect | VP-021..VP-041, VP-INDEX, domain-spec/*, product-brief, dtu, gene-transfusion, feasibility | A2-02 (VP-034), A2-03 (VP-021), A2-05 (VP-032), A2-06 (invariants recount with the stated method), A2-08 (VP-029), A2-11 (VP-040 P5); B03 (VP-040 P7 generator); C2-01 (VP-031); VP-INDEX sync |
| 5 | product-owner | ss-01 BC-1.01.*, BC-1.02.* | B01 (name CP-S IDs in ECs), B02, B03 (EC + vector), B04, B05 (BC-1.01.006 Inv 1), B06, B09 |
| 6 | product-owner | ss-01 BC-1.03.*, BC-1.06.*, BC-1.07.* | C01, C02, C03, C04 |
| 7 | product-owner | ss-01 BC-1.04.*, BC-1.05.* | OD-194 consumers (derive the words, report them; name the keys in postconditions); C2-01 (BC-1.04.003 names the four series), C2-02, C2-04, C2-05, C2-06, C2-08, C2-09 |
| 8 | product-owner | ss-02..ss-06 BCs, BC-INDEX, BC-ALLOCATION | OD-194 registry rows in BC-2.01.004; A07 (BC-6.01.001 selector); A09 (BC-2.01.004 defaults); A2-02 (BC-6.03.002, BC-6.01.002 per call 1); B08 (BC-6.01.001 self-check); D01..D16 (D03 H1 sync in BC-INDEX/BC-ALLOCATION) |
