---
document_type: behavioral-contract
level: L3
version: "1.3.10"
status: draft
producer: product-owner
timestamp: 2026-11-18T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md]
input-hash: "465db67"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:fetch_sample (SL:158-187)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-040"
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: v0.1.0
modified:
  - "2026-11-17 (v1.3) pass-2 remediation ADV-P2-C2-08/09/13/14"
  - "2026-11-18 (v1.3.1) pass-3 remediation ADV-P3-C2-04/05/10 (redirect loop detection; OverflowError catch; 1e400; key identity)"
  - "2026-11-18 (v1.3.2) sync — Verification Properties row relabeled; VP-022 (partial: network edge only) now states its own property (the status line never reads the ledger, DI-007) instead of VP-030's differential-equivalence text"
  - "2026-11-18 (v1.3.3) pass-4 remediation ADV-P4-C2-01/02 (overflow vector >= 2**1024 - 2**970; metric wrapper on the two-key vector), ADV-P4-C2-07 (37-hop worst case; normalized redirect key; rebuilt chain example), ADV-P4-C2-08 (URI header fallback), ADV-P4-C2-09 (Accept-Encoding: identity / DisableCompression), ADV-P4-C2-12 (CP-N03 named on EC-013)"
  - "2026-11-18 (v1.3.4) pass-4 residual sweep — D4-EX-3 table-test name canonicalized to TestD4EX3_* (ADV-P4-D22; entry redated into the pass-4 burst date to keep the modified sequence monotonic)"
  - "2026-11-18 (v1.3.5) pass-5 remediation ADV-P5-C2-01/02 (manual redirect loop: unconditional ErrUseLastResponse, hylo-driven hops, empty-Location self-redirect, quote safe=string.punctuation, urlunparse round trip), ADV-P5-C2-03 (userinfo metrics URL: dead rung, OD-180), ADV-P5-C2-04 (VP-030 scoped to body bytes over well-formed HTTP)"
  - "2026-11-18 (v1.3.6) pass-6 remediation ADV-P6-C2-02/05/06/07/08/11/12 (empty-Location target = urljoin at the requesting hop's URL; minimal net.Conn HTTP/1.1 client with urllib's exact header set/order and compat32 header-value spaces; fetch-site JSON depth measured 992 accepted / 993 rejected; ftp and TLS deviations named under exclusion id OD-181; empty-fragment key drop)"
  - "2026-11-18 (v1.3.7) pass-7 remediation ADV-P7-C2-01/02/04/08 (body framing = the http.client read ladder: chunked, then Content-Length, else EOF; compat32 header rule corrected to lstrip space/tab then rstrip CRLF — leading whitespace stripped too; http/https client versus plain-http parity corpus disentangled; the next GET drops the URL fragment) + ADV-P7-C2-03 (VP-012 closure row for OD-181) + ADV-P7-C2-09 (stale ARCH-03 line label corrected)"
  - "2026-11-18 (v1.3.8) pass-8 remediation ADV-P8-C2-02 (followed-3xx body drained under the PC1 framing ladder before the next hop; a drain failure raises IncompleteRead and gives no sample with one fewer wire request), ADV-P8-C2-03 (chunked = the exact equality tr_enc.lower() == \"chunked\"; trailing-space and list values fall to Content-Length/EOF), ADV-P8-C2-13 (_MAXHEADERS = 100, the 65536-byte header-line limit, and the interim 1xx skip pinned), ADV-P8-C2-10 (ARCH-03 line anchors re-verified on disk: 187/270), ADV-P8-A2-17 (stale Transport{Proxy: nil} residue dropped from PC2)"
  - "2026-11-18 (v1.3.9) pass-8 residual — Refactoring Notes seam respelled to the ARCH-03 TEST SEAM ruling: raw net.Listener fake in tests, not httptest"
  - "2026-11-18 (v1.3.10) pass-9 remediation ADV-P9-C2-01 (interim skip = status 100 only; 101/102/103 final → HTTPError → no sample even with a 200 behind them; EC-025), ADV-P9-C2-02 (urlsplit sanitization before scheme guard and quote: leading C0/space stripped, TAB/CR/LF deleted anywhere, scheme lowercased; oracle: /a<TAB>b → /ab, <VT>/foo → /foo, HTTP:// hop followed), ADV-P9-C2-07 (Host = URL netloc as written, percent-unquoted, port only when written), ADV-P9-C2-06 (ARCH-03 citations as section anchors, line labels dropped)"

deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.001: fetch_sample: query, 1.5 s timeout, first-wins

## Description

One metrics-store instant query per fetch turns the backend's metrics into a flat
sample `{series name: float}`. The query string, the URL shape, the proxy bypass, the
per-series skip rule and the first-wins rule reproduce legacy `fetch_sample` exactly;
every failure collapses to "no sample" (never an error, never a crash). Notation: `\e`
is byte 0x1B.

## Preconditions

1. The metrics URL is `backends[0].metrics_url` (OD-123; default `http://192.0.2.10:8428`,
   legacy SL:73), with every trailing `/` stripped (legacy `rstrip("/")`).
2. The query is config key `statusline.telemetry.query`, whose default is
   **byte-identical** to legacy `QUERY` (SL:102-123); the pinned golden is that literal.
3. The timeout is `statusline.telemetry.timeout_s`, default 1.5 s (T-005, rationale
   "~60x the measured ~25 ms LAN RTT and below one 4 s refresh tick", OD-57 E-0).

## Postconditions

1. Exactly one HTTP GET is issued to
   `<url>/api/v1/query?query=<QUERY percent-encoded as Python quote(QUERY, safe='')>`
   (space as `%20`, never `+`; the encoded prefix is
   `%7B__name__%3D~%22vllm%3Anum_requests_running%7C...`). Transport: hylo's metrics
   client is a MINIMAL HTTP/1.1 client over a `net.Conn`: an `http` URL dials plain TCP;
   an `https` URL upgrades the SAME `net.Conn` through `crypto/tls` with SNI, ALPN
   `http/1.1` only, and the OS trust store (system roots on Linux) — it is the PARITY
   CORPUS that is plain http only (OD-181), never the client (ADV-P7-C2-04). It
   sends exactly what urllib sends, byte for byte and in urllib's order — request line
   `GET <selector> HTTP/1.1`, then `Accept-Encoding: identity`,
   `Host: <URL netloc as written, percent-unquoted, with the port only when the URL
   carries one>`, `User-Agent: Python-urllib/3.11`, `Connection: close` — and nothing
   else (Host measured against a local listener, CPython 3.11.7, 2026-11-18, one run
   each: `http://127.0.0.1:55785/...` → `Host: 127.0.0.1:55785`;
   `http://127.0.0.%31:55785/...` → `Host: 127.0.0.1:55785` — `Request._parse` does
   `self.host = unquote(self.host)`; a URL with no port sends `Host: 127.0.0.1` with
   the port omitted — `HTTPConnection.putrequest`'s `urlsplit(url)`-netloc Host branch
   emits the netloc verbatim, and `_get_hostport` normalizes the absent port to the
   scheme default; the portless leg is source-derived, a privileged port not being
   wire-capturable; ADV-P9-C2-07) (header
   spelling and order verified from the CPython 3.11.7 stdlib source — `do_request_`
   adds `Host` then the `addheaders` `User-agent`, `do_open` appends `Connection:
   close` and title-cases, `putrequest` emits `Accept-Encoding: identity` before the
   dict because `Host` is already present — and captured byte-for-byte against a local
   listener, 2026-11-18; ADV-P6-C2-12). It parses the response body raw and never
   decompresses (legacy asks for `identity`; Go's default Transport would send
   `Accept-Encoding: gzip` and silently decompress — ADV-P4-C2-09). The minimal client
   is required, not a style choice: Go's `net/http`/`textproto` (a) TRIMS BOTH ENDS of
   every header value (`textproto.TrimString`), while CPython 3.11.7 compat32
   `header_source_parse` does `value.lstrip(' \t')` then `rstrip('\r\n')` — leading
   spaces/tabs are STRIPPED TOO, and inner and TRAILING spaces/tabs are KEPT
   (oracle-verified CPython 3.11.7, 2026-11-18: `Location: ␉␠/x␠` parses to `/x␠`;
   ADV-P7-C2-02, correcting the ADV-P6-C2-05 wording). The sides diverge on TRAILING
   whitespace: a `Location: /x␠` value parses to `/x␠` (quoted `/x%20`) under compat32
   but `/x` under Go's trim; (b) `url.Parse` rejects
   a `%` not followed by two hex digits, which urllib passes through (`%` is in the
   safe punctuation set); (c) an empty `Location` makes `http.Client` skip
   `CheckRedirect` entirely. Status line and headers are therefore parsed exactly as
   `http.client` does (compat32: `lstrip(' \t')` then `rstrip('\r\n')` — rule (a)
   above). The observable http.client header limits are parity behaviour, not
   implementation detail (ADV-P8-C2-13; oracle-verified through urllib on CPython
   3.11.7, 2026-11-18, one run each against a local listener): more than
   `_MAXHEADERS` = 100 header lines raises `HTTPException` ("got more than 100
   headers") → no sample; a header line longer than `_MAXLINE` = 65536 bytes raises
   `LineTooLong` ("got more than 65536 bytes when reading header line") → no sample;
   an interim header block is skipped for STATUS 100 ONLY (ADV-P9-C2-01, correcting
   the pass-8 "1xx" wording; oracle-measured through urllib on CPython 3.11.7,
   2026-11-18, one run against a local listener): `HTTPResponse.begin` loops only
   while the status is 100, so a `HTTP/1.1 100 Continue` block followed by a 200-block
   yields status 200 and the body, while a 101/102/103 block IS THE FINAL RESPONSE —
   it is not in 200-299, so `HTTPErrorProcessor` raises `HTTPError` with that code and
   legacy gets NO SAMPLE even when a 200-block follows on the SAME connection (oracle:
   `HTTP/1.1 103 Early Hints` then `HTTP/1.1 200 OK` on one connection → `HTTPError`
   code 103 and the pending 200 is never parsed; 101 "Switching Protocols" and 102
   "Processing" are equally final). A Go client that skips ANY 1xx takes the 200
   behind a 103 and obtains a sample where legacy obtains none (EC-025). The constants
   100/65536 are CPython stdlib class constants emulated
   for parity — named constants in hylo with a "why not config" comment, not config
   keys (P16). Body framing is `http.client`'s `HTTPResponse.read()` ladder, because
   legacy `resp.read()` (SL:172) reads through `http.client`: (i)
   `Transfer-Encoding: chunked` → the DE-CHUNKED concatenation, and chunked wins over
   a `Content-Length` (RFC 2616 §4.4 #3 as coded in `HTTPResponse.begin`) — where
   "chunked" means the EXACT equality `tr_enc.lower() == "chunked"` on the lowercased
   compat32 value, NOT a trimmed or membership test: `Transfer-Encoding: Chunked␠`
   (trailing space survives compat32) and `Transfer-Encoding: gzip, chunked` are both
   NON-chunked — the body falls to the Content-Length/EOF ladders and the raw
   chunk-size lines reach `json.loads` (there is no sample); oracle-verified CPython
   3.11.7, 2026-11-18: `TE: Chunked␠` and `TE: gzip, chunked` each read the body
   `3\r\n{"a\r\n4\r\n: 1}\r\n0\r\n\r\n` verbatim while `TE: chunked` reads
   `{"a: 1}` (ADV-P8-C2-03, replacing the former "case-insensitive" wording — the
   only case rule is the `.lower()` inside the exact equality); (ii) else
   `Content-Length` → exactly that many bytes (a value that fails `int()` or is negative
   is treated as ABSENT; a truncated body raises `IncompleteRead` → outer
   `except Exception` → no sample); (iii) else (neither header) → read to EOF
   (connection close). Oracle-verified on CPython 3.11.7, 2026-11-18: chunks
   `3\r\n{"a\r\n4\r\n: 1}\r\n0\r\n\r\n` read as
   `{"a: 1}`; `Content-Length: 5` yields exactly `hello`; neither header yields the
   stream until close (ADV-P7-C2-01). A literal client that hands the raw body —
   chunk-size lines included — to `json.loads` yields no sample for every chunked reply
   where legacy gets one. Redirects: the Go client follows HTTP redirects exactly as
   urllib's default `HTTPRedirectHandler` (active because
   `build_opener(ProxyHandler({}))` keeps it, SL:168-171) — a 301/302/303/307/308 is
   followed by GET and the **final** body is parsed; other statuses are not redirected.
   Followed-3xx body drain (ADV-P8-C2-02; CPython 3.11.7 `http_error_302`, oracle-verified
   through urllib 2026-11-18): before opening the next hop, urllib DRAINS the body of a 3xx
   it decides to follow (`fp.read(); fp.close()`) under the SAME http.client framing ladder
   as above — the drain honours Content-Length, chunked and EOF framing. A drain failure
   gives NO SAMPLE and, because the raise precedes the next hop, one FEWER wire request: an
   oracle hop 1 announcing `Content-Length: 100` but sending 3 bytes then closing raises
   `IncompleteRead(3 bytes read, 97 more expected)` with exactly ONE wire request observed
   and no sample; a bad chunk line in the drained body and a no-length drained body held
   open to the timeout raise the same way (outer `except Exception` → no sample). A client
   that skips the drain and jumps straight to the next hop obtains a sample where legacy
   obtains none.
   Header read (CPython 3.11.7 `http_error_302`, verified from the 3.11.7 stdlib source
   on 2026-11-17): the target is the first `Location` header, falling back to the first
   `URI` header when `Location` is absent; a 30x carrying neither header is returned
   unhandled (HTTPError → no sample). A present-but-EMPTY `Location` is a real target:
   urllib computes `urljoin(req.full_url, "")`, where `req` is the request that
   RECEIVED THIS 3XX — on hop 1 that is the original URL (query included), but from the
   second hop on it is the CURRENT hop's URL B, not the original A (oracle:
   `urljoin(B, "")` returns B exactly; ADV-P6-C2-02). From hop 2 on, B is both the loop
   key and the next GET target (the ADV-P5-C2-01 keyed-target behavior follows from the
   corrected rule). A redirect naming only
   `URI:` is therefore followed
   by legacy and must be followed by hylo; a client that reads only `Location` gets no
   sample where legacy gets one (ADV-P4-C2-08). Scheme guard: the scheme AFTER
   `urlsplit` sanitization of the raw target must be `http`, `https`, `ftp` or empty
   (inherit); anything else makes urllib raise `HTTPError` (→ no sample). The
   sanitization happens BEFORE the guard and before quote (ADV-P9-C2-02; urlsplit,
   CPython 3.11.7): all leading C0 controls and spaces are stripped, every `\t`, `\r`
   and `\n` byte anywhere in the target is deleted, and the scheme is LOWERCASED — so
   `HTTP://…` passes the guard as `http` and urllib follows it (oracle: a
   `Location: HTTP://127.0.0.1:PORT/x` hop is followed, second request
   `GET /x HTTP/1.1` observed on a local listener, 2026-11-18); a guard written
   against the raw header string would wrongly reject it. Hylo rule (exclusion id **OD-181**,
   DI-012 closed set): the manual loop follows only `http`/`https` targets after
   empty-scheme inheritance — an `ftp:` or other non-http(s) target gives **no
   sample**. Legacy MAY produce a sample there: its default opener keeps
   `FTPHandler`/`HTTPSHandler` (verified from `build_opener(ProxyHandler({})).handlers`,
   CPython 3.11.7), so an `ftp:` redirect can be fetched by the FTPHandler — hylo
   implements no FTP fallback; table tests pin hylo's behaviour, and parity cases use
   plain http only (OD-181). TLS trust (an https metrics URL or an https redirect
   target; OD-181): legacy CPython 3.11 verifies certificates against OpenSSL's default
   store, hylo (Go `crypto/tls`) against the OS trust store (macOS/Windows) — a
   certificate trusted by only one store yields a sample on one side and no sample on
   the other; table tests pin hylo's behaviour (OS store), parity cases plain http.
   Target normalization (ADV-P4-C2-07; completed ADV-P5-C2-02): the
   loop-detection key is the target AFTER the raw-header scheme check, the `urlsplit`
   sanitization (leading C0 controls and spaces stripped, `\t`/`\r`/`\n` deleted
   anywhere in the target, scheme lowercased — an inner TAB vanishes: `Location: /a␉b`
   keys and targets `/ab`, NOT `/a%09b` as the former chain spelled it; a leading
   `\x0b`, which compat32 rule (a) above keeps, is stripped: `Location: \x0b/foo`
   targets `/foo`; oracle-measured through urllib on CPython 3.11.7, 2026-11-18, local
   listener, ADV-P9-C2-02), the empty-path fix
   (netloc with no path → `/`), the `urlunparse` round trip (an empty query or empty
   params component is dropped, so `/x?` and `/x` are ONE key; an EMPTY fragment is
   dropped too — `urlunsplit` adds `#` only when the fragment is non-empty — so `/x#`
   and `/x` are ONE key; parameters and a NON-EMPTY fragment are kept as part of the
   key — the fragment is a LOOP-KEY component only: the next GET splits it off, since
   urllib's `Request` strips the fragment from the wire target (oracle:
   `Request('http://h:8428/p?x=1#frag').selector` = `/p?x=1`, CPython 3.11.7,
   2026-11-18), so a request line never carries `#frag` (ADV-P7-C2-08); ADV-P6-C2-11),
   percent-encoding of non-ASCII
   and special bytes (`quote(newurl, encoding="iso-8859-1", safe=string.punctuation)` —
   the `safe` set is ALL ASCII punctuation, not the default `'/'`; read with the default
   the rule would encode `:` and double-encode existing `%XX`, giving loop keys urllib
   never forms), and resolution to an absolute URL
   (`urljoin(req.full_url, ...)`); a raw `Location: /x` and a `Location: http://<host>/x`
   that resolve to the same absolute URL are ONE key — keying the raw header would split
   them and must not be done. Pinned loop detection: urllib keeps a per-request
   `redirect_dict` keyed by that normalized absolute redirect-target URL (the initial URL
   is never a key) and, before following, refuses iff
   `visited.get(newurl, 0) >= max_repeats (= 4)` **or** `len(visited) >= max_redirections
   (= 10)`; the target's count increments only after the decision to follow. The cap is
   therefore NOT a hop counter: at most 10 distinct targets are ever keyed, a keyed
   target is followed at most 4 times, and the tenth key's single follow exhausts the
   budget — worst case 9×4 + 1 = **37 hops**, after which every further redirect is
   refused. A chain that revisits targets (A→B→A→B…, each visit count < 4) is followed
   while the counts hold, and a distinct-target chain is refused at its 11th redirect
   (len = 10); a Go `CheckRedirect` that counts hops refuses chains urllib follows
   (sample vs no sample). The caps 4/10 are CPython stdlib class constants emulated for
   parity — named constants in hylo with a "why not config" comment, not config keys
   (P16). Normative Go rule (pass-5 call 14, ADV-P5-C2-01/02): hylo does NOT ride
   `http.Client`'s automatic redirect machinery. The client's `CheckRedirect` returns
   `http.ErrUseLastResponse` unconditionally, so every 3xx response comes back to hylo
   unelevated, and hylo drives the hops itself in a loop it controls: pick the target
   (`location` then `uri`; a present-but-empty value resolves as
   `urljoin(<URL of the request that received this 3xx>, "")` — hop 1: the original URL
   (query included); hop ≥ 2: the current hop's URL), apply the scheme
   guard, normalize (`urlsplit` sanitization — leading C0 controls and spaces
   stripped, `\t`/`\r`/`\n` deleted anywhere, scheme lowercased, ADV-P9-C2-02 — then
   empty-path fix → `urlunparse` →
   `quote(..., "iso-8859-1", safe=string.punctuation)` → `urljoin`), then consult the
   `redirect_dict` emulation — refuse (no sample, and never parse the refused 3xx body)
   iff `count[normalized] >= 4 || len(count) >= 10`, otherwise `count[normalized]++` and
   issue the next GET (its request target drops the fragment; only the loop key keeps
   it). Only this structure reproduces the empty-`Location` self-redirect,
   the urllib-normalized key and the non-http(s)-target no-sample guard: `CheckRedirect`
   alone sees none of them (Go skips it on an empty `Location` and cannot rewrite the
   target). Hylo must reproduce every refusal mode the
   way urllib does — the fetch fails to "no sample" (outer `except Exception`, SL:186) —
   and must never parse the refused 3xx body.
2. Proxy environment variables are ignored for this request (legacy `ProxyHandler({})`,
   SL:168): hylo's PC1 minimal client has NO proxy machinery at all — there is no
   `http.Transport` to configure, and nothing in the dial path reads `HTTP(S)_PROXY`;
   the connection goes directly to the metrics host (ADV-P8-A2-17 dropped the stale
   `Transport{Proxy: nil}` spelling, a residue of the pre-pass-6 net/http design).
   Userinfo (OD-180, ADV-P5-C2-03): a metrics URL
   carrying a `userinfo@` component (`http://u:p@192.0.2.10:8428`) reproduces legacy's
   dead rung — urllib hands `u:p@192.0.2.10` to `HTTPConnection` as the host, the name
   lookup fails, and the fetch is **no sample**; hylo must not strip the userinfo and
   send Basic auth (Go's `url.User` default), so the userinfo rung is no sample (no
   exclusion id; the URL still passes BC-2.02.005's load-time approval, BC-1.04.001
   fetches it to no sample).
3. Result is **no sample** (Go: nil; legacy `None`) when: the status is outside 200-299;
   the body is not decodable JSON (decoded as `json.loads(resp.read())` on BYTES =
   bytes-mode acceptance (BOM/UTF-16/32 detection, BC-5.02.003); a multi-line metrics
   body (newline/carriage-return bytes between tokens) is valid input here — the
   BC-5.02.003 one-line precondition governs the stdin sites, not this one; the fetch
   site's JSON nesting-depth limit is MEASURED per call site, never inferred: depth
   **992 accepted / 993 rejected** on the production stack (F = 7 frames,
   <module>→main→get_sample→fetch_sample→loads→decode→raw_decode; oracle-measured
   2026-11-18 by running the real `dgx_statusline.py` as a subprocess with an isolated
   HOME against a fake local metrics server, ADV-P6-C2-06) — a deeper body gives no
   sample); the
   payload is not an object; `payload["status"] != "success"`; `data`/`result` is
   missing or of a wrong type; any series raises outside the per-series catch; or the
   resulting map is empty.
4. Otherwise, for each element `s` of `data.result`, in array order:
   - `name = s["metric"].get("__name__", "")`; a missing `metric` key or a non-object
     `metric` aborts the **whole** fetch (no sample).
   - `val = float(s["value"][1])` with the Python float grammar (BC-5.01.002). On
     `KeyError`, `ValueError` or `IndexError` that series is skipped. A `TypeError`
     (e.g. `value` is a number, `value[1]` is `null`) is **not** caught per series and
     aborts the whole fetch (no sample). So is an `OverflowError`: Python's `json.loads`
     decodes an integer literal at arbitrary precision, and a JSON integer with
     |value| >= 2**1024 - 2**970 (oracle-verified on CPython 3.11.7, 2026-11-18) raises
     `float(int)` outside the per-series catch (SL:177-180) and aborts the whole fetch
     (no sample, outer `except Exception` SL:186). A JSON **float** literal is not
     subject to that conversion — `1e400` is decoded by `json.loads` itself to +Inf and
     kept. A Go float64 decode maps both literal forms to +/-Inf, so it must
     special-case the oversize integer literal to stay differential-equivalent.
   - `name == "up"` is rewritten to `"up:" + s["metric"].get("job", "")`; a non-string
     `job` makes the concatenation raise `TypeError` — both sites sit outside the
     per-series catch (SL:182-185) — and aborts the whole fetch (no sample).
   - The pair is stored only if `name` is truthy and not already present
     (**first wins**). Membership is dict hashing, so an unhashable non-empty
     `__name__` (list, dict) raises `TypeError` at `name not in out` (SL:183-184) and
     aborts the whole fetch, while an empty list/dict name is falsy and the series is
     skipped. The hashable non-strings `1`, `1.0` and `true` collide under first-wins
     (`True == 1`, equal hash; `1.0 == 1`) and round-trip through the JSON cache write
     as strings. Key identity is Python hash/eq, not text: the string `"5"` and the int
     `5` are **distinct** dict keys, and `json.dump` writes both as the JSON text
     `"5"` (a duplicate-key object, SL:203); a `json.load` of that object keeps the
     **last** one. And the JSON constant `NaN` decodes to one shared float object, so
     two series whose `__name__` is `NaN` collide through dict identity and first-wins
     keeps the first (oracle-verified 2026-11-18). A Go `map[string]float64` model
     diverges on both counts under the VP-030 differential; hylo must carry the
     Python key identity (typed hash/eq key plus the shared-NaN sentinel) through the
     session-cache round trip (BC-1.04.020).
5. The function never raises; the render path continues with the result.

## Invariants

1. One fetch decision per refresh (BC-1.04.002 decides whether to fetch); the decision issues the initial GET plus any redirect hops urllib's default handler would also take — a bare single-request `Transport` is not parity-compatible.
2. Non-finite strings (`"NaN"`, `"+Inf"`, `"-Inf"`, `"1e400"`) are accepted as floats and
   flow to the renderers and history unchanged (handled by BC-1.04.014/015/016).
3. Ordering of the sample map is insertion order (it is written to the session cache in
   that order, BC-1.04.020).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Two series with the same `__name__` | first in the array kept: `x`=1 then `x`=2 → `{"x": 1.0}` |
| EC-002 | `value[1]` = `"a5"` next to a good series | `"a5"` skipped (ValueError), `{"y": 7.0}` |
| EC-003 | Every series skipped | no sample (empty map → None) |
| EC-004 | `value` = `5` (TypeError) next to a good series | **no sample** (whole fetch dropped) |
| EC-005 | `value` = `[1, null]` | no sample (TypeError) |
| EC-006 | `value` = `[1]` or key absent | that series skipped (IndexError/KeyError) |
| EC-007 | `value` = `"17"` (a string) | `"17"[1]` = `"7"` → `7.0` |
| EC-008 | `value` = `[1, true]` | `1.0` |
| EC-009 | `value[1]` = `" ١_0 "` (Unicode digit, underscore, spaces) | `10.0` (Python float grammar) |
| EC-010 | `metric` = `{}` | name `""` → series skipped, others kept |
| EC-011 | `metric` key missing on any element | no sample |
| EC-012 | `up` without `job` label | key `"up:"` |
| EC-013 | `__name__` is a number (`5`) | stored under int key 5; `serving_state`'s `any(k.startswith("vllm:") for k in m)` short-circuits at the first `vllm:` key (SL:717), so the numeric key degrades the line (BC-1.01.001) only when it precedes every `vllm:`-prefixed key (`{5: 1}` alone → degraded; `{"vllm:x": 1, 5: 1}` → renders normally) AND only when row 2 renders at all — telemetry runs only under the SL:1224 responsive rule (`rows_env > 2 or cols == 0 or cols >= NARROW_COLS`), so a terminal narrow enough to drop row 2 never calls `serving_state` and nothing degrades (ADV-P5-C2-13). Metrics-borne degrade, crash id **CP-N03**. After the session-cache write the key round-trips through JSON as the string `"5"`, so later cached-path refreshes never degrade |
| EC-014 | HTTP 500 / 404 | no sample |
| EC-015 | body `not json`; `[1,2]`; `{"status":"error"}`; `result` = `{}` or `"ab"` | no sample |
| EC-016 | body with UTF-8 BOM | accepted (bytes-mode decode) |
| EC-017 | connection refused / timeout | no sample |
| EC-018 | `value[1]` = a bare JSON integer literal with magnitude >= 2**1024 - 2**970 (the smallest magnitude that overflows; e.g. 2**1024 - 2**970 itself. Note 10**308 — also 309 digits — is BELOW DBL_MAX: `float(10**308)` returns `1e+308` without raising, oracle-verified CPython 3.11.7, ADV-P4-C2-01) | `float(int)` raises OverflowError outside the per-series catch (SL:177-180, 186) → **no sample**; a bare float literal `1e400` next to it is kept as +Inf (ADV-P3-C2-05) |
| EC-019 | `value[1]` = `1e400` (bare JSON float literal) | `json.loads` decodes it to +Inf; `float(+Inf)` = +Inf → series stored (`{"x": +Inf}`) |
| EC-020 | two series, `__name__` = string `"5"` and int `5` | both stored (distinct keys, insertion order); `json.dump` emits two `"5"` keys; the cache reload keeps the **last** (ADV-P3-C2-10) |
| EC-021 | two series, both `__name__` = `NaN` | one shared NaN object → dict identity collides → first wins (ADV-P3-C2-10) |
| EC-022 | followed 302 announces `Content-Length: 100`, sends 3 body bytes, closes; target 200 serves valid JSON | the drain of the 3xx body raises `IncompleteRead(3 bytes read, 97 more expected)` before the next hop → **no sample**, exactly ONE wire request observed (oracle-verified CPython 3.11.7, 2026-11-18, ADV-P8-C2-02) |
| EC-023 | `Transfer-Encoding: Chunked␠` (trailing space) or `gzip, chunked`, chunked-style body, no `Content-Length` | NOT chunked (exact equality `tr_enc.lower() == "chunked"`); the raw chunk-size lines `3\r\n{"a\r\n4\r\n: 1}\r\n0\r\n\r\n` reach `json.loads` → **no sample**; bare `chunked` de-chunks to `{"a: 1}` (oracle-verified CPython 3.11.7, 2026-11-18, ADV-P8-C2-03) |
| EC-024 | reply with 101 header lines / a 70,000-byte header line / a `100 Continue` block then a 200 block | >100 headers → `HTTPException` ("got more than 100 headers") → **no sample**; >65536-byte line → `LineTooLong` → **no sample**; the interim skip is status-100-only: a `100 Continue` block then a 200 block yields status 200 and the body (oracle-verified CPython 3.11.7, 2026-11-18, ADV-P8-C2-13; narrowed ADV-P9-C2-01) |
| EC-025 | `HTTP/1.1 103 Early Hints` block (101 or 102 alike) with a `HTTP/1.1 200 OK` JSON block behind it on the SAME connection | the 1xx-non-100 block is the FINAL response → `HTTPError` with that code → **no sample**; the pending 200 is never parsed (oracle-measured through urllib, CPython 3.11.7, 2026-11-18, ADV-P9-C2-01) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `{"status":"success","data":{"result":[{"metric":{"__name__":"vllm:num_requests_running"},"value":[1,"3"]},{"metric":{"__name__":"up","job":"vllm"},"value":[1,"1"]},{"metric":{"__name__":"up","job":"lmcache"},"value":[1,"0"]}]}}` | `{"vllm:num_requests_running": 3.0, "up:vllm": 1.0, "up:lmcache": 0.0}` (this order) | happy-path |
| result with `"NaN"`, `"+Inf"`, `"1e400"` for x, y, z | `{"x": NaN, "y": +Inf, "z": +Inf}` | edge-case |
| result `[{"metric":{"__name__":"y"},"value":[1,"7"]},{"metric":{"__name__":"x"},"value":5}]` | no sample | error |
| result `[{"metric":{"__name__":"x"},"value":[1,1e400]}]` | `{"x": +Inf}` | edge-case |
| result `[{"metric":{"__name__":"y"},"value":[1,"7"]},{"metric":{"__name__":"x"},"value":[1,<2**1024 - 2**970 as a bare JSON integer literal>]}` | no sample (integer-literal OverflowError; the smallest overflowing magnitude, ADV-P3-C2-05 + ADV-P4-C2-01) | error |
| result `[{"metric":{"__name__":"5"},"value":[1,"1"]},{"metric":{"__name__":5},"value":[1,"2"]}]` | two keys stored (distinct keys: string `"5"` then int `5`, insertion order); after a cache round trip one `"5"` key remains holding `2.0` (ADV-P4-C2-02) | edge-case |
| HTTP 500 with a valid body | no sample | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | For any response **body** delivered over well-formed HTTP framing, the Go fetch returns the same map (keys incl. Python key identity per PC4 — distinct `"5"`/`5`, shared NaN; order; float bits) or "no sample" as legacy. Malformed wire framing (header lines Python's email parser tolerates, LF-only line endings, duplicate Content-Length) is out of scope by design: the Tier C oracle emits WELL-FORMED framing per the PC1 ladder (chunked / Content-Length / EOF) and varies status, header values and body only (ADV-P5-C2-04; the stale net/http reason removed ADV-P7-C2-01 — framing is hylo's own code since pass 6) | fuzz (Tier C differential) + table |
| VP-022 (partial: network edge only) | The status line never reads the ledger (DI-007): the metrics fetch reads only the VictoriaMetrics HTTP response at the network edge — no ledger/file reads in the render path | static analysis (read-scope absence) |
| VP-030 | The function never panics or returns an error to the caller | fuzz |
| VP-030 | Request URL bytes equal legacy's for the default query | manual (golden) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-181` (metrics transport beyond plain http: non-http(s) redirect targets give no sample; https TLS trust-store differences) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-181` entry and its riding table test `TestMetricsClient_OD181_TransportTable` (defined in VP-030), and the mutation test fails closed if that entry is dropped (ADV-P7-C2-03) | property test (VP-012, go test) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:fetch_sample (SL:158-187); QUERY (SL:102-123); VM_URL/HTTP_TIMEOUT (SL:73, 81) |
| Legacy contract | BC-SL-040 (P3 base + r1 refinement; r5 verified, r8 coverage) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007, DI-008, DI-012 (metrics-URL D4-EX-3 deviation, BC-2.02.005; ftp/TLS transport deviations named under exclusion id OD-181, ADV-P6-C2-07/08) |
| Decisions | OD-123 (metrics URL under backends[0]), OD-56 (timeout = total deadline), OD-57 E-0 (T-005), D14 (proxy bypass is defense in depth) |
| Architecture Module | `internal/statusline/telemetry.go` (design §2.2; listed in ARCH-03 §Interfaces — the `MetricsClient` interface declaration and the `telemetry.go` file-list row; cited by SECTION anchor only, never line numbers, per pass-9 ADV-P9-C2-06 — the third line-label drift there after ADV-P7-C2-09 and ADV-P8-C2-10) |
| Stories | TBD (story-writer) |

## Related BCs (Recommended)

- BC-1.04.002 — composes with: decides when this fetch runs and stores its result
- BC-1.04.016 — related to: renders non-finite values this fetch admits
- BC-5.01.002 — depends on: Python float grammar
- BC-5.02.003 — depends on: `json.loads(bytes)` acceptance set
- BC-2.01.002 — depends on: `backends[0].metrics_url`
- BC-2.02.005 — related to: a non-http(s) metrics URL is not fetched at all; it is approved deviation D4-EX-3 (config error line; OD-105 exclusion entry `D4-EX-3`, dedicated test `TestD4EX3_URL`), whereas legacy handed any string to urllib (BC-SL-087: a bad URL yields no sample)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/telemetry.go (query, total deadline, first-wins) (metrics client and fake-metrics seam) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — fetch differential equivalence; VP-022 (partial) — network-edge read scope only

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:102-123, 158-187) |
| **Confidence** | medium — the per-site catch list (`TypeError` drops the whole sample) is the subtle surface (design §8 row 040) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except (KeyError, ValueError, IndexError): continue` (SL:179-180); outer `except Exception` (SL:186)
- **inferred**: series order = VictoriaMetrics result order; re-executed against a local fake server on CPython 3.11.7 (2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | network call |
| **Global state access** | reads config |
| **Deterministic** | no — depends on the metrics store |
| **Thread safety** | unknown (single-threaded use) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Split into a `MetricsClient.Query` seam (I/O, raw `net.Listener` fake in tests — not httptest, whose server canonicalises headers into a map and trims values; ARCH-03 TEST SEAM, ADV-P7-C2-05) and a pure
`parseSample(body []byte) (Value, bool)` that carries the catch-list semantics. Timeout
semantics differ by owner ruling OD-56: legacy's 1.5 s is per socket operation, Go's is
a total deadline. The parity corpus never exercises timeouts (fake metrics failure
modes are closed listener, 5xx and garbage), so this is not an output difference and has
no exclusion entry.
