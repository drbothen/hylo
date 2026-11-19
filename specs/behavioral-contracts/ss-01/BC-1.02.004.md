---
document_type: behavioral-contract
level: L3
version: "1.3.9"
status: draft
producer: product-owner
timestamp: 2026-11-18T10:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "f3906fd"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:git_branch (SL:364-396)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-009
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "2026-11-18T02:00:00Z (v1.1): pass-3 remediation (ADV-P3-B02): file-read encoding pinned to OD-159 (Go reads files as UTF-8 on all OSes, named deviation); the LANG rationale replaced"
  - "2026-11-18T03:00:00Z (v1.2): pass-4 remediation (ADV-P4-B18/B06/B07/B03): CPython os.fsencode/surrogateescape path-encoding pin (P18); parity-class row acknowledges the OD-159 deviation; DI-012 cited; for-all walk-termination and fake-FS syscall legs re-anchored to VP-041"
  - "2026-11-18T05:42:56Z (v1.3): pass-5 remediation (ADV-P5-B06/B16): lone-surrogate levels do not raise — genericpath.isdir/isfile return False (caught ValueError), so the walk continues to the nearest ancestor repo instead of returning \"\" (oracle-verified); PC2 pin and EC-013 aligned; typo \"statt\"→\"stat\""
  - "2026-11-19T02:00:00Z (v1.3.1): sync-check adv-p5 closure (SC-20) — pass-4 stamp re-dated ascending (it predated pass-3's); no behavioral change"
  - "2026-11-19T04:00:00Z (v1.3.2): pass-6 remediation (ADV-P6-B05 + B12): PC2 pin marked POSIX-only with the Windows lone-surrogate outcome spun out as new EC-014 (wide-string stat; Go U+FFFD substitution flagged for a named-deviation ruling, OD-188); detached-HEAD ref[:7] marked a named format constant, not config, with the D15 rationale (Inv 4)"
  - "2026-11-19T14:00:00Z (v1.3.3): pass-6 residual sweep (orchestrator call 16): EC-014 resolved with no exclusion — internal/platform encodes WTF-8 path values to UTF-16 itself, keeping lone surrogates as single 16-bit units (no U+FFFD substitution), Windows table test (ARCH-05); deviation-ruling note removed"
  - "2026-11-19T15:00:00Z (v1.3.4): pass-7 remediation (ADV-P7-B07): the cwd read is stated, not hidden — abspath resolves a relative input directory against cwd (reachable via BC-1.02.003 EC-004) and the empty-string fallback reads it too; both route through Env.Cwd / platform.Abs, and the Purity row drops the 'unreachable fallback' wording; no behavioral change"
  - "2026-11-19T16:00:00Z (v1.3.5): pass-9 remediation (ADV-P9-B04/B05, orchestrator call 12; one measurement each on the pinned oracle): PC2.3 pins the chunk-scoped strict decode of the pointer read — readline() decodes a whole buffered chunk (io.DEFAULT_BUFFER_SIZE 8192), so an invalid byte after the first LF still fails the read (end-to-end: no ancestor fallback, the walk stops) — and PC3 partitions the error kinds: isdir/isfile catch (OSError, ValueError) and return False (probes: embedded NUL ValueError, mode-000 PermissionError errno 13), so stat-level errors only make the level count as not-a-directory and the walk continues upward; only open/read failures reach the SL:394 handler; vectors 11-12 added"
  - "2026-11-20T18:00:00Z (v1.3.6): pass-10 remediation (ADV-P10-B02/B06, orchestrator call 12): PC2.3 chunk boundary re-pinned to the orchestrator measurement — the text reader decodes the first 8192 bytes in one chunk (invalid byte at offset < 8192 fails, at >= 8192 the whole line reads, independent of st_blksize (4096 on the measuring filesystem)); the 4096-byte-prefetch note removed; boundary probes at offsets 8191/8192 stated; PC2.2/PC2.4 and PC3 state the stat semantics (isdir/isfile follow symlinks, unlike PC1's purely lexical abspath) so a port cannot pick lstat-only or DirEntry-type checks and diverge on a symlinked .git or HEAD"
  - "2026-11-21T12:00:00Z (v1.3.7): pass-11 remediation (ADV-P11-B02): PC2.4 pins the whole-read universal-newline translation — any interior CR or CRLF inside the HEAD file becomes LF before the strip (bytes ref: refs/heads/a\rb\n give branch a\nb, interpreter-verified CPython 3.11.7), also written to the git cache; new EC-015 and canonical vector; no behavioral change"
  - "2026-11-24T00:00:00Z (v1.3.8): pass-13 remediation (ADV-P13-B08c): PC2 step 3's severed clause repaired - the inserted Stat-semantics note no longer cuts the strip-whitespace lead-in away from its if-it-starts-with-gitdir continuation; the continuation is its own sentence; history canonicalized date-first (undated pass entries defaulted to the stamps the same passes carry in sibling files); no behavioral change"
  - "2026-11-24T01:00:00Z (v1.3.9): pass-14 remediation (ADV-P14-B09): the VP-028 golden row's layout-table count updated from the stale 10 to the table's current 14 rows (rows 11-14 added in passes 9 and 11); no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.004: Branch walk reads .git dir or file and HEAD

## Description

The branch lookup walks from the absolute project directory up to the filesystem root and
stops at the first directory that is a real repository: its `.git` is a directory, or a
pointer file whose first line starts with `gitdir:`, **and** the resolved git directory
holds a `HEAD` file. It returns the branch name for `ref: refs/heads/<name>`, otherwise the
first 7 code points of HEAD (detached head), or `""` when no repository is found or an open/decode
error occurs (stat-level errors only skip a level — PC3). It never invokes the git binary.

## Preconditions

1. Called with a non-empty directory string (render path: the raw `proj_dir` of
   BC-1.02.003, only when the git segment is enabled, BC-1.02.005). **Environment input (pass-7 ADV-P7-B07):**
   `os.path.abspath` (SL:373) resolves any *relative* directory against the process cwd — a reachable input,
   since BC-1.02.003 EC-004 renders `"."` and `rel/dir` — and the `directory or os.getcwd()` fallback (SL:373)
   reads cwd for an empty string. Go routes both cwd reads through the `Env.Cwd` seam
   (`platform.Abs(env.Cwd(), directory)`, design §2.2), so harness results never depend on the real
   process cwd; the legacy fallback stays unreachable from rendering.
2. The filesystem is read through the `Env.Files` seam; text decoding is strict UTF-8 on
   every OS as a **named deviation** — exclusion id **OD-159** ("Go reads files as UTF-8 on all
   OSes"): legacy's `open()` has no encoding argument (SL:380-381, 385-386), so on Windows the
   CPython oracle decodes with the ANSI code page (LANG has no effect there; the BC-6.01.002
   shim reconfigures only stdin/stdout), e.g. the vector `ref: refs/heads/\xff\xfe` decodes to
   the two code points U+00FF U+00FE (UTF-8 bytes `\xc3\xbf\xc3\xbe`) on the Windows oracle
   instead of erroring. Windows-oracle goldens for non-ASCII or
   invalid-UTF-8 HEAD/`.git` content therefore carry the OD-159 exclusion and are regenerated
   on the Windows CI leg (EC-012); POSIX goldens are unaffected.

   **Path-encoding pin (P18, pass-4 ADV-P4-B18):** path arguments are encoded exactly as CPython encodes them with
   `os.fsencode` — the `surrogateescape` handler: code points U+DC80..DCFF map to the raw bytes 0x80..0xFF, so
   `.../\udcff/sub` stats a real directory whose name is the single byte 0xFF; any other lone surrogate makes the
   level checks fail (no `UnicodeEncodeError` escapes: CPython's `genericpath.isdir`/`isfile` catch the
   `ValueError` superclass — oracle-verified 2026-11-17: both return `False` on a lone-surrogate path — so the
   level only counts as not-a-directory and the walk continues upward, returning the nearest ancestor repo's
   branch, or `""` when no repository is found). Go must
   reproduce this mapping byte-for-byte: a WTF-8 port would stat the three bytes ED B3 BF and the `sub` label
   would not degrade, diverging the branch (oracle-verified CPython 3.11.7, 2026-11-17). This pin is
   POSIX-only: on Windows the `str` path is passed to the OS as a wide string, which has a different
   lone-surrogate outcome (EC-014).

## Postconditions

1. `d = abspath(directory)` (host OS path module; no symlink resolution, no existence
   check) — relative inputs resolve against the seam-provided cwd (PC1; `Env.Cwd` /
   `platform.Abs`, not the real process environment).
2. Loop, for each `d` from the start up to the root:
   1. `dotgit = join(d, ".git")`; `gitdir = None`.
   2. If `dotgit` is a directory → `gitdir = dotgit`.
   3. Else if `dotgit` is a regular file → read its first line in text mode (universal
      newlines: `\n`, `\r\n` and a lone `\r` all end the line) and strip Python whitespace.
      **Stat semantics (pass-10 ADV-P10-B06):** `os.path.isdir`/`isfile` follow symlinks (stat, not
      lstat — a symlinked `.git` or a symlinked `HEAD` is statted through, and a symlink pointing at a
      directory makes the level qualify as a repo directory; SL:377, 379, 384). Only PC1's `abspath` is
      purely lexical; the level checks are not. Go must reproduce this with stat-following-symlink
      semantics (or `os.Lstat` + follow-on-stat), never lstat-only or `DirEntry`-type checks.
      Then, if the stripped first line starts with `gitdir:` → `gitdir = normpath(join(d, rest.strip()))` (an
      absolute `rest` replaces `d`, as `os.path.join` does).

      **Chunk-scoped decode (pass-9 ADV-P9-B04, oracle-verified 2026-11-18; chunk boundary orchestrator-measured
      pass-10 ADV-P10-B02, CPython 3.11.7):** the pointer read is `open(dotgit).readline()` (SL:380-381), which
      decodes the first 8192 bytes (`io.DEFAULT_BUFFER_SIZE`) in one chunk — independent of `st_blksize` (4096 on
      the measuring filesystem) — not a line-scoped validation: an invalid byte at file offset < 8192 fails
      `readline()` with `UnicodeDecodeError`; at offset >= 8192 the first line reads (boundary probes: raw `\xff`
      at offset 8191 → raise; at offset 8192 → first line reads; corroborating probes: offset 14 in a 95-byte
      pointer file → raise; offset 9015 → first line reads; end-to-end through the real entry point: pointer
      `gitdir: ../gd\n` + raw `\xff` inside the first chunk → `""` immediately, no ancestor fallback despite a
      qualifying ancestor repo). Go must reproduce the chunk-scoped strict decode with the 8192-byte chunk, not a
      validate-only-the-first-line read. The 8192-byte chunk is **io.DEFAULT_BUFFER_SIZE**, inherited from
      CPython's text-io buffering — a **named format constant** shared with legacy's runtime, not config (D15
      rationale: parity-bound to the oracle's own stdlib default; why not config = a configurable chunk size
      would change which pointer files decode, a behavior knob no ruling mints; unlike this BC's Inv 4 slice,
      it is not even hylo's constant to tune).
   4. If `gitdir` is set and `join(gitdir, "HEAD")` is a regular file → read it whole in
      text mode, strip Python whitespace into `ref`, and **return**:
      `ref[len("ref: refs/heads/"):]` if `ref` starts with `ref: refs/heads/`, else
      `ref[:7]` (code points).

      **Whole-read newline translation (pass-11 ADV-P11-B02, interpreter-verified CPython 3.11.7):** the whole
      read is `open(...).read()` in text mode (SL:385-386), so universal newlines translate not only a trailing
      terminator but any interior CR or CRLF inside the file to LF before the strip: HEAD bytes
      `ref: refs/heads/a\rb\n` yield `ref` = `ref: refs/heads/a\nb\n` after the read (the stripped `ref` retains
      the interior LF) and the returned branch is the two-line string `a\nb` — the same value a CRLF interior
      produces; a raw-bytes port that skips the translation returns `a\rb` and diverges. The translated branch
      string (LF inside) is also what the git cache stores (BC-1.02.005).
   5. `parent = dirname(d)`; if `parent == d` → return `""`; else `d = parent`.
3. Errors partition by kind (pass-9 ADV-P9-B05, oracle-verified 2026-11-18): **stat-level errors never
   raise** — `os.path.isdir`/`isfile` catch `(OSError, ValueError)` and return `False` (oracle
   `genericpath` source; probes: an embedded NUL — `ValueError: embedded null byte` — and a mode-000 parent
   component — `PermissionError` errno 13 — both return `False`), so EACCES on a parent component,
   `ENAMETOOLONG`, `ENOTDIR` and embedded NULs only make the level count as not-a-directory and the walk
   **continues upward** (end-to-end: start under a mode-000 directory above a repo → the repo's branch,
   not `""`); this is the general rule behind the PC2 lone-surrogate pin; the checks are stat semantics
   that follow symlinks (PC2.2). Only `open`/read failures —
   including the PC2.3 chunk-decode error — reach the outer handler (SL:394) and return `""` immediately
   (the walk does **not** continue upward).

## Invariants

1. Read-only: no file is created or modified.
2. A directory without `.git`, a `.git` directory without `HEAD`, a stray plain `HEAD`
   file, or a non-`gitdir:` pointer file never stops the walk.
3. The first qualifying ancestor wins; the result is never a name from a farther ancestor
   once a nearer `HEAD` has been read.
4. The detached-HEAD result is the literal slice `ref[:7]` — the first 7 code points of HEAD
   (PC2.4; EC-008). It is a **named format constant shared with legacy's stdout**, not config
   (D15, mirroring the cache-key slice T-062 in BC-1.02.005 Inv 2): 7 is git's conventional
   abbreviated-sha display length, but the parity obligation is legacy's literal slice, and a
   configurable length would change rendered bytes (D4); why not config = it is a display-format
   constant of the output, not a behavior knob.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | start in a subdirectory of a repo | branch of that repo (walk up) |
| EC-002 | `.git` dir without `HEAD`, parent is a repo | parent's branch |
| EC-003 | stray plain file `HEAD` in a non-repo dir | ignored; walk continues |
| EC-004 | `.git` file with content not starting `gitdir:` | ignored; walk continues |
| EC-005 | worktree pointer `gitdir: ../wt/gitdirs/c` (relative) or absolute | resolved and read |
| EC-006 | pointer first line terminated by a lone `\r` (`gitdir: ../wt/g\rjunk\n`) | first line is `gitdir: ../wt/g` (universal newlines) |
| EC-007 | HEAD `ref: refs/heads/a\r\n` or with surrounding spaces/blank lines | `a` (strip) |
| EC-015 | Interior CR or CRLF in HEAD (pass-11 ADV-P11-B02): bytes `ref: refs/heads/a\rb\n` or `ref: refs/heads/a\r\nb\n` | branch = the two-line string `a\nb` (whole-read universal-newline translation, PC2.4); the same translated value is written to the git cache (BC-1.02.005); a raw-bytes port gives `a\rb` and diverges |
| EC-008 | HEAD `ref: refs/remotes/origin/main` | `ref: re` (first 7 code points; legacy behavior kept) |
| EC-009 | empty HEAD | `""` and the walk stops (HEAD exists) |
| EC-010 | HEAD bytes invalid UTF-8 | decode error → `""` (no further walking) |
| EC-011 | start dir does not exist | walk still runs lexically; an existing ancestor repo is found if any, else `""` |
| EC-012 | Windows paths | ntpath `abspath`/`dirname`/`join`; the loop ends when `dirname(d) == d` at the drive root; OS-specific goldens |
| EC-013 | Directory segment holding a lone surrogate (hand-crafted tree) | U+DC80..DCFF encode to the raw bytes 0x80..0xFF (`os.fsencode`/surrogateescape); any other lone surrogate makes `isdir`/`isfile` return `False` (the caught `ValueError` superclass) → the level counts as not-a-directory and the walk **continues upward** to the nearest ancestor repo's branch, or `""` when no repo is found; Go reproduces the mapping (P18 pin, PC2; oracle-verified 2026-11-17) |
| EC-014 | Windows leg, lone-surrogate path component (pass-6 ADV-P6-B05; outcome ruled, vector pending Windows-CI run) | On Windows CPython passes `str` paths to the OS as wide strings, so a lone surrogate is a valid UTF-16 unit and **can stat a real directory** whose name contains it — no surrogateescape remapping occurs (that pin is POSIX-only). Resolved with no exclusion (pass-6 orchestrator call 16): `internal/platform` encodes WTF-8 path values to UTF-16 itself, keeping lone surrogates as single 16-bit units — never Go's U+FFFD substitution — so a path with a lone surrogate stats the same directory CPython's wide-string call does. Windows lone-surrogate goldens are separate Windows-CI table tests (EC-012 leg), not POSIX corpus cases; table-tested on Windows (ARCH-05) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15 with synthetic trees under a
temp root `<T>` that has no repository above it; rows 11-12 (ADV-P9-B04/B05) verified 2026-11-18 through
the real entry point (`python3 -I -s legacy/dgx_statusline.py`, isolated HOME and cwd).

| Input (tree, start dir) | Expected Output | Category |
|-------|----------------|----------|
| `<T>/a/.git/HEAD` = `ref: refs/heads/main\n`; start `<T>/a` | `main` | happy-path |
| same tree; start `<T>/a/sub/deep` | `main` | happy-path |
| `<T>/b/.git/HEAD` = `0123456789abcdef0123456789abcdef01234567\n` | `0123456` | happy-path |
| `<T>/c/.git` = `gitdir: ../wt/gitdirs/c\n`, `<T>/wt/gitdirs/c/HEAD` = `ref: refs/heads/feature/x\n` | `feature/x` | edge-case |
| `<T>/p/.git/HEAD` = `ref: refs/heads/parent\n`, empty dir `<T>/p/d/.git/`; start `<T>/p/d` | `parent` | edge-case |
| `<T>/p/e/HEAD` stray; start `<T>/p/e` | `parent` | edge-case |
| `<T>/p/f/.git` = `garbage\n`; start `<T>/p/f` | `parent` | edge-case |
| `<T>/i/.git/HEAD` = `ref: refs/remotes/origin/main\n` | `ref: re` | edge-case |
| `<T>/k/.git/HEAD` empty | `""` | edge-case |
| `<T>/none/x`, no repo anywhere | `""` | edge-case |
| `<T>/h/.git/HEAD` = bytes `ref: refs/heads/\xff\xfe\n` | `""` | error |
| `<T>/r/.git/HEAD` = `ref: refs/heads/ancestor\n`; `<T>/r/wt/.git` = `gitdir: ../gd\n` + raw `\xff` bytes; `<T>/gd/HEAD` = `ref: refs/heads/feature\n`; start `<T>/r/wt` | `""` (chunk-decode error stops the walk; no ancestor fallback) | error |
| `<T>/u/.git/HEAD` = `ref: refs/heads/main\n`; start `<T>/u/child` where `child` is mode 000 (stat EACCES) | `main` (stat-level error: the walk continues upward) | edge-case |
| `<T>/cr/.git/HEAD` = bytes `ref: refs/heads/a\rb\n` (interior CR); start `<T>/cr` | `a\nb` (the two-line string: interior CR translated to LF by the whole-read universal newlines, PC2.4; interpreter-verified CPython 3.11.7); the cached branch holds the same `a\nb` value | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-041 | Walk terminates for every start path (strictly shorter `d` each step until `dirname(d)==d`) | table test + reasoning (VP-028 retains the bounded golden tables) |
| VP-041 | No write syscalls during the walk | fake FileSystem test (VP-028 retains the bounded golden tables) |
| VP-028 | Results equal the oracle on the layout table (pass-3 #3; 14 rows after the pass-9 and pass-11 additions) on all three OSes | table test against CPython goldens |
| VP-012 | The named deviation this contract defines — exclusion id `OD-159` (Go reads files as UTF-8 on all OSes; Windows HEAD/`.git` decoding) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-159` entry and its riding table test `TestGitTextReads_OD159_StrictUTF8`, and the mutation test fails closed if that entry is dropped | property test (VP-012 `TestParityExclusions_ClosedSet` / `TestParityExclusions_MutationFailClosed`, go test) |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:git_branch (SL:364-396; allocation cites SL:372-396, the body) |
| Legacy contract | BC-SL-009 (confirmed fully guarded, locale text mode: pass-3 r1 §A; r8 audit) |
| Parity class | byte-exact; carries the named deviation `OD-159` (Go reads files as UTF-8 on all OSes — PC2, EC-012), covered by the exclusion-closure row VP-012 |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Owner decisions | D5 (cross-platform, no shelling out to git), OD-104 (oracle CPython 3.11), OD-159 (files read as UTF-8 on all OSes — Windows HEAD/`.git` decoding cases) |
| Config keys | none directly (enable/TTL in BC-1.02.005) |
| Architecture Module | `internal/statusline/git.go` (design §2.2) |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.005 — composes with (cached caller)
- BC-1.02.003 — depends on (raw `proj_dir`)
- BC-5.03.002 — depends on (Python whitespace strip, line splitting)
- BC-5.03.004 — depends on (per-OS path functions)
- BC-6.01.002 — related to (oracle locale fixed to UTF-8)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#git` — internal/statusline/git.go (.git/HEAD walk; py sha1 key) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — branch segment story

## VP Anchors (Recommended)

- VP-041 — walk termination and read-only property (for-all start paths; fake-FS no-syscall leg); VP-028 — golden layout table
- VP-012 — exclusion-closure cover for the named deviation `OD-159`

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`git_branch`, SL:364-396) |
| **Confidence** | high (pass-3 HIGH-R, 10 layouts; re-run 2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `try/except Exception` → `""` (SL:372, 394-396)
- **documentation**: docstring SL:365-371 (review 2026-11-13 #3.2, #3.3)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads only (stat + two small file reads per qualifying level) |
| **Global state access** | cwd, read by `abspath` for any relative input directory (and by the empty-string fallback) — routed through the `Env.Cwd` seam (PC1; pass-7 ADV-P7-B07) |
| **Deterministic** | yes for a fixed filesystem |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Reads go through the injected `FileSystem` so the walk is table-testable with an in-memory
tree; the decision logic (pointer parse, HEAD parse) can be split into pure helpers.
