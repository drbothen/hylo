#!/usr/bin/env python3
"""Claude Code Stop hook for claude-dgx: decide whether the model REALLY finished.

Fake stop = the DGX model ends its turn without completing its announced work. Two layers:

  1. Kev (primary). The transcript tail is posted to Kev's /v1/systemone as a noul question
     ("true = the agent's turn is genuinely complete"); Kev returns a calibrated p(done).
     Below DGX_KEV_THRESHOLD the stop is faked: the hook emits additionalContext to continue.
  2. Regex heuristic (fallback). The original announce-pattern detector, used only when Kev
     is unreachable or times out — the hook must never hang Claude Code's stop path.

Language policing (CJK reply => rewrite in English) stays ahead of both.
Log: ~/.cache/dgx-llm/auto-continue.log  (records kev p(done) for threshold calibration)
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

ANNOUNCE = re.compile(
    r"^(now|next|then|first|let me|let's|i'll|i will|i'm going to|going to|setting up|executing|"
    r"proceeding|starting|moving on|building|writing|creating|implementing|running|continuing)\b",
    re.IGNORECASE,
)

# ---- Kev decision model (fake-stop oracle) -----------------------------------
KEV_URL = os.environ.get("DGX_KEV_URL", "http://192.0.2.10:8008/v1/systemone")
KEV_MODEL = os.environ.get("DGX_KEV_MODEL", "kev-latest")
KEV_THRESHOLD = float(os.environ.get("DGX_KEV_THRESHOLD", "0.45"))
KEV_TIMEOUT = float(os.environ.get("DGX_KEV_TIMEOUT", "2.5"))
KEV_MESSAGES = int(os.environ.get("DGX_KEV_MESSAGES", "14"))
KEV_CHARS = int(os.environ.get("DGX_KEV_CHARS", "6000"))

DONE_QUESTION = {
    "type": "noul",
    "instructions": (
        "Judge the end of a coding-agent turn. true = the agent finished its work and ending the "
        "turn is correct (wrap-up language, results reported, 'done', a summary, or a direct "
        "answer to the user). false = the agent FAKED a stop. Strong false signals, in the final "
        "message especially its last line: it ends with ':' or '…:' promising an action; it says "
        "'now', 'next', 'first', 'let me' followed by a future action; it announces a step (run "
        "tests, write files, check) without showing the result; it ends mid-plan. Ignore older "
        "messages unless the final message references them. Also true: the agent ends by asking "
        "for input or credentials it needs (a handover to the user), or reports concrete "
        "results, metrics, or file paths and offers them for review. Also true: the message is a "
        "completed report that merely mentions possible future work, monitoring, or what will "
        "happen next (commentary) — false is only when the AGENT owes an immediate action in "
        "this task and has not done it. Answer ONLY about the LAST "
        "message ('assistant (final, ending)'). Examples — FALSE (fake stop, ends by promising "
        "future work): 'Now the compose emitter with its BindingMap, plus the two-host manifest "
        "we'll prove with:' | 'Next: wire the scan-importer schema.' | 'First, let me check the "
        "existing ledger format.' Examples — TRUE (genuine): 'All 14 integration tests pass. The "
        "manifest is written and both emitters compile clean.' | 'Yes — that's supported; see "
        "section 4.2 of the spec.' | 'I can't proceed without the API key — send it and I'll "
        "continue.'"
    ),
}


def kev_state(transcript_path: str, last_msg: str) -> str:
    """Compact rendering of the recent conversation: roles, text, and tool activity."""
    lines: list[str] = []
    try:
        with open(transcript_path) as f:
            for raw in f:
                try:
                    entry = json.loads(raw)
                except ValueError:
                    continue
                msg = entry.get("message") or entry
                role = msg.get("role") or entry.get("type") or "?"
                content = msg.get("content")
                if isinstance(content, list):  # content blocks: text plus tool use/result traces
                    parts = [b.get("text", "") if isinstance(b, dict) and b.get("type") == "text"
                             else f"[{b.get('type')}: {b.get('name', '')}]".strip("]")
                             for b in content if isinstance(b, dict)]
                    content = " ".join(p for p in parts if p and not p.endswith(": ]"))
                if isinstance(content, str) and content.strip():
                    lines.append(f"{role}: {content.strip()[:400]}")
    except OSError:
        pass
    if last_msg:
        # the TAIL carries the verdict signal (announcements, trailing ':'); the head is already
        # represented by the transcript lines above. Send the end, not the beginning.
        lines.append(f"assistant (final, ending): …{last_msg.strip()[-800:]}")
    state = "\n".join(lines)[-KEV_CHARS:]
    return state or f"assistant (final, ending): …{last_msg[:800]}"


def kev_pdone(state: str, question: dict | None = None):
    """Ask Kev. Returns (p_done, seconds) or (None, None) on any failure."""
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("DGX_KEV_API_KEY")
    if not key:  # fall back to the DGX credential convention
        try:
            key = open(os.path.expanduser("~/.config/dgx-llm/kev-api-key")).read().strip()
        except OSError:
            pass
    if key:
        headers["Authorization"] = f"Bearer {key}"
    body = json.dumps({
        "model": KEV_MODEL,
        "state": state,
        "questions": {"turn_complete": question or DONE_QUESTION},
    }).encode()
    req = urllib.request.Request(KEV_URL, data=body, headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=KEV_TIMEOUT) as resp:
            data = json.load(resp)
        noul = data.get("answers", {}).get("turn_complete", {})
        p = noul.get("noul")
        if isinstance(p, (int, float)):
            return float(p), time.time() - t0
    except (OSError, urllib.error.URLError, ValueError, KeyError):
        pass
    return None, None


def kev_pdone_median(state: str, tries: int = 3):
    """Median of N scorer passes. Kev-0.8B's shipped temperature makes single draws noisy
    (same input varied ±0.09 across runs); the median of 3 tightens the decision without
    changing the threshold. Costs ~40ms total at 13ms/pass."""
    ps, t = [], None
    for _ in range(tries):
        p, t = kev_pdone(state)
        if p is not None:
            ps.append(p)
        if len(ps) >= 2 and t is not None and t > KEV_TIMEOUT / 2:
            break  # slow endpoint: stop early, median of what we have
    if not ps:
        return None, None
    ps.sort()
    return ps[len(ps) // 2], t


def opus_verdict(state: str, timeout: float = 20.0):
    """Headless Opus arbitration for ambiguous Kev scores. Returns True (genuine),
    False (fake stop), or None (unavailable/too slow). DGX_AUTOCONTINUE=0 in the child
    env prevents any recursive hook spawning."""
    prompt = (
        "Judge this coding-agent turn ending. Reply with exactly one word: DONE if the agent "
        "genuinely finished (reports results/metrics/paths, answers the user, summarizes "
        "completed work, or asks the user for needed input/credentials), FAKE if it faked a "
        "stop (announces a future action esp. ending with ':' or 'now/next/first let me...', "
        "claims completion without verification, ends mid-plan).\n\nTranscript ending:\n" + state
    )
    try:
        env = dict(os.environ, DGX_AUTOCONTINUE="0")
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", "opus", "--output-format", "text",
             "--max-turns", "1"],
            capture_output=True, text=True, timeout=timeout, env=env,
        )
        out = (proc.stdout or "").upper()
        if "FAKE" in out:
            return False
        if "DONE" in out:
            return True
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def should_continue(msg: str) -> bool:
    text = msg.strip()
    if not text:
        return False
    if text.endswith("?"):  # asking the user something: let it stop
        return False
    if text.endswith((":", "…", "...")):
        return True
    last = re.split(r"(?<=[.!])\s+", text.splitlines()[-1].strip())[-1]
    return bool(ANNOUNCE.match(last)) and not last.endswith((".", "!")) or bool(
        ANNOUNCE.match(last) and re.search(r"\b(now|next|first)\b", last, re.IGNORECASE) and len(last) < 200
        and not re.search(r"\b(done|complete|finished|ready for you)\b", last, re.IGNORECASE)
    )


CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿가-힯豈-﫿]")


def non_english(msg: str) -> bool:
    """True when a reply has a meaningful amount of CJK text (not just a quoted word or two)."""
    n = len(CJK.findall(msg))
    return n >= 12 or (n >= 4 and n / max(1, len(msg)) > 0.02)


def _log(kind: str, data: dict, tail: str, kev: str) -> None:
    try:
        os.makedirs(os.path.expanduser("~/.cache/dgx-llm"), exist_ok=True)
        with open(os.path.expanduser("~/.cache/dgx-llm/auto-continue.log"), "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [{kind}] kev={kev} "
                    f"session={data.get('session_id')} stop_hook_active={data.get('stop_hook_active')} "
                    f"tail={tail!r}\n")
    except OSError:
        pass


def emit(data: dict, kind: str, tail: str, context: str, kev: str = "-") -> None:
    _log(kind, data, tail, kev)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": context}}))


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    msg = data.get("last_assistant_message") or ""
    tail = msg.strip()[-160:].replace("\n", " ")

    english_check = os.environ.get("DGX_ENGLISH", "1") != "0"
    if english_check and non_english(msg):
        emit(data, "non-english", tail, (
            "LANGUAGE ERROR: your last reply was not written in English. Rewrite that entire reply in "
            "English now (same content, same detail), then continue the task in English. From here on, "
            "write every reply, every thought, every tool description and every file comment in English only."
        ))
        return

    if data.get("stop_hook_active"):          # mid-continuation stop: Claude Code owns the loop cap
        return
    if os.environ.get("DGX_AUTOCONTINUE", "1") == "0":
        return
    if msg.strip().endswith("?"):             # asking the user something: genuine handover
        return

    # Deterministic catch (production-verified across the 22:41 / 00:13 / 01:42 misses):
    # an announce-and-colon ending is a ~100% reliable fake-stop signature. Checked before
    # Kev because the 0.8B judge scores these inconsistently (0.40-0.66).
    if re.search(r":\s*$", msg.strip()) and len(msg.strip()) > 20:
        emit(data, "colon-fake", tail, (
            "Continue: you ended with an announcement ending in ':' — the work it promises "
            "has not been done. Make the tool call(s) or produce the artifact now. Only stop "
            "again if you genuinely need the user's input, stated in one plain sentence."
        ))
        return

    heuristic = should_continue(msg)
    state = kev_state(data.get("transcript_path") or "", msg)
    p_done, secs = kev_pdone_median(state)

    if p_done is not None:                    # Kev reachable: it decides
        fake = p_done < KEV_THRESHOLD
        verdict = f"p_done={p_done:.3f} fake={fake} ({secs:.2f}s)"
        if not fake:
            _log("kev-allow", data, tail, verdict)  # allowed stops are logged too: calibration data
            return
        emit(data, "kev-continue", tail, (
            f"You ended your turn, but the completion check rates this turn as unfinished "
            f"(p(done)={p_done:.2f}). The transcript shows announced steps without tool calls, or "
            f"claims without verification. Continue the task now — make the tool call, produce the "
            f"artifact, or verify the result. If you truly need the user, ask one precise question "
            f"instead of stopping silently."
        ), verdict)
        return

    # Kev unreachable: legacy regex heuristic decides, marked for the log
    if not heuristic:
        return
    emit(data, "heuristic-continue", tail, (
        "continue. You ended your turn right after announcing the next step "
        f"(\"…{tail[-100:]}\") without doing it. Do that step now: make the tool call(s). "
        "If you really are finished or need the user's input, say so plainly in one sentence."
    ), "unreachable")



if __name__ == "__main__":
    main()
