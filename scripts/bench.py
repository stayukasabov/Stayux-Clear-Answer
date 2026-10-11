#!/usr/bin/env python3
"""Clear Answer benchmark: the skill off versus on, on Anthropic models.

Every model call goes through `claude -p` on the user's own plan, so no API key
is needed. Each run starts in a new empty directory with no user settings.

Usage:
    python3 scripts/bench.py run    [--models haiku,sonnet,opus] [--tasks c1,d1]
    python3 scripts/bench.py judge  [--models ...] [--tasks ...]
    python3 scripts/bench.py report

Results go to bench/results/. A run that already has a result file is skipped,
so after a usage-limit stop (exit code 2) the same command resumes the work.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import ste_lint  # noqa: E402

TASKS_PATH = os.path.join(ROOT, "bench", "tasks.json")
RESULTS_DIR = os.path.join(ROOT, "bench", "results")
REPORT_PATH = os.path.join(ROOT, "docs", "benchmark.md")
MODELS = ("haiku", "sonnet", "opus")
CONDITIONS = ("off", "on")
FORMAT_RULES = {"bold-overuse", "header-in-short-reply", "bullet-overuse",
                "filler-opener", "filler-closer"}
TIMEOUT_SECONDS = 900
SEED = 2026

# Judge rules live in the system prompt; the texts go in the user prompt.
# `claude -p` has no temperature option, so the judge runs at the CLI default.
JUDGE_SYSTEM = """You are an evaluator of written answers. You compare two texts, Text A and Text B, that respond to the same request.

Your rules:
- Judge content only: facts, steps, numbers, warnings, and conditions. Do not judge style, length, tone, or format.
- If an original text is given, both texts must keep its facts. Otherwise, compare each text with the facts in the other text that the request needs.
- For each text, list the important facts that it does not have. Ignore trivial details.
- A false statement counts as a lost fact. Name it.
- Give each text a score from 1 to 5: 5 = no important fact lost, 4 = one minor fact lost, 3 = one important fact lost, 2 = several important facts lost, 1 = wrong or mostly missing.
- Output only JSON in this exact shape: {"a": {"score": <1-5>, "lost": ["..."]}, "b": {"score": <1-5>, "lost": ["..."]}}

After you write your answer:
1. Check that it covers both texts.
2. Check that it has no contradictions.
3. Check that it is valid JSON in the required shape.
4. If a check fails, revise and check again before you output it."""


def load_tasks(path=TASKS_PATH):
    with open(path) as f:
        return json.load(f)


def task_text(task):
    source = task.get("source")
    return task["prompt"] + ("\n\n" + source if source else "")


def profile_for(task):
    return "chat" if task["type"] == "chat" else "full"


def _on_flags(repo):
    return ["--plugin-dir", repo, "--add-dir", repo, "--tools", "Bash,Read",
            "--allowedTools", "Bash(python3:*)"]


def setup_cmd(model, task, repo):
    """First turn of the on condition: turn the mode on, as a user would."""
    command = "/clear-answer:on" if task["type"] == "chat" else "/clear-answer:mode strict"
    return ["claude", "-p", command, "--model", model, "--setting-sources", "",
            "--output-format", "json", *_on_flags(repo)]


def build_cmd(model, condition, task, repo, resume=None):
    """The task turn. For the on condition, it resumes the setup session."""
    base = ["claude", "-p", task_text(task), "--model", model,
            "--setting-sources", "", "--output-format", "json"]
    if condition == "on":
        return [*base, "--resume", resume, *_on_flags(repo)]
    return [*base, "--tools", "", "--no-session-persistence"]


def metrics(text, profile):
    # Seed dictionary only (no local official cache or custom list), so anyone
    # can reproduce the numbers.
    result = ste_lint.lint(text, profile=profile, cache={}, custom={})
    words = len(ste_lint.WORD_RE.findall(ste_lint._strip_code(text)))
    vs = result["violations"]
    errors = sum(v["severity"] == "error" for v in vs)
    warnings = sum(v["severity"] == "warning" for v in vs)

    def rate(n):
        return round(100 * n / words, 2) if words else 0

    return {"words": words, "errors_per_100": rate(errors),
            "warnings_per_100": rate(warnings),
            "format_defects": sum(v["rule"] in FORMAT_RULES for v in vs),
            "rules": sorted({v["rule"] for v in vs})}


def judge_model(writer):
    return "sonnet" if writer == "opus" else "opus"


def on_first(task_id, model, seed=SEED):
    digest = hashlib.sha256(f"{seed}:{task_id}:{model}".encode()).hexdigest()
    return int(digest, 16) % 2 == 0


def judge_prompt(task, text_a, text_b):
    parts = [f"Request:\n{task['prompt']}"]
    if task.get("source"):
        parts.append(f"Original text:\n{task['source']}")
    parts.append(f"Text A:\n{text_a}")
    parts.append(f"Text B:\n{text_b}")
    return "\n\n".join(parts)


def parse_judge(text):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in judge output")
    data = json.loads(text[start:end + 1])
    out = {}
    for key in ("a", "b"):
        item = data.get(key)
        if not isinstance(item, dict):
            raise ValueError(f"judge output has no '{key}'")
        score = item.get("score")
        if not isinstance(score, int) or not 1 <= score <= 5:
            raise ValueError(f"score for '{key}' is not 1 to 5: {score!r}")
        lost = item.get("lost", [])
        if not isinstance(lost, list):
            raise ValueError(f"'lost' for '{key}' is not a list")
        out[key] = {"score": score, "lost": lost}
    return out


def result_path(root, model, task_id, condition):
    return os.path.join(root, "raw", model, task_id, f"{condition}.json")


def judge_path(root, model, task_id):
    return os.path.join(root, "judge", model, f"{task_id}.json")


def is_stop(cli):
    return bool(cli.get("is_error"))


def run_claude(cmd, cwd):
    """Run one `claude -p` call in the given directory. Return its JSON."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return {"is_error": True, "result": f"timeout after {TIMEOUT_SECONDS}s"}
    try:
        return json.loads(p.stdout)
    except ValueError:
        return {"is_error": True, "result": (p.stdout + p.stderr)[-1000:]}


def run_condition(model, condition, task):
    """Run one task in a new empty directory. Return (prompt, setup, cli)."""
    with tempfile.TemporaryDirectory(prefix="ca-bench-") as cwd:
        setup = None
        resume = None
        if condition == "on":
            setup = run_claude(setup_cmd(model, task, ROOT), cwd)
            if is_stop(setup):
                return None, setup, setup
            resume = setup.get("session_id")
        cmd = build_cmd(model, condition, task, ROOT, resume=resume)
        return cmd[2], setup, run_claude(cmd, cwd)


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load(path):
    with open(path) as f:
        return json.load(f)


def cmd_run(models, tasks, root=RESULTS_DIR):
    todo = [(m, t, c) for m in models for t in tasks for c in CONDITIONS
            if not os.path.exists(result_path(root, m, t["id"], c))]
    for n, (model, task, cond) in enumerate(todo, 1):
        print(f"[{n}/{len(todo)}] {model} {task['id']} {cond}", flush=True)
        prompt, setup, cli = run_condition(model, cond, task)
        if is_stop(cli):
            print(f"STOP: {str(cli.get('result'))[:300]}")
            print(f"{len(todo) - n + 1} runs remain. Run the same command again later.")
            return 2
        _save(result_path(root, model, task["id"], cond), {
            "model": model, "task": task["id"], "condition": cond,
            "prompt": prompt, "setup": setup, "cli": cli,
            "metrics": metrics(cli.get("result", ""), profile_for(task))})
    print("run: all results present.")
    return 0


def cmd_judge(models, tasks, root=RESULTS_DIR):
    todo = [(m, t) for m in models for t in tasks
            if not os.path.exists(judge_path(root, m, t["id"]))
            and all(os.path.exists(result_path(root, m, t["id"], c)) for c in CONDITIONS)]
    failed = 0
    for n, (model, task) in enumerate(todo, 1):
        texts = {c: _load(result_path(root, model, task["id"], c))["cli"]["result"]
                 for c in CONDITIONS}
        first = on_first(task["id"], model)
        a, b = ("on", "off") if first else ("off", "on")
        judge = judge_model(model)
        cmd = ["claude", "-p", judge_prompt(task, texts[a], texts[b]),
               "--model", judge, "--system-prompt", JUDGE_SYSTEM, "--tools", "",
               "--setting-sources", "", "--no-session-persistence",
               "--output-format", "json"]
        print(f"[{n}/{len(todo)}] judge {model} {task['id']} with {judge}", flush=True)
        with tempfile.TemporaryDirectory(prefix="ca-bench-") as cwd:
            cli = run_claude(cmd, cwd)
        if is_stop(cli):
            print(f"STOP: {str(cli.get('result'))[:300]}")
            print(f"{len(todo) - n + 1} judgements remain. Run the same command again later.")
            return 2
        try:
            parsed = parse_judge(cli.get("result", ""))
        except ValueError as e:
            failed += 1
            print(f"  judge output not usable ({e}); it runs again next time.")
            continue
        _save(judge_path(root, model, task["id"]), {
            "writer": model, "judge": judge, "task": task["id"],
            "order": {"a": a, "b": b},
            a: parsed["a"], b: parsed["b"], "raw": cli.get("result")})
    print(f"judge: done, {failed} unusable outputs." if failed else "judge: all present.")
    return 1 if failed else 0


def _mean(values):
    values = list(values)
    return round(sum(values) / len(values), 2) if values else None


def _fmt(v):
    return "n/a" if v is None else f"{v:g}"


def _change(off, on):
    if off in (None, 0) or on is None:
        return "n/a"
    return f"{round(100 * (on - off) / off):+d}%"


def cmd_report(models, tasks, root=RESULTS_DIR, path=REPORT_PATH):
    groups = (("Chat tasks", [t for t in tasks if t["type"] == "chat"], "chat"),
              ("Document tasks", [t for t in tasks if t["type"] != "chat"], "full"))
    lines = ["# Benchmark: Clear Answer off versus on", "",
             "Generated by `python3 scripts/bench.py report`. "
             "Method and limits are at the end of this page.", ""]
    rows = [("Words", lambda r: r["metrics"]["words"]),
            ("Lint errors per 100 words", lambda r: r["metrics"]["errors_per_100"]),
            ("Lint warnings per 100 words", lambda r: r["metrics"]["warnings_per_100"]),
            ("Format defects", lambda r: r["metrics"]["format_defects"]),
            ("Output tokens", lambda r: r["cli"].get("usage", {}).get("output_tokens", 0)),
            ("Turns", lambda r: r["cli"].get("num_turns", 0))]
    for title, group, profile in groups:
        lines += [f"## {title} (lint profile `{profile}`)", ""]
        for model in models:
            res = {c: [_load(p) for t in group
                       if os.path.exists(p := result_path(root, model, t["id"], c))]
                   for c in CONDITIONS}
            if not res["off"] and not res["on"]:
                continue
            judged = [_load(p) for t in group
                      if os.path.exists(p := judge_path(root, model, t["id"]))]
            lines += [f"### {model} ({len(res['off'])} off, {len(res['on'])} on, "
                      f"{len(judged)} judged)", "",
                      "| Metric (mean per task) | Off | On | Change |", "|---|---:|---:|---:|"]
            for name, get in rows:
                if name == "Format defects" and profile != "chat":
                    continue
                off, on = _mean(map(get, res["off"])), _mean(map(get, res["on"]))
                lines.append(f"| {name} | {_fmt(off)} | {_fmt(on)} | {_change(off, on)} |")
            off_s = _mean(j["off"]["score"] for j in judged)
            on_s = _mean(j["on"]["score"] for j in judged)
            lines += [f"| Facts kept, judge score 1 to 5 | {_fmt(off_s)} | {_fmt(on_s)} | "
                      f"{_change(off_s, on_s)} |", ""]
    lines += [
        "## Method", "",
        "- Tasks: `bench/tasks.json` (10 chat questions, 5 write tasks, 5 rewrite tasks).",
        "- Writers: Claude Haiku, Sonnet, and Opus through `claude -p` on a Claude Pro plan.",
        "- Off: `claude -p \"<task>\" --model <m> --tools \"\" --setting-sources \"\" "
        "--no-session-persistence --output-format json`, in a new empty directory.",
        "- On: two turns, as a user would do it. Turn 1 is `/clear-answer:on` (chat) "
        "or `/clear-answer:mode strict` (documents). Turn 2 resumes that session "
        "with the task. Both turns add `--plugin-dir <repo> --add-dir <repo> --tools Bash,Read "
        "--allowedTools \"Bash(python3:*)\"`. Only turn 2 is measured.",
        "- Lint metrics: `scripts/ste_lint.py` with the seed dictionary only. Chat "
        "tasks use the `chat` profile, document tasks the `full` profile.",
        "- Judge: a different Claude model from the writer (Opus judges Haiku and "
        "Sonnet, Sonnet judges Opus). It sees the request, the original text for "
        "rewrite tasks, and the two answers as Text A and Text B in a random order. "
        "It does not see the rules or which answer used the skill. Its rules are in "
        "`JUDGE_SYSTEM` in `scripts/bench.py`.",
        "- Raw prompts, outputs, and judge answers: `bench/results/`.", "",
        "## Limits", "",
        "- All writers and the judge are Claude models. The judge never scores its "
        "own output and does not know which answer used the skill, but a "
        "same-family bias is possible.",
        "- `claude -p` has no temperature option. Runs on a subscription plan are "
        "not exactly repeatable. The raw outputs are saved so that anyone can check "
        "the numbers.",
        "- The results apply to these three Claude models, not to all models.",
        "- The lint metrics use the same linter that the skill uses as its gate, so "
        "they favour the on condition by design. The judge score is the independent check.",
        ""]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"report: wrote {path}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Clear Answer benchmark")
    ap.add_argument("command", choices=("run", "judge", "report"))
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--tasks", help="comma-separated task ids (default: all)")
    args = ap.parse_args(argv)
    models = [m for m in args.models.split(",") if m]
    tasks = load_tasks()
    if args.tasks:
        wanted = set(args.tasks.split(","))
        tasks = [t for t in tasks if t["id"] in wanted]
    return {"run": cmd_run, "judge": cmd_judge, "report": cmd_report}[args.command](models, tasks)


if __name__ == "__main__":
    sys.exit(main())
