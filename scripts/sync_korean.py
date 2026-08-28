#!/usr/bin/env python3
"""Keep the Korean pages in step with the English ones.

    python3 scripts/sync_korean.py                  # what has drifted?
    python3 scripts/sync_korean.py --worklist       # write the translation worklist
    python3 scripts/sync_korean.py --apply FILE     # splice translations back in
    python3 scripts/sync_korean.py --accept         # mark everything current, no edits

What this is for
----------------
The Korean pages are `*.ko.md` files sitting beside their English originals, so
Hugo serves them at /ko/... as real pages. They are written by hand -- the site
used to run Google's Website Translator over the DOM instead, and the Korean it
produced was poor.

Hand-written translations go stale the moment the English changes, and nothing
in Hugo notices. So this records, for every translatable field, a hash of the
English text as it stood when the Korean was written, in data/ko_manifest.json.
Re-run it after editing English content and it will tell you exactly which
Korean strings the edit invalidated -- not just which files.

Statuses
--------
  MISSING   English exists, no Korean for it yet
  STALE     Korean exists, but the English has changed since it was written
  ORPHAN    Korean exists for a field the English no longer has
  OK        hashes agree

The worklist
------------
`--worklist` writes korean_worklist.json: one entry per MISSING or STALE field,
carrying the English text, the current Korean if there is one, and for a STALE
entry the English it was originally translated from -- so a translator can see
what actually changed rather than redoing the whole string. Fill in the
"korean" values and feed it back with `--apply`.

`--apply` writes scalar strings and page bodies. It refuses arrays and nested
tables (`group` entries, `topics` lists): rewriting those means re-emitting the
TOML, which would throw away the comments in the file. Those are reported with
their exact location so they can be edited by hand, and `--accept` then records
the new hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tomllib

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "data", "ko_manifest.json")
WORKLIST = os.path.join(ROOT, "korean_worklist.json")

# ---------------------------------------------------------------------------
# What gets translated.
#
# Each entry is an English content file and the front-matter keys whose values
# are prose. "@body" means the markdown below the front matter. Dotted paths
# walk into tables and arrays: `group.*.title` is the title of every [[group]].
#
# Deliberately absent: publications, author profiles, news posts and gallery
# captions. Those are ~31k words, mostly names and paper titles that stay in
# English by convention on Korean lab sites.
# ---------------------------------------------------------------------------
PROJECT_FIELDS = ["title", "summary", "projecttext",
                  "projectimagecaption", "projectimagecaptionshort"]

FIELDS: dict[str, list[str]] = {
    "content/home/hero_card.md":      ["subtitle", "cta_text", "alt", "slides.*.alt"],
    "content/home/posts.md":          ["title", "subtitle", "welcomemessage",
                                       "welcome_links.*.name"],
    "content/home/videos.md":         ["title", "subtitle", "cta_text",
                                       "item.*.title", "item.*.description", "@body"],
    "content/home/wordcloud.md":      ["title", "subtitle", "caption", "cta_text"],
    "content/home/contact.md":        ["title", "subtitle"],
    "content/research/subgroups.md":  ["title", "subtitle", "group.*.title",
                                       "group.*.summary", "group.*.description",
                                       "group.*.topics.*", "group.*.links.*.name"],
    "content/development/overview.md": ["title", "subtitle", "group.*.title",
                                        "group.*.summary", "group.*.description",
                                        "group.*.topics.*", "group.*.links.*.name"],
    # Project and software pages carry their prose in front-matter keys, not in
    # a body: `projecttext` is the page, and the two captions sit under the
    # figure. YAML front matter here, TOML above -- parse_front_matter handles
    # both.
    "content/project/materialscreening/index.md": PROJECT_FIELDS,
    "content/project/multiscalemodeling/index.md": PROJECT_FIELDS,
    "content/project/solvationandelectrifiedinterfaces/index.md": PROJECT_FIELDS,
    "content/software/CatINT/index.md":          PROJECT_FIELDS,
    "content/software/CatmapInterface/index.md": PROJECT_FIELDS,
    "content/software/MPBE/index.md":            PROJECT_FIELDS,
    "content/contact/contact.md":     ["title", "subtitle", "@body"],
    "content/people/people.md":       ["title", "subtitle", "@body"],
    "content/alumni/index.md":        ["title", "@body"],
    "content/professor/about.md":     ["title", "subtitle", "@body"],
    # Not the gallery body: it is 81 album headings that are dates and proper
    # nouns -- "6/2026: Visit of Dr. Bergmann and Dr. Turk" -- where the only
    # translatable words are "Visit of". Left in English on both sides on
    # purpose, so it is not reported MISSING for ever.
    "content/gallery/gallery.md":     ["title", "subtitle"],
    "content/my-publications/publications.md": ["title", "subtitle", "@body"],
}

# Both front-matter styles are in use here: the widget files are TOML (+++),
# the project and software pages are YAML (---). Matching only +++ meant the six
# project/software pages were silently skipped and never reported.
FM_TOML = re.compile(r"^\+\+\+\s*?\n(.*?)\n\+\+\+\s*?\n?(.*)$", re.S)
FM_YAML = re.compile(r"^---\s*?\n(.*?)\n---\s*?\n?(.*)$", re.S)


def parse_front_matter(text: str):
    """Return (data, front matter text, body, kind) for either style."""
    m = FM_TOML.match(text)
    if m:
        return tomllib.loads(m.group(1)), m.group(1), m.group(2), "toml"
    m = FM_YAML.match(text)
    if m:
        return yaml.safe_load(m.group(1)) or {}, m.group(1), m.group(2), "yaml"
    return None


def ko_path(en_rel: str) -> str:
    base, ext = os.path.splitext(en_rel)
    return f"{base}.ko{ext}"


def split(path: str):
    """Return (data, front matter text, body, kind) or None."""
    if not os.path.exists(path):
        return None
    return parse_front_matter(open(path, encoding="utf-8").read())


def walk(data, parts: list[str]):
    """Yield (concrete path, value) for a dotted path, expanding * over lists."""
    if not parts:
        if isinstance(data, str):
            yield "", data
        return
    head, rest = parts[0], parts[1:]
    if head == "*":
        if isinstance(data, list):
            for i, item in enumerate(data):
                for sub, val in walk(item, rest):
                    yield (f"{i}.{sub}" if sub else str(i)), val
        return
    if isinstance(data, dict) and head in data:
        for sub, val in walk(data[head], rest):
            yield (f"{head}.{sub}" if sub else head), val


def fields_of(path: str, specs: list[str]) -> dict[str, str]:
    """Every translatable string in one file, keyed by its concrete path."""
    try:
        parts = split(path)
    except (tomllib.TOMLDecodeError, yaml.YAMLError) as e:
        print(f"!! {path}: cannot parse front matter: {e}", file=sys.stderr)
        return {}
    if parts is None:
        return {}
    fm, _fm_text, body, _kind = parts
    out: dict[str, str] = {}
    for spec in specs:
        if spec == "@body":
            if body.strip():
                out["@body"] = body.strip()
            continue
        for concrete, value in walk(fm, spec.split(".")):
            if value.strip():
                out[concrete] = value
    return out


def digest(s: str) -> str:
    return hashlib.sha256(s.strip().encode("utf-8")).hexdigest()[:16]


def survey() -> tuple[dict, list[dict]]:
    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding="utf-8"))
    rows = []
    for en_rel, specs in FIELDS.items():
        en_abs = os.path.join(ROOT, en_rel)
        if not os.path.exists(en_abs):
            rows.append({"file": en_rel, "field": "-", "status": "NO-ENGLISH"})
            continue
        ko_rel = ko_path(en_rel)
        en = fields_of(en_abs, specs)
        ko = fields_of(os.path.join(ROOT, ko_rel), specs)
        recorded = manifest.get(en_rel, {})
        for field, en_text in en.items():
            ko_text = ko.get(field)
            if ko_text is None:
                status = "MISSING"
            elif recorded.get(field) != digest(en_text):
                status = "STALE"
            else:
                status = "OK"
            rows.append({"file": en_rel, "ko_file": ko_rel, "field": field,
                         "status": status, "english": en_text, "korean": ko_text,
                         "was_english_hash": recorded.get(field)})
        for field in ko:
            if field not in en:
                rows.append({"file": en_rel, "ko_file": ko_rel, "field": field,
                             "status": "ORPHAN", "korean": ko.get(field)})
    return manifest, rows


def is_scalar_field(field: str) -> bool:
    """True when --apply can rewrite it: a top-level key, or the body."""
    return field == "@body" or "." not in field


def cmd_report(rows) -> int:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    order = ["MISSING", "STALE", "ORPHAN", "NO-ENGLISH", "OK"]
    for status in order:
        hits = [r for r in rows if r["status"] == status]
        if not hits or status == "OK":
            continue
        print(f"\n{status} ({len(hits)})")
        for r in hits:
            hand = "" if is_scalar_field(r["field"]) else "   [edit by hand]"
            print(f"  {r['file']}  ::  {r['field']}{hand}")
            if status in ("MISSING", "STALE"):
                snippet = " ".join(r["english"].split())[:88]
                print(f"      en: {snippet}{'...' if len(snippet) == 88 else ''}")
    print("\n" + "  ".join(f"{k}={counts.get(k, 0)}" for k in order))
    todo = counts.get("MISSING", 0) + counts.get("STALE", 0)
    if todo:
        print(f"\n{todo} field(s) need attention -- "
              f"`--worklist` writes them to {os.path.relpath(WORKLIST, ROOT)}")
    else:
        print("\nKorean is in step with English.")
    return 1 if todo else 0


def cmd_worklist(rows) -> int:
    todo = [r for r in rows if r["status"] in ("MISSING", "STALE")]
    if not todo:
        print("Nothing to translate.")
        return 0
    out = {
        "_instructions": [
            "Fill in every \"korean\" value, then run:",
            "    python3 scripts/sync_korean.py --apply korean_worklist.json",
            "Entries marked applies_automatically=false must be edited by hand in",
            "the .ko.md file shown; --apply will not touch them, and --accept",
            "records their hashes once you have.",
        ],
        "entries": [
            {
                "file": r["file"], "ko_file": r["ko_file"], "field": r["field"],
                "status": r["status"],
                "applies_automatically": is_scalar_field(r["field"]),
                "english": r["english"],
                "korean": r.get("korean") or "",
            }
            for r in todo
        ],
    }
    with open(WORKLIST, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    auto = sum(1 for e in out["entries"] if e["applies_automatically"])
    print(f"wrote {os.path.relpath(WORKLIST, ROOT)}: {len(todo)} entr(ies), "
          f"{auto} of which --apply can write back")
    return 0


def set_scalar(path: str, field: str, value: str) -> bool:
    """Replace one top-level key, or the body, keeping everything else byte for byte."""
    text = open(path, encoding="utf-8").read()
    parts = parse_front_matter(text)
    if parts is None:
        return False
    _fm, fm_text, body, kind = parts
    fence = "+++" if kind == "toml" else "---"
    if field == "@body":
        new = f"{fence}\n{fm_text}\n{fence}\n{value.rstrip()}\n"
    else:
        # Only a key at column 0, so a same-named key inside a [[table]] is
        # left alone -- those are the ones --apply refuses anyway.
        sep = r"\s*=\s*" if kind == "toml" else r"\s*:\s*"
        pat = re.compile(rf'^({re.escape(field)}{sep})(".*?"|\'\'\'.*?\'\'\'|""".*?""")',
                         re.M | re.S)
        if not pat.search(fm_text):
            return False
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        fm_text = pat.sub(lambda mm: mm.group(1) + f'"{escaped}"', fm_text, count=1)
        new = f"{fence}\n{fm_text}\n{fence}\n{body}"
    open(path, "w", encoding="utf-8").write(new)
    return True


def cmd_apply(manifest, path_to_worklist: str) -> int:
    data = json.load(open(path_to_worklist, encoding="utf-8"))
    wrote = skipped = blank = 0
    for e in data["entries"]:
        if not e["korean"].strip():
            blank += 1
            continue
        if not e["applies_automatically"]:
            skipped += 1
            continue
        ko_abs = os.path.join(ROOT, e["ko_file"])
        if not os.path.exists(ko_abs):
            print(f"!! {e['ko_file']} does not exist yet -- create it first "
                  f"(copy the English file and translate), then re-run")
            skipped += 1
            continue
        if set_scalar(ko_abs, e["field"], e["korean"]):
            wrote += 1
        else:
            print(f"!! {e['ko_file']}: no key `{e['field']}` to replace")
            skipped += 1
    print(f"applied {wrote}, skipped {skipped}, left blank {blank}")
    if wrote:
        print("re-run with --accept once the by-hand edits are in, to record hashes")
    return 0


def cmd_accept(rows) -> int:
    manifest: dict[str, dict[str, str]] = {}
    recorded = 0
    for r in rows:
        if r["status"] in ("NO-ENGLISH", "ORPHAN"):
            continue
        if not r.get("korean"):
            continue                       # nothing translated, nothing to record
        manifest.setdefault(r["file"], {})[r["field"]] = digest(r["english"])
        recorded += 1
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"recorded {recorded} field hash(es) in "
          f"{os.path.relpath(MANIFEST, ROOT)}")
    return 0


def check_menus() -> None:
    """The Korean menu is a separate file; warn if it has drifted structurally."""
    import itertools
    en = os.path.join(ROOT, "config/_default/menus.toml")
    ko = os.path.join(ROOT, "config/_default/menus.ko.toml")
    if not (os.path.exists(en) and os.path.exists(ko)):
        return
    def entries(p):
        txt = open(p, encoding="utf-8").read()
        txt = "\n".join(l for l in txt.splitlines() if not l.lstrip().startswith("#"))
        try:
            d = tomllib.loads(txt)
        except tomllib.TOMLDecodeError:
            return None
        return [(m.get("url"), m.get("weight"), m.get("parent")) for m in d.get("main", [])]
    a, b = entries(en), entries(ko)
    if a is None or b is None:
        return
    if sorted(map(str, a)) != sorted(map(str, b)):
        print("\n!! menus.toml and menus.ko.toml no longer line up "
              "(different urls/weights/parents) -- the Korean nav will differ "
              "from the English one.")
        for x in itertools.filterfalse(lambda v: v in b, a):
            print(f"     only in English: {x}")
        for x in itertools.filterfalse(lambda v: v in a, b):
            print(f"     only in Korean:  {x}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--worklist", action="store_true",
                   help="write korean_worklist.json for everything MISSING or STALE")
    g.add_argument("--apply", metavar="FILE",
                   help="write a filled-in worklist back into the .ko.md files")
    g.add_argument("--accept", action="store_true",
                   help="record current English hashes without editing anything")
    args = ap.parse_args()

    manifest, rows = survey()
    if args.worklist:
        rc = cmd_worklist(rows)
    elif args.apply:
        rc = cmd_apply(manifest, args.apply)
    elif args.accept:
        rc = cmd_accept(rows)
    else:
        rc = cmd_report(rows)
    check_menus()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
