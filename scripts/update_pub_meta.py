#!/usr/bin/env python3
"""Regenerate data/pubmeta.json: Google Scholar citation counts + publication/member links.

Hugo cannot do either of these at build time (Scholar has no API, and matching
romanised Korean names needs an alias table), so both are precomputed here and
committed. The site build stays offline and deterministic.

    python3 scripts/update_pub_meta.py            # fetch Scholar, rebuild everything
    python3 scripts/update_pub_meta.py --offline   # rebuild member links only,
                                                  # keep the citation counts on disk

Run it from the repo root after adding a publication or a member page.
Scholar blocks datacentre traffic, so this only works from a normal machine --
never from CI.
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import glob
import html
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "pubmeta.json")
SCHOLAR_USER = "uSQ8J50AAAAJ"
SCHOLAR_URL = (
    "https://scholar.google.com/citations"
    f"?user={SCHOLAR_USER}&hl=en&cstart=0&pagesize=100"
)
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Names that no automatic rule can connect. Keep this list short and explain
# every entry -- it is the file a human is expected to review.
ALIASES = {
    # Adith writes his name family-name-last in some papers, first-name-last in
    # others; both forms appear in the .bib files.
    "adith": ["Adith Ramakrishnan Velmurugan", "Ramakrishnan Velmurugan, Adith",
              "Velmurugan, Adith Ramakrishnan", "Adith, Ramakrishnan Velmurugan"],
    # Romanised as "Seo Young" in publications, "Seoyeong" on her profile
    # (cf. her seoyoung0323@ address). Distinct from kim-sung-yeon (김성연).
    "seoyeong-kim": ["Kim, Seo Young"],
    # Appears as both "Sejun" and "Se-Jun".
    "kim-sejun": ["Kim, Sejun", "Kim, Se-Jun"],
}


# --------------------------------------------------------------------------- #
# text normalisation
# --------------------------------------------------------------------------- #
def delatex(s: str) -> str:
    """Strip the LaTeX accent escapes bibtex uses, e.g. N{\\o}rskov, Leb{\\`e}gue."""
    s = re.sub(r"\{\\[a-zA-Z]+\s*\{?([a-zA-Z])\}?\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    return s.replace("{", "").replace("}", "")


def fold(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )


def tokens(s: str) -> list[str]:
    """Lowercase alphabetic tokens, markup and non-latin script removed."""
    s = fold(delatex(html.unescape(s)))
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^A-Za-z]+", " ", s)
    return [t.lower() for t in s.split() if t]


def title_key(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", html.unescape(delatex(s))).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def latin_name(s: str) -> str:
    """Member display names are '김서영<br/> Seoyeong Kim'; keep the latin half."""
    s = re.sub(r"<[^>]+>", " ", html.unescape(s))
    s = re.sub(r"[^\x00-\x7F]+", " ", s)
    return " ".join(s.split())


# --------------------------------------------------------------------------- #
# reading the content tree
# --------------------------------------------------------------------------- #
def front_matter(path: str, field: str) -> str:
    if not os.path.exists(path):
        return ""
    m = re.search(rf"^{field}:\s*(.+?)\s*$", read(path), re.M)
    return m.group(1).strip().strip('"') if m else ""


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def bib_field(raw: str, name: str) -> str:
    """Read one brace- or quote-delimited bibtex field, honouring nesting."""
    m = re.search(rf"{name}\s*=\s*[{{\"]", raw, re.I)
    if not m:
        return ""
    i = m.end() - 1
    if raw[i] == "{":
        depth, j = 0, i
        while j < len(raw):
            if raw[j] == "{":
                depth += 1
            elif raw[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = raw[i + 1 : j]
    else:
        j = raw.index('"', i + 1)
        body = raw[i + 1 : j]
    return " ".join(body.split())


def bib_authors(path: str) -> list[str]:
    field = bib_field(read(path), "author")
    return [a.strip() for a in re.split(r"\s+and\s+", field) if a.strip()]


def load_members() -> dict[str, dict]:
    members = {}
    for d in sorted(glob.glob(os.path.join(ROOT, "content/authors/*/"))):
        slug = os.path.basename(d.rstrip("/"))
        f = os.path.join(d, "_index.md")
        if not os.path.exists(f):
            continue
        name = latin_name(front_matter(f, "name"))
        toks = set(tokens(name))
        alias_toks = [set(tokens(a)) for a in ALIASES.get(slug, [])]
        if not toks and not alias_toks:
            continue  # e.g. jeon-minsu, whose profile has no latin name
        members[slug] = {"name": name, "tokens": toks, "aliases": alias_toks}
    return members


def load_publications() -> list[dict]:
    pubs = []
    for f in sorted(glob.glob(os.path.join(ROOT, "content/publication/*/cite.bib"))):
        d = os.path.dirname(f)
        slug = os.path.basename(d)
        idx = os.path.join(d, "index.md")
        raw_idx = read(idx) if os.path.exists(idx) else ""
        m = re.search(r"^authors:\s*\[(.*?)\]\s*$", raw_idx, re.M | re.S)
        display = [a.strip() for a in m.group(1).split(",") if a.strip()] if m else []
        pubs.append(
            {
                "slug": slug,
                "title": front_matter(idx, "title"),
                "date": front_matter(idx, "date"),
                "doi": front_matter(idx, "doi"),
                "bib": bib_authors(f),
                "bib_title": bib_field(read(f), "title"),
                "display": display,
            }
        )
    return pubs


# --------------------------------------------------------------------------- #
# matching
# --------------------------------------------------------------------------- #
def match_member(bib_name: str, members: dict) -> tuple[str | None, str]:
    """Resolve one bibtex author to a member slug. Refuses to guess."""
    at = tokens(bib_name)
    if len(at) < 2:
        return None, "single-token"
    aset = set(at)

    for slug, m in members.items():
        if any(a == aset for a in m["aliases"]):
            return slug, "alias"

    exact = [s for s, m in members.items() if m["tokens"] == aset]
    if len(exact) == 1:
        return exact[0], "exact"
    if len(exact) > 1:
        return None, "AMBIGUOUS:" + "/".join(sorted(exact))

    # "Sung Yeon" vs "Sungyeon": compare ignoring word boundaries
    flat = "".join(sorted("".join(at)))
    sp = [s for s, m in members.items()
          if "".join(sorted("".join(sorted(m["tokens"])))) == flat and m["tokens"]]
    if len(sp) == 1:
        return sp[0], "spacing"

    # one name carries an extra middle name the other omits
    sub = [
        s for s, m in members.items()
        if m["tokens"] and (m["tokens"] <= aset or aset <= m["tokens"])
        and len(m["tokens"] & aset) >= 2
    ]
    if len(sub) == 1:
        return sub[0], "subset"
    if len(sub) > 1:
        return None, "AMBIGUOUS:" + "/".join(sorted(sub))
    return None, "external"


def match_display(bib_name: str, display: list[str]) -> str | None:
    """Find the index.md author entry (e.g. '<b>R. V. Adith†</b>') for a bib name.

    Publications spell authors as initials + surname, in either name order, so
    match structurally: the entry's surname must be one of the bib name's
    tokens, and each initial must start a different remaining token.
    """
    btoks = tokens(bib_name)
    if not btoks:
        return None
    hits = []
    for entry in display:
        et = tokens(entry)
        if len(et) < 2:
            continue
        # "S. Y. Kim" puts the surname last, "Adith. R. V" puts it first
        for surname, initials in ((et[-1], et[:-1]), (et[0], et[1:])):
            if surname not in btoks:
                continue
            pool = [t for t in btoks if t != surname]
            ok = True
            for ini in (t[0] for t in initials):
                hit = next((t for t in pool if t.startswith(ini)), None)
                if hit is None:
                    ok = False
                    break
                pool.remove(hit)
            if ok:
                hits.append(entry)
                break
    return hits[0] if len(hits) == 1 else None


# --------------------------------------------------------------------------- #
# Google Scholar
# --------------------------------------------------------------------------- #
def fetch_scholar(cache: str | None) -> str:
    if cache and os.path.exists(cache):
        print(f"  using cached profile: {cache}")
        return read(cache)
    import requests

    print(f"  GET {SCHOLAR_URL}")
    r = requests.get(SCHOLAR_URL, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    if cache:
        with open(cache, "w", encoding="utf-8") as fh:
            fh.write(r.text)
    return r.text


def parse_scholar(page: str) -> tuple[list[tuple[str, int]], dict]:
    if re.search(r"(?i)captcha|unusual traffic|not a robot", page):
        raise RuntimeError("Google Scholar served a bot check; try again later")
    rows = []
    for tr in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', page, re.S):
        t = re.search(r'class="gsc_a_at"[^>]*>(.*?)</a>', tr, re.S)
        c = re.search(r'class="gsc_a_ac[^"]*"[^>]*>(.*?)</a>', tr, re.S)
        if not t:
            continue
        cites = re.sub(r"<[^>]+>", "", c.group(1)).strip() if c else ""
        rows.append((title_key(re.sub(r"<[^>]+>", "", t.group(1))),
                     int(cites) if cites.isdigit() else 0))
    if not rows:
        raise RuntimeError("no publication rows found; Scholar markup may have changed")
    std = [int(x.replace(",", ""))
           for x in re.findall(r'class="gsc_rsb_std">([\d,]+)</td>', page)]
    summary = {}
    if len(std) >= 6:
        summary = {"citations_total": std[0], "h_index": std[2], "i10_index": std[4]}
    return rows, summary


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="skip Scholar; keep the counts already in data/pubmeta.json")
    ap.add_argument("--cache", metavar="FILE",
                    help="read/write the raw Scholar HTML here instead of refetching")
    args = ap.parse_args()

    members = load_members()
    pubs = load_publications()
    print(f"members: {len(members)}   publications: {len(pubs)}")

    previous = {}
    if os.path.exists(OUT):
        previous = json.loads(read(OUT))

    # ---- citations ----
    summary, scholar_rows, warn = previous.get("meta", {}), [], []
    if args.offline:
        print("citations: --offline, reusing existing counts")
    else:
        print("citations: fetching Google Scholar profile")
        try:
            rows, summary_new = parse_scholar(fetch_scholar(args.cache))
            scholar_rows = rows
            if summary_new:
                summary = summary_new
            print(f"  parsed {len(rows)} profile entries; {summary}")
        except Exception as exc:                          # noqa: BLE001
            print(f"  !! Scholar fetch failed: {exc}", file=sys.stderr)
            print("  !! keeping existing counts (nothing overwritten)", file=sys.stderr)

    keys = [k for k, _ in scholar_rows]
    prev_pubs = previous.get("publications", {})

    out_pubs, out_members = {}, {}
    for p in pubs:
        slug = p["slug"]

        # citations
        cites, how = None, "none"
        if scholar_rows:
            tk = title_key(p["title"]) or title_key(p["bib_title"])
            if tk in keys:
                cites, how = scholar_rows[keys.index(tk)][1], "title"
            else:
                near = difflib.get_close_matches(tk, keys, n=1, cutoff=0.85)
                if near:
                    cites, how = scholar_rows[keys.index(near[0])][1], "fuzzy"
                else:
                    warn.append(f"{slug}: no Scholar entry matched")
        if cites is None:
            cites = prev_pubs.get(slug, {}).get("citations")
            how = "kept" if cites is not None else "none"

        # members
        entry_members = []
        for bib_name in p["bib"]:
            slug_m, why = match_member(bib_name, members)
            if slug_m is None:
                if why.startswith("AMBIGUOUS"):
                    warn.append(f"{slug}: {bib_name!r} -> {why}")
                continue
            disp = match_display(bib_name, p["display"])
            if disp is None:
                warn.append(
                    f"{slug}: {slug_m} ({bib_name!r}) has no matching entry in "
                    f"index.md authors -- name will not be hyperlinked"
                )
            entry_members.append({"slug": slug_m, "display": disp or "", "bib": bib_name})
            out_members.setdefault(slug_m, []).append(slug)

        rec = {"members": entry_members}
        if cites is not None:
            rec["citations"] = cites
        if how in ("fuzzy",):
            rec["match"] = how
        out_pubs[slug] = rec

    # newest first on the member pages
    order = {p["slug"]: p["date"] for p in pubs}
    for slug in out_members:
        out_members[slug] = sorted(
            set(out_members[slug]), key=lambda s: order.get(s, ""), reverse=True
        )

    doc = {
        "meta": {
            "generated": datetime.date.today().isoformat(),
            "source": "Google Scholar profile " + SCHOLAR_USER,
            "scholar_user": SCHOLAR_USER,
            "script": "scripts/update_pub_meta.py",
            **summary,
        },
        "publications": out_pubs,
        "members": out_members,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")

    linked = sum(len(v["members"]) for v in out_pubs.values())
    cited = sum(1 for v in out_pubs.values() if v.get("citations") is not None)
    print(f"\nwrote {os.path.relpath(OUT, ROOT)}")
    print(f"  member authorships linked : {linked}")
    print(f"  members with publications : {len(out_members)}")
    print(f"  publications with a count : {cited}/{len(pubs)}")
    if warn:
        print(f"\n{len(warn)} warning(s) -- review these:")
        for w in warn:
            print("  -", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
