#!/usr/bin/env python3
"""Fleet Yearbook smoke test — cross-checks every displayed stat against the sources.

* Recomputes stats from the archived source bytes (data/sources/, sha256-verified against yearbook.json),
  with code independent of build.py, and compares them to data/yearbook.json.
* Renders the live book (http://127.0.0.1:4251/?print=1) and the offline snapshot with headless Chrome and
  checks what's displayed: per-bot facts, superlative/motto citations, signatures, class stats, awards, matrix.
* Checks jobs come from each bot's own profile.json, text stays kind, the snapshot is self-contained and the
  PDF has one Letter page per yearbook page.
Run: python3 tests/smoke_test.py   (exit 0 = pass)
"""
import collections, glob, hashlib, html, json, os, re, shutil, statistics, subprocess, sys, tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ET = ZoneInfo("America/New_York")
P, F, NOTES = [], [], []


def check(c, m):
    (P if c else F).append(m)
    if not c:
        print("FAIL:", m)


def et(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(ET)


def render(url):
    d = tempfile.mkdtemp(prefix="fy-test-")
    try:
        out = subprocess.run(["nice", "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--window-size=1200,900",
                              "--virtual-time-budget=4000", f"--user-data-dir={d}", "--dump-dom", url], capture_output=True, text=True, timeout=180).stdout
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return re.sub(r"<script\b[^>]*>.*?</script>", "", out, flags=re.S), out


def main():
    yb = json.load(open(os.path.join(HERE, "data", "yearbook.json")))
    # ---------- sources: archived copies match recorded hashes; note if live source moved on
    for k, v in yb["sources"].items():
        if "sha256" in v:
            a = os.path.join(HERE, v["archived"])
            check(hashlib.sha256(open(a, "rb").read()).hexdigest() == v["sha256"], f"archived {k} matches recorded sha256")
            if os.path.exists(v["path"]) and hashlib.sha256(open(v["path"], "rb").read()).hexdigest() != v["sha256"]:
                NOTES.append(f"live {v['path']} changed since build (re-run ./run.sh to refresh); checks use the archived copy")
    fleet = json.load(open(os.path.join(HERE, yb["sources"]["fleet"]["archived"])))
    strips = json.load(open(os.path.join(HERE, yb["sources"]["strips"]["archived"])))
    hub = json.load(open(os.path.join(HERE, yb["sources"]["hub"]["archived"])))
    names = {b["id"]: b["name"] for b in fleet["bots"]}
    ev = fleet["events"]

    # ---------- independent recomputation
    msgs = collections.Counter((e["from"], e["bot"]) for e in ev if e["type"] == "agent_msg" and e.get("from"))
    exp = {}
    for b in fleet["bots"]:
        i = b["id"]
        own = [e for e in ev if e["bot"] == i and e["type"] != "agent_msg"] + [e for e in ev if e["type"] == "agent_msg" and e.get("from") == i]
        runs = [r for rt in b.get("routines", []) for r in rt.get("runs", [])]
        t = [e["ts"] for e in own] + [r["start"] for r in runs]
        hrs = sorted(et(x).hour + et(x).minute / 60 for x in t)
        cast = sum(1 for s in strips["strips"] if b["name"] in {c for p in s.get("panels", []) for c in p.get("cast", [])})
        typ = collections.Counter(e["type"] for e in ev if e["bot"] == i)
        exp[b["name"]] = {
            "activities": len(t), "activeDays": len({et(x).date() for x in t}),
            "sent": sum(n for (f, _), n in msgs.items() if f == i), "received": sum(n for (_, r), n in msgs.items() if r == i),
            "toolCalls": typ["mcp_tool_call"], "shell": typ["shell_command"], "browse": typ["browser_navigation"], "computerUse": typ["computer_use_session"],
            "fileWrites": typ["file_write"], "outputs": typ["dated_output"], "boydMsgs": typ["boyd_msg"],
            "runs": len(runs), "runsOk": sum(1 for r in runs if r.get("status") == "ok"), "routines": len(b.get("routines", [])),
            "artifactWrites30d": b.get("artifactWrites30d", 0), "comicStrips": cast,
            "firstSeen": min(t) if t else None, "hourHist": [sum(1 for x in t if et(x).hour == h) for h in range(24)],
            "medianHour": statistics.median(hrs) if len(hrs) >= 3 else None,
            "partners": len({o for (f, r) in msgs for o in (f, r) if i in (f, r) and o != i}),
            "hosts": len({e.get("host") for e in ev if e["bot"] == i and e["type"] == "browser_navigation" and e.get("host")}),
            "apps": collections.Counter(e.get("app") for e in ev if e["bot"] == i and e["type"] == "mcp_tool_call"),
            "sentTo": {names.get(r, r): n for (f, r), n in msgs.items() if f == i},
            "durs": [(datetime.fromisoformat(r["end"].replace("Z", "+00:00")) - datetime.fromisoformat(r["start"].replace("Z", "+00:00"))).total_seconds() / 60 for r in runs if r.get("end")],
            "span": round((datetime.fromisoformat(max(t).replace("Z", "+00:00")) - datetime.fromisoformat(min(t).replace("Z", "+00:00"))).total_seconds() / 60, 1) if t else None,
        }

    def fact_value(name, key):
        e = exp[name]
        if key.startswith("app:"):
            return e["apps"].get(key[4:], 0)
        if key.startswith("sentTo:"):
            return e["sentTo"].get(key[7:], 0)
        if key == "medianRunMin":
            return round(statistics.median(e["durs"]), 1)
        if key == "spanMinutes":
            return e["span"]
        if key == "firstSeenDate":
            return et(e["firstSeen"]).strftime("%b %-d")
        if key == "medianTime":
            h = e["medianHour"]; hh, mm = int(h), int(round((h % 1) * 60))
            if mm == 60: hh, mm = hh + 1, 0
            return f"{(hh % 12) or 12}:{mm:02d} {'AM' if hh < 12 else 'PM'} ET"
        return e[key]

    for b in yb["bots"] + yb["alumni"]:
        s, e = b["stats"], exp[b["name"]]
        for k in ("activities", "activeDays", "sent", "received", "toolCalls", "shell", "browse", "computerUse", "fileWrites", "outputs",
                  "boydMsgs", "runs", "runsOk", "routines", "artifactWrites30d", "comicStrips", "firstSeen", "hourHist", "partners", "hosts"):
            check(s[k] == e[k], f"{b['name']}: {k}={s[k]} recomputes to {e[k]}")
        for which in ("superlative", "motto"):
            c = b.get(which)
            if not c:
                continue
            for f in c["facts"]:
                v = fact_value(b["name"], f["key"])
                check(f["value"] == v, f"{b['name']} {which} fact {f['key']}={f['value']} recomputes to {v}")
                shown = f"{v:,}" if isinstance(v, int) else str(v)
                check(shown in c["stat"], f"{b['name']} {which} citation shows '{shown}'")
            check(not re.search(r"\b(worst|lazy|useless|slowest|least|fail|dumb|boring|loser)\b", c["text"] + " " + c["stat"], re.I), f"{b['name']} {which} is kind")
        if which and b.get("superlative"):
            check(b["superlative"]["title"].startswith("Most likely to"), f"{b['name']} superlative is a 'most likely to…'")
        # signatures
        for g in b.get("signatures", []):
            if g.get("boyd"):
                check(g["toYou"] == e["boydMsgs"], f"{b['name']}: Boyd signature count {g['toYou']}")
            else:
                fid = next(k for k, v in names.items() if v == g["from"])
                check(g["toYou"] == msgs.get((fid, b["id"]), 0) and g["fromYou"] == msgs.get((b["id"], fid), 0), f"{b['name']}: {g['from']} signature {g['toYou']}/{g['fromYou']}")
    # profiles: job + title come from each bot's own profile.json (live files)
    for b in yb["bots"]:
        pf = f"/home/box/agent-data/agents/{b['id']}/profile.json"
        prof = json.load(open(pf))
        check((prof.get("title") or "") == b["title"] or not prof.get("title"), f"{b['name']}: title from profile.json")
        words = [w for w in re.findall(r"[A-Za-z]{6,}", b["job"]) if w.lower() not in ("prepares", "watches", "spots", "makes", "owns", "ships", "designs")]
        desc = (prof.get("description") or "").lower()
        check(all(w.lower() in desc for w in words), f"{b['name']}: job words all come from its profile.json")
    # class + awards
    K = yb["class"]
    check(K["events"] == len(ev) and K["messagesBetweenBots"] == sum(msgs.values()) and K["boydMsgs"] == sum(1 for e in ev if e["type"] == "boyd_msg"), "class totals recompute")
    allruns = [r for b in fleet["bots"] for rt in b.get("routines", []) for r in rt.get("runs", [])]
    check(K["runs"] == len(allruns) and K["runsOk"] == sum(1 for r in allruns if r.get("status") == "ok"), "class routine runs recompute")
    days = collections.Counter(et(e["ts"]).date().isoformat() for e in ev)
    check(K["activeDays"] == len(days) and K["busiestDay"] == days.most_common(1)[0][0] and K["busiestDayCount"] == days.most_common(1)[0][1], "class busiest day recomputes")
    pairs = collections.Counter()
    for (f, r), n in msgs.items():
        pairs[frozenset((f, r))] += n
    duo, dn = pairs.most_common(1)[0]
    check(yb["awards"][0]["value"] == dn and set(yb["awards"][0]["winner"].split(" & ")) == {names[i] for i in duo}, f"Best Duo = {yb['awards'][0]['winner']} ({dn})")
    for a in yb["awards"][1:]:
        if a["key"] in ("apps", "boydMsgs", "browse", "shell", "computerUse", "comicStrips"):
            ws = a["winner"].split(" & ")
            vals = {n: (len(exp[n]["apps"]) if a["key"] == "apps" else exp[n][a["key"]]) for n in exp if n in {x["name"] for x in yb["bots"]}}
            best = max(vals.values())
            check(a["value"] == best and all(vals[w] == best for w in ws), f"award {a['title']} → {a['winner']} ({best})")

    # ---------- displayed DOM (live + snapshot)
    for label, url in (("live", "http://127.0.0.1:4251/?print=1"), ("snapshot", "file://" + os.path.join(HERE, "dist", "fleet-yearbook-snapshot.html") + "?print=1")):
        dom, full = render(url)
        pages = re.findall(r'<div class="page[ "]', dom)
        check(len(pages) == len(yb["bots"]) + 7, f"[{label}] {len(pages)} pages rendered")
        for b in yb["bots"]:
            m = re.search(r'data-bot="' + re.escape(html.escape(b["name"])) + r'" style=.*?(?=<div class="page[ "]|$)', dom, re.S)
            check(bool(m), f"[{label}] portrait page for {b['name']}")
            if not m:
                continue
            pg, e = m.group(0), exp[b["name"]]
            def shown(k):
                mm = re.search(rf'data-k="{k}">([^<]*)<', pg); return html.unescape(mm.group(1)) if mm else None
            check(shown("activities") == f"{e['activities']:,}", f"[{label}] {b['name']} logged actions {shown('activities')}")
            check(shown("activeDays") == str(e["activeDays"]), f"[{label}] {b['name']} active days")
            check(shown("sentReceived") == f"{e['sent']} / {e['received']}", f"[{label}] {b['name']} sent/received {shown('sentReceived')}")
            check(shown("toolCalls") == f"{e['toolCalls']:,}", f"[{label}] {b['name']} tool calls")
            check(shown("runs") == (f"{e['runsOk']}/{e['runs']}" if e["runs"] else "—"), f"[{label}] {b['name']} routine runs")
            check(shown("firstSeen") == (et(e["firstSeen"]).strftime("%b %-d")), f"[{label}] {b['name']} joined {shown('firstSeen')}")
            hh = re.search(r'data-hours="([^"]+)"', pg)
            check(hh and [int(x) for x in hh.group(1).split(",")] == e["hourHist"], f"[{label}] {b['name']} hour chart")
            check(html.escape(b["superlative"]["stat"], quote=False) in pg and html.escape(b["motto"]["stat"], quote=False) in pg, f"[{label}] {b['name']} citations displayed under superlative + motto")
            check(html.escape(b["job"], quote=False) in pg, f"[{label}] {b['name']} job line displayed")
            for sg in re.findall(r'data-sig="([^"]+)" data-to="(\d+)"(?: data-from="(\d+)")?', pg):
                frm = html.unescape(sg[0])
                if frm == "Boyd":
                    check(int(sg[1]) == e["boydMsgs"], f"[{label}] {b['name']} Boyd signature")
                else:
                    fid = next(k for k, v in names.items() if v == frm)
                    check(int(sg[1]) == msgs[(fid, b["id"])] if (fid, b["id"]) in msgs else int(sg[1]) == 0, f"[{label}] {b['name']} ← {frm} count")
                    check(int(sg[2]) == msgs.get((b["id"], fid), 0), f"[{label}] {b['name']} → {frm} count")
        for k, v in (("events", f"{len(ev):,}"), ("messagesBetweenBots", f"{sum(msgs.values()):,}"), ("boydMsgs", str(K["boydMsgs"]))):
            check(re.search(rf'data-k="{k}">{re.escape(v)}<', dom) is not None, f"[{label}] class stat {k}={v}")
        cells = re.findall(r'data-f="([^"]+)" data-t="([^"]+)">(\d+)<', dom)
        inv = {v: k for k, v in names.items()}
        check(cells and all(msgs[(inv[html.unescape(f)], inv[html.unescape(t)])] == int(n) for f, t, n in cells), f"[{label}] autograph matrix ({len(cells)} cells) matches messages")
        check(len(re.findall(r'class="award"', dom)) == len(yb["awards"]), f"[{label}] {len(yb['awards'])} awards shown")
        if label == "snapshot":
            body = full.split("<body", 1)[1]
            check(not re.search(r'<script[^>]+src=|<link[^>]+href=', full), "[snapshot] no external scripts/styles")
    # ---------- PDF
    pdf = os.path.join(HERE, "dist", "fleet-yearbook.pdf")
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    check(f"Pages:           {len(yb['bots']) + 7}" in info and "612 x 792" in info, "PDF: one Letter page per yearbook page")
    txt = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
    check(all(b["name"] in txt for b in yb["bots"]), "PDF text includes every classmate")
    print(f"\n{len(P)} passed, {len(F)} failed")
    for n in sorted(set(NOTES)):
        print("note:", n)
    sys.exit(1 if F else 0)


if __name__ == "__main__":
    main()
