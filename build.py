#!/usr/bin/env python3
"""Fleet Yearbook builder: computes every stat from read-only sources and writes data/yearbook.json.

Sources (read-only; a byte-for-byte copy of each is archived in data/sources/ for reproducible tests):
  /workspace/tokenmax/bot-island/data/fleet.json        events, routines, colors, shapes, buildings
  /workspace/tokenmax/agent-playbook/data/playbook.json fleet roster (one-liners, schedules)
  /workspace/tokenmax/fleet-funnies/data/strips.json    comic strips (count of strips each bot stars in)
  /home/box/agent-data/agents/*/profile.json            name, title, job description
No message contents are read or quoted: only event types, timestamps, sender and recipient ids.
"""
import collections, glob, hashlib, json, os, re, shutil, statistics
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ET = ZoneInfo("America/New_York")
SRC = {
    "fleet": "/workspace/tokenmax/bot-island/data/fleet.json",
    "playbook": "/workspace/tokenmax/agent-playbook/data/playbook.json",
    "strips": "/workspace/tokenmax/fleet-funnies/data/strips.json",
    "hub": "/workspace/tokenmax/fleet-funnies/data/hub-snapshot.json",
}
PROFILES = "/home/box/agent-data/agents/*/profile.json"
COLORS = {"blue": "#3b82f6", "red": "#ef4444", "green": "#22c55e", "yellow": "#eab308", "gray": "#94a3b8", "orange": "#f97316",
          "cyan": "#06b6d4", "violet": "#8b5cf6", "magenta": "#d946ef", "purple": "#8b5cf6", "pink": "#ec4899", "teal": "#14b8a6"}  # Bot Island web/app.js


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def et(s):
    return ts(s).astimezone(ET)


def archive():
    """Copy sources into data/sources (so tests can re-derive from the exact bytes used)."""
    out = {}
    for k, p in SRC.items():
        dst = os.path.join(HERE, "data", "sources", os.path.basename(p))
        shutil.copyfile(p, dst)
        out[k] = {"path": p, "archived": os.path.relpath(dst, HERE), "sha256": sha(dst), "mtime": datetime.fromtimestamp(os.path.getmtime(p), timezone.utc).isoformat()}
    pdir = os.path.join(HERE, "data", "sources", "profiles")
    os.makedirs(pdir, exist_ok=True)
    profs = {}
    for p in sorted(glob.glob(PROFILES)):
        aid = p.split("/")[-2]
        d = json.load(open(p))
        # keep only the fields the yearbook uses
        keep = {k: d.get(k) for k in ("name", "title", "description", "avatarShape", "avatarColor")}
        json.dump(keep, open(os.path.join(pdir, aid + ".json"), "w"), indent=1)
        profs[aid] = keep
    out["profiles"] = {"path": PROFILES, "archived": "data/sources/profiles/", "count": len(profs)}
    return out, profs


def _verb3(m):
    v = m.group(1)
    return (v + ("es" if re.search(r"(ch|sh|x|s)$", v) else "s")).capitalize()


def job_line(desc, title, name=""):
    """Opening sentence(s) of the bot's own profile description, lightly cleaned (second person → plain)."""
    if not desc:
        return title or ""
    out = []
    for s in re.split(r"(?<=[.!?])\s+", desc.strip()):
        s = re.sub(r"^You are (my |the |)", "", s)
        if s.startswith("Your ONLY job is to "):
            s = re.sub(r"^Your ONLY job is to (\w+)", lambda m: _verb3(m), s)
        if name:
            s = re.sub(r"^" + re.escape(name) + r"(, | — )", "", s)
        if ":" in s:
            s = re.sub(r",?\s*(using)?\s*$", "", s.split(":")[0]) + "."
        s = re.sub(r"^You (\w+)", _verb3, s)
        s = s[:1].upper() + s[1:]
        out.append(s)
        if len(" ".join(out)) >= 34:
            break
    j = " ".join(out)
    return j if len(j) <= 230 else j[:227].rsplit(" ", 1)[0] + "…"


def build():
    sources, profs = archive()
    fleet = json.load(open(os.path.join(HERE, sources["fleet"]["archived"])))
    playbook = json.load(open(os.path.join(HERE, sources["playbook"]["archived"])))
    strips = json.load(open(os.path.join(HERE, sources["strips"]["archived"])))
    hub = json.load(open(os.path.join(HERE, sources["hub"]["archived"])))
    hubbots = {h["name"]: h for h in hub.get("bots", [])}
    names = {b["id"]: b["name"] for b in fleet["bots"]}
    pb = {f["name"]: f for f in playbook.get("fleet", [])}

    # comic-strip appearances (Fleet Funnies cast lists)
    cast = collections.Counter()
    for st in strips.get("strips", []):
        seen = set()
        for pn in st.get("panels", []):
            for c in pn.get("cast", []):
                seen.add(c)
        for c in seen:
            cast[c] += 1

    ev = fleet["events"]
    per = collections.defaultdict(list)
    for e in ev:
        per[e["bot"]].append(e)
    msgs = collections.Counter()  # (from, to) -> n
    msg_first, msg_days = {}, collections.defaultdict(collections.Counter)
    for e in ev:
        if e["type"] == "agent_msg" and e.get("from"):
            k = (e["from"], e["bot"])
            msgs[k] += 1
            msg_first[k] = min(msg_first.get(k, e["ts"]), e["ts"])
            msg_days[frozenset(k)][et(e["ts"]).date().isoformat()] += 1

    bots = []
    for b in fleet["bots"]:
        bid = b["id"]
        prof = profs.get(bid)
        mine = per.get(bid, [])
        sent = [e for e in ev if e["type"] == "agent_msg" and e.get("from") == bid]
        acts = [e for e in mine if e["type"] != "agent_msg"] + sent  # things this bot did (received msgs aren't its activity)
        runs = [r for rt in b.get("routines", []) for r in rt.get("runs", [])]
        stamps = [e["ts"] for e in acts] + [r["start"] for r in runs]
        tcount = collections.Counter(e["type"] for e in mine)
        hours = [et(s).hour + et(s).minute / 60 for s in stamps]
        days = collections.Counter(et(s).date().isoformat() for s in stamps)
        durs = [(ts(r["end"]) - ts(r["start"])).total_seconds() / 60 for r in runs if r.get("end")]
        apps = collections.Counter(e.get("app") for e in mine if e["type"] == "mcp_tool_call")
        hosts = {e.get("host") for e in mine if e["type"] == "browser_navigation" and e.get("host")}
        partners = {o for (f, t) in msgs for o in (f, t) if bid in (f, t) and o != bid}
        s = {
            "toolCalls": tcount["mcp_tool_call"], "shell": tcount["shell_command"], "browse": tcount["browser_navigation"],
            "computerUse": tcount["computer_use_session"], "fileWrites": tcount["file_write"], "outputs": tcount["dated_output"],
            "boydMsgs": tcount["boyd_msg"],
            "sent": sum(n for (f, t), n in msgs.items() if f == bid), "received": sum(n for (f, t), n in msgs.items() if t == bid),
            "partners": len(partners), "apps": len(apps), "topApp": apps.most_common(1)[0][0] if apps else None,
            "topAppCalls": apps.most_common(1)[0][1] if apps else 0, "hosts": len(hosts),
            "routines": len(b.get("routines", [])), "routinesEnabled": sum(1 for r in b.get("routines", []) if r.get("enabled")),
            "runs": len(runs), "runsOk": sum(1 for r in runs if r.get("status") == "ok"),
            "medianRunMin": round(statistics.median(durs), 1) if len(durs) >= 2 else None,
            "artifactWrites30d": b.get("artifactWrites30d", 0),
            "activities": len(stamps), "activeDays": len(days),
            "busiestDay": days.most_common(1)[0][0] if days else None, "busiestDayCount": days.most_common(1)[0][1] if days else 0,
            "medianHour": round(statistics.median(hours), 2) if len(hours) >= 3 else None,
            "firstSeen": min(stamps) if stamps else None, "lastSeen": max(stamps) if stamps else None,
            "comicStrips": cast.get(b["name"], 0),
            "hourHist": [sum(1 for s_ in stamps if et(s_).hour == h) for h in range(24)],
        }
        bots.append({
            "id": bid, "name": b["name"], "hasProfile": prof is not None,
            "title": (prof or {}).get("title") or b.get("title") or (pb.get(b["name"], {}).get("title")) or "",
            "job": job_line((prof or {}).get("description"), b.get("title"), b["name"]),
            "jobSource": f"profile.json ({bid[:8]})" if prof and prof.get("description") else "Bot Island title",
            "color": b.get("color"), "hex": COLORS.get(b.get("color"), "#94a3b8"), "shape": b.get("shape"), "building": b.get("building"),
            "routineNames": [r["name"] for r in b.get("routines", [])],
            "schedule": (hubbots.get(b["name"]) or {}).get("schedule", []),
            "paused": (hubbots.get(b["name"]) or {}).get("paused", []),
            "rhythm": (hubbots.get(b["name"]) or {}).get("rhythm", []),
            "playbook": {k: pb.get(b["name"], {}).get(k) for k in ("only", "quiet")} if b["name"] in pb else None,
            "stats": s,
        })

    # ---- extra per-bot facts used by superlatives / mottos
    for x in bots:
        bid, st = x["id"], x["stats"]
        mine = per.get(bid, [])
        st["appCalls"] = dict(collections.Counter(e.get("app") for e in mine if e["type"] == "mcp_tool_call"))
        st["sentTo"] = {names.get(t, t): n for (f, t), n in msgs.items() if f == bid}
        st["spanMinutes"] = round((ts(st["lastSeen"]) - ts(st["firstSeen"])).total_seconds() / 60, 1) if st["firstSeen"] else None
        st["firstSeenDate"] = et(st["firstSeen"]).strftime("%b %-d") if st["firstSeen"] else None
        st["medianTime"] = None
        if st["medianHour"] is not None:
            h = st["medianHour"]; hh, mm = int(h), int(round((h % 1) * 60))
            if mm == 60: hh, mm = hh + 1, 0
            st["medianTime"] = f"{(hh % 12) or 12}:{mm:02d} {'AM' if hh < 12 else 'PM'} ET"
    klass_bots = [x for x in bots if x["hasProfile"]]

    def fact(x, key):
        st = x["stats"]
        if ":" in key:
            kind, arg = key.split(":", 1)
            return (st["appCalls"] if kind == "app" else st["sentTo"]).get(arg, 0)
        return st.get(key)

    LOWER = {"medianRunMin", "medianHour", "spanMinutes"}

    def rank_note(x, key):
        if key in ("firstSeenDate", "medianTime", "runsOk"):
            key = {"firstSeenDate": "firstSeen", "medianTime": "medianHour", "runsOk": None}[key]
            if key is None:
                return None
        vals = [fact(y, key) for y in klass_bots]
        vals = [v for v in vals if v not in (None, 0)]
        v = fact(x, key)
        if v in (None, 0) or len(vals) < 1:
            return None
        if len(vals) == 1:
            return "the only one in the class"
        best = (max(vals) if key not in LOWER else min(vals))
        if key == "firstSeen":
            best = max(vals)
        if v == best:
            return "tied for #1 in the class" if vals.count(v) > 1 else "#1 in the class"
        return None

    # Curated "most likely to…" lines. The words are ours; every number is computed from the sources above.
    # Each spec: (title, [fact keys], text template using {k} placeholders, rank key)
    SPECS = {
        "Michael": (("Most likely to delegate it to exactly the right bot", ["sent", "partners"], "Sent {sent} messages to {partners} classmates", "sent"),
                    ("My door (and inbox) is always open.", ["received"], "Received {received} messages from classmates", "received")),
        "Jim": (("Most likely to show up every single day", ["activeDays"], "Active on {activeDays} different days", "activeDays"),
                ("If Boyd saved it, I've read it.", ["app:Notion", "routines"], "{app:Notion} Notion tool calls · {routines} scheduled routines", "routines")),
        "Oscar": (("Most likely to never miss a bill", ["runsOk", "runs", "routines"], "{runsOk} of {runs} routine runs finished OK across {routines} routines", "routines"),
                  ("Every receipt has a home.", ["app:Drive"], "{app:Drive} Google Drive tool calls — the top app", "app:Drive")),
        "Pam": (("Most likely to have the week sorted by 7:30 AM", ["runsOk", "runs"], "{runsOk} of {runs} weekday calendar scans finished OK", None),
                ("Plan ahead, then tell Michael.", ["sentTo:Michael", "sent"], "{sentTo:Michael} of {sent} messages sent went to Michael", None)),
        "Kelly": (("Most likely to spot it on X first", ["app:X"], "{app:X} X tool calls", "app:X"),
                  ("Report straight to the top.", ["sentTo:Michael", "sent"], "{sentTo:Michael} of {sent} messages sent went to Michael", None)),
        "Dwight": (("Most likely to get it done in one sitting", ["activities", "spanMinutes"], "All {activities} logged actions happened within {spanMinutes} minutes", "spanMinutes"),
                   ("Home is where the prompt is.", ["shell", "activities"], "{shell} of {activities} logged actions were shell commands", None)),
        "Dr. EggBot": (("Most likely to know everyone's name", ["partners"], "Traded messages with {partners} different classmates", "partners"),
                       ("Checkups keep the flock healthy.", ["runsOk", "runs", "routines"], "{runsOk} of {runs} health-check runs finished OK ({routines} routines)", None)),
        "Char Tutor": (("Most likely to pull up a chair and study with you", ["computerUse"], "{computerUse} computer-use sessions", "computerUse"),
                       ("Homework first, then high fives.", ["runsOk", "runs"], "{runsOk} of {runs} weeknight check-ins finished OK", None)),
        "Vic Tutor": (("Most likely to find the answer on the web", ["browse", "hosts"], "{browse} page visits across {hosts} sites", "browse"),
                      ("Quick check-ins, big wins.", ["medianRunMin"], "Median check-in run: {medianRunMin} min", "medianRunMin")),
        "Brief": (("Most likely to read your calendar before you do", ["app:Calendar", "toolCalls"], "{app:Calendar} of its {toolCalls} tool calls were Calendar", None),
                  ("Everything you need by 8 AM.", ["runsOk", "runs"], "{runsOk} of {runs} morning brief runs finished OK", None)),
        "Boyd Family Times": (("Most likely to make headlines", ["outputs"], "{outputs} dated editions logged", "outputs"),
                              ("All the news that fits, before sunrise.", ["medianTime"], "Typical activity time: {medianTime}", "medianTime")),
        "Pods": (("Most likely to have your playlist ready", ["fileWrites", "activeDays"], "{fileWrites} files written across {activeDays} days", None),
                 ("Fresh episodes, early.", ["medianTime"], "Typical activity time: {medianTime}", None)),
        "Path": (("Most likely to map out the next four years", ["fileWrites", "activeDays", "firstSeenDate"], "{fileWrites} files written across {activeDays} days since {firstSeenDate}", None),
                 ("One step at a time, every morning.", ["medianTime"], "Typical activity time: {medianTime}", None)),
        "Ryan": (("Most likely to pitch Jim a side hustle", ["sentTo:Jim", "sent"], "{sentTo:Jim} of {sent} messages sent went to Jim", None),
                 ("Big ideas, once a week.", ["runsOk", "runs"], "Weekly idea digest: {runsOk} of {runs} logged run(s) finished OK", None)),
        "TokenMax": (("Most likely to use every last token", ["fileWrites", "firstSeenDate"], "{fileWrites} files written on day one ({firstSeenDate})", None),
                     ("Use it or lose it.", ["firstSeenDate"], "Newest in the class: first logged activity {firstSeenDate}", "firstSeenDate")),
    }

    def cite(x, spec):
        title, keys, tmpl, rk = spec
        vals = {k: fact(x, k) for k in keys}
        txt = tmpl
        for k, v in vals.items():
            txt = txt.replace("{" + k + "}", f"{v:,}" if isinstance(v, int) else str(v))
        return {"text": title, "stat": txt, "facts": [{"key": k, "value": v} for k, v in vals.items()], "rankText": rank_note(x, rk) if rk else None}

    for x in bots:
        sp = SPECS.get(x["name"])
        if sp and x["hasProfile"]:
            x["superlative"], x["motto"] = cite(x, sp[0]), cite(x, sp[1])
            x["superlative"]["title"] = x["superlative"]["text"]
        elif x["hasProfile"]:  # a future classmate without a curated line still gets a grounded one
            x["superlative"] = cite(x, ("Most likely to surprise us next year", ["activities"], "{activities} logged actions so far", None))
            x["superlative"]["title"] = x["superlative"]["text"]
            x["motto"] = cite(x, ("Just getting started.", ["activeDays"], "Active on {activeDays} days", None))
        else:
            x["superlative"] = x["motto"] = None

    # ---- signatures: classmates who messaged this bot, with counts both ways
    for x in bots:
        sigs = []
        for y in bots + [{"id": k, "name": names.get(k, k)} for k in set()]:
            if y["id"] == x["id"]:
                continue
            a, b_ = msgs.get((y["id"], x["id"]), 0), msgs.get((x["id"], y["id"]), 0)
            if a or b_:
                k = frozenset((x["id"], y["id"]))
                firsts = [msg_first[p] for p in ((y["id"], x["id"]), (x["id"], y["id"])) if p in msg_first]
                bd = msg_days[k].most_common(1)[0]
                sigs.append({"from": y["name"], "fromId": y["id"], "hex": y["hex"], "toYou": a, "fromYou": b_, "total": a + b_,
                             "first": min(firsts), "busiestDay": bd[0], "busiestDayCount": bd[1], "daysTalked": len(msg_days[k])})
        sigs.sort(key=lambda z: -z["total"])
        if x["stats"]["boydMsgs"]:
            sigs.append({"from": "Boyd", "fromId": "boyd", "hex": "#111827", "boyd": True, "toYou": x["stats"]["boydMsgs"], "fromYou": None, "total": x["stats"]["boydMsgs"]})
        x["signatures"] = sigs

    # ---- class stats + awards
    tc = collections.Counter(e["type"] for e in ev)
    daycount = collections.Counter(et(e["ts"]).date().isoformat() for e in ev)
    pairs = collections.Counter()
    for (f, t), n in msgs.items():
        pairs[frozenset((f, t))] += n
    duo, duo_n = pairs.most_common(1)[0]
    duo_names = sorted(names[i] for i in duo)
    all_runs = [(x["name"], r) for b in fleet["bots"] for rt in b.get("routines", []) for r in rt.get("runs", []) for x in [b]]
    logs_end = fleet.get("sources", {}).get("auditNewest")
    klass = {
        "bots": len(bots), "withProfile": sum(1 for x in bots if x["hasProfile"]),
        "events": len(ev), "byType": dict(tc),
        "messagesBetweenBots": sum(msgs.values()), "messagePairs": len(pairs), "boydMsgs": tc["boyd_msg"],
        "routines": sum(x["stats"]["routines"] for x in bots), "routinesEnabled": sum(x["stats"]["routinesEnabled"] for x in bots),
        "runs": len(all_runs), "runsOk": sum(1 for _, r in all_runs if r.get("status") == "ok"),
        "firstEvent": min(e["ts"] for e in ev), "lastEvent": max(e["ts"] for e in ev),
        "busiestDay": daycount.most_common(1)[0][0], "busiestDayCount": daycount.most_common(1)[0][1],
        "activeDays": len(daycount), "logsNote": f"Activity logs (tool calls, messages, browsing) run through {logs_end}; file writes and outputs continue to {fleet.get('sources', {}).get('filesNewest')}.",
        "colors": collections.Counter(x["color"] for x in bots).most_common(),
        "eggs": [e["name"] for e in fleet.get("eggs", [])],
        "alumni": [x["name"] for x in bots if not x["hasProfile"]],
        "comicStrips": len(strips.get("strips", [])),
    }
    kb = [x for x in bots if x["hasProfile"]]

    def top(key, low=False, fmt=lambda v: f"{v:,}"):
        vals = [(x["stats"].get(key), x) for x in kb if x["stats"].get(key) not in (None, 0)]
        if not vals:
            return None
        best = (min if low else max)(v for v, _ in vals)
        w = [x for v, x in vals if v == best]
        return {"winner": " & ".join(x["name"] for x in w), "hex": [x["hex"] for x in w], "value": best, "key": key, "fmt": fmt(best), "tie": len(w) > 1}

    def award(title, t, stat):
        if t:
            awards.append({"title": title, "winner": t["winner"], "hex": t["hex"], "stat": stat.format(v=t["fmt"]), "key": t["key"], "value": t["value"]})

    awards = [{"title": "Best Duo", "winner": " & ".join(duo_names), "stat": f"{duo_n} messages between them — the most of any pair",
               "hex": [next(x["hex"] for x in bots if x["name"] == n) for n in duo_names], "key": "pair", "value": duo_n}]
    award("Biggest Toolbox", top("apps"), "Used {v} different apps")
    award("Most Messages from Boyd", top("boydMsgs"), "{v} messages from Boyd in the logs")
    award("Marathon Day", top("busiestDayCount"), "{v} logged actions in a single day")
    award("Early Bird", top("medianHour", True, lambda v: next(x["stats"]["medianTime"] for x in kb if x["stats"]["medianHour"] == v)), "Typical activity time: {v}")
    award("Night Owl", top("medianHour", False, lambda v: next(x["stats"]["medianTime"] for x in kb if x["stats"]["medianHour"] == v)), "Typical activity time: {v}")
    award("Speed Demon", top("medianRunMin", True, lambda v: f"{v}"), "Median routine run: {v} min")
    award("Comic-Strip Star", top("comicStrips"), "Stars in {v} of the 11 Fleet Funnies strips".replace("11", str(len(strips.get("strips", [])))))
    award("Web Explorer", top("browse"), "{v} page visits")
    award("Terminal Champion", top("shell"), "{v} shell commands")
    award("Most Hands-On", top("computerUse"), "{v} computer-use sessions")
    awards.append({"title": "Perfect Record (whole class)", "winner": "Every routine", "hex": ["#22c55e"],
                   "stat": f"{klass['runsOk']} of {klass['runs']} logged routine runs finished OK", "key": "runsOk", "value": klass["runsOk"]})
    awards.append({"title": "Busiest Day of the Year", "winner": datetime.fromisoformat(klass["busiestDay"]).strftime("%a %b %-d"), "hex": ["#f59e0b"],
                   "stat": f"{klass['busiestDayCount']:,} logged events fleet-wide that day (ET)", "key": "busiestDayCount", "value": klass["busiestDayCount"]})
    cc = collections.Counter(x["color"] for x in kb if x["color"] != "gray")
    col, ncol = cc.most_common(1)[0]
    awards.append({"title": "Class Color", "winner": col.title(), "hex": [COLORS[col]],
                   "stat": f"{ncol} of {len(kb)} classmates wear it on Bot Island ({', '.join(x['name'] for x in kb if x['color'] == col)})", "key": "color", "value": ncol})
    gen = {"generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "fleetGeneratedAt": fleet.get("generatedAt")}
    yb = {"meta": gen, "sources": sources, "class": klass, "awards": awards,
          "bots": sorted([x for x in bots if x["hasProfile"]], key=lambda x: x["name"].lower()),
          "alumni": [x for x in bots if not x["hasProfile"]]}
    json.dump(yb, open(os.path.join(HERE, "data", "yearbook.json"), "w"), indent=1)
    return yb


if __name__ == "__main__":
    yb = build()
    for x in yb["bots"] + yb["alumni"]:
        sp, mo = x["superlative"], x["motto"]
        print(f"{x['name']:28s} {str(sp and sp['title']):55s} | {sp and sp['stat']} ({sp and sp['rankText']})")
        print(f"{'':28s} motto: {mo and mo['text']} | {mo and mo['stat']} ({mo and mo['rankText']}) sigs={len(x['signatures'])}")
    print(yb["awards"])
    print({k: v for k, v in yb["class"].items() if k not in ("byType",)})
