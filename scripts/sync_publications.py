#!/usr/bin/env python3
"""One command to turn publications.bib into a finished publications section.

    python3 scripts/sync_publications.py

For every entry in publications.bib it will
  1. create content/publication/<slug>/{index.md,cite.bib} if the paper has no
     page yet, filling in gaps from Crossref and writing the author line in the
     site's own style (initials + surname, group members in bold);
  2. rebuild data/pubmeta.json, which maps each paper to the group members who
     co-authored it and carries a citation count for browsers without
     JavaScript. Live counts come from OpenAlex in the browser --
     see assets/js/citations.js.

Existing pages are never rewritten, so hand-edits are safe.

Options
    --dry-run       report what would change, write nothing
    --no-fetch      skip the network; keep the citation counts already on disk
    --migrate-bib   rebuild publications.bib FROM the per-paper cite.bib files.
                    Run this once: 22 of the 50 papers were never added to
                    publications.bib, so it is not yet the source of truth.
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
MASTER_BIB = os.path.join(ROOT, "publications.bib")
PUB_DIR = os.path.join(ROOT, "content", "publication")
AUTHOR_DIR = os.path.join(ROOT, "content", "authors")
OUT = os.path.join(ROOT, "data", "pubmeta.json")

# Contact address for OpenAlex's "polite pool". Only ever sent from this script,
# never from the browser, so it does not end up published on the site.
OPENALEX_MAILTO = "stefan.ringe.tum@gmail.com"

# Bibtex names that no automatic rule can connect to a profile. Every entry
# needs a reason; this is the table a human is expected to review.
ALIASES = {
    # Writes his name family-name-last in some papers, first-name-last in others.
    "adith": ["Adith Ramakrishnan Velmurugan", "Ramakrishnan Velmurugan, Adith",
              "Velmurugan, Adith Ramakrishnan", "Adith, Ramakrishnan Velmurugan"],
    # Romanised "Seo Young" in publications, "Seoyeong" on her profile
    # (cf. her seoyoung0323@ address). A different person from kim-sung-yeon (김성연).
    "seoyeong-kim": ["Kim, Seo Young"],
    # Appears as both "Sejun" and "Se-Jun".
    "kim-sejun": ["Kim, Sejun", "Kim, Se-Jun"],
}

# How a member prefers to be credited, when it differs from "initials + surname".
DISPLAY_OVERRIDES = {
    "adith": "R. V. Adith",
}

# Journal abbreviations, read off the 50 papers that already have pages.
# An unknown journal falls through to its full name and prints a warning.
JOURNAL_SHORT = {
    "acs catalysis": "ACS Catal.",
    "acs energy letters": "ACS Energy Lett.",
    "advanced energy materials": "Adv Energy Mater",
    "advanced materials": "Adv. Mater.",
    "angewandte chemie international edition": "Angew Chem Int Ed Engl",
    "current opinion in electrochemistry": "Curr Opin Electrochem",
    "energy & environmental materials": "Energy Environ. Mater.",
    "energy & environmental science": "Energy Environ. Sci.",
    "journal of materials chemistry a": "J. Mater. Chem. A.",
    "journal of the american chemical society": "J. Am. Chem. Soc.",
    "nano letters": "Nano Lett.",
    "nat catal": "Nat. Catal.",
    "nature catalysis": "Nat. Catal.",
    "nature communications": "Nat. Commun.",
    "small science": "Small Sci.",
    "the journal of chemical physics": "J. Chem. Phys.",
    "the journal of physical chemistry letters": "J. Phys. Chem. Lett.",
}

# Bibtex titles are plain text, but the site writes formulae with <sub> tags.
# Only these exact tokens are rewritten -- a general "digit after a letter" rule
# would mangle things like "2D materials", "II-VI" and "(CdSe)13".
FORMULAE = ["CO2RR", "CO2", "H2O2", "H2O", "H2", "O2", "N2", "CH4", "CH3OH",
            "C2H4", "C2H6", "NH3", "N2O", "NO2", "NO3", "HCO3", "CO3",
            "SnO2", "CeO2", "TiO2", "MoS2", "PtP2", "SiO2", "Al2O3", "Cu2O"]


def subscript_formulae(title: str) -> str:
    """CO2 -> CO<sub>2</sub>, for the handful of formulae this group writes."""
    for f in FORMULAE:
        sub = re.sub(r"(\d+)", r"<sub>\1</sub>", f)
        title = re.sub(rf"(?<![A-Za-z0-9<]){re.escape(f)}(?![A-Za-z0-9])", sub, title)
    return title


MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
MARKERS = "†*‡§"
WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# --------------------------------------------------------------------------- #
# text helpers
# --------------------------------------------------------------------------- #
def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def delatex(s: str) -> str:
    """Strip the accent escapes bibtex uses: N{\\o}rskov, Leb{\\`e}gue."""
    s = re.sub(r"\{\\[a-zA-Z]+\s*\{?([a-zA-Z])\}?\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    return s.replace("{", "").replace("}", "")


def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def tokens(s: str) -> list[str]:
    s = fold(delatex(html.unescape(s)))
    s = re.sub(r"<[^>]+>", " ", s)
    return [t.lower() for t in re.sub(r"[^A-Za-z]+", " ", s).split() if t]


def title_key(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", html.unescape(delatex(s))).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def norm_doi(s: str) -> str:
    return re.sub(r"^(https?://)?(dx\.)?doi\.org/", "",
                  (s or "").strip().strip("{}\"")).lower()


def latin_name(s: str) -> str:
    """Profile names read '김서영<br/> Seoyeong Kim'; keep the latin half."""
    s = re.sub(r"<[^>]+>", " ", html.unescape(s))
    return " ".join(re.sub(r"[^\x00-\x7F]+", " ", s).split())


# --------------------------------------------------------------------------- #
# bibtex
# --------------------------------------------------------------------------- #
def brace_match(s: str, i: int) -> int:
    """Index of the '}' closing the '{' at position i."""
    depth = 0
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(s) - 1


def parse_bib(raw: str) -> list[dict]:
    """Split a .bib file into entries. Returns dicts of lowercased field names
    plus '_type' and '_key'."""
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{", raw):
        kind = m.group(1).lower()
        if kind in ("comment", "preamble", "string"):
            continue
        open_brace = m.end() - 1
        body = raw[open_brace + 1 : brace_match(raw, open_brace)]
        key, _, rest = body.partition(",")
        entry = {"_type": kind, "_key": key.strip()}
        # walk the field list, honouring nested braces and quoted values
        i = 0
        while i < len(rest):
            fm = re.compile(r"([A-Za-z_-]+)\s*=\s*").search(rest, i)
            if not fm:
                break
            name, j = fm.group(1).lower(), fm.end()
            while j < len(rest) and rest[j] in " \t\r\n":
                j += 1
            if j >= len(rest):
                break
            if rest[j] == "{":
                end = brace_match(rest, j)
                val, i = rest[j + 1 : end], end + 1
            elif rest[j] == '"':
                end = j + 1
                while end < len(rest):
                    if rest[end] == '"' and rest[end - 1] != "\\":
                        break
                    end += 1
                val, i = rest[j + 1 : end], end + 1
            else:
                end = j
                while end < len(rest) and rest[end] not in ",\n":
                    end += 1
                val, i = rest[j:end], end
            entry[name] = " ".join(val.split())
        entries.append(entry)
    return entries


def split_authors(field: str) -> list[str]:
    return [a.strip() for a in re.split(r"\s+and\s+", " ".join(field.split()))
            if a.strip()]


def split_name(raw: str) -> tuple[str, list[str], str]:
    """-> (surname, [given names], markers). Handles 'Last, First' and 'First Last',
    and the †/* markers this group attaches to the surname."""
    name = delatex(raw).strip()
    marks = "".join(sorted({c for c in name if c in MARKERS}, key=name.index))
    name = "".join(c for c in name if c not in MARKERS).strip(" ,")
    if "," in name:
        last, _, first = name.partition(",")
        surname, given = last.strip(), first.split()
    else:
        parts = name.split()
        surname, given = (parts[-1] if parts else ""), parts[:-1]
    return surname, given, marks


def display_name(raw: str, member: str | None) -> str:
    """Render one author the way the site writes them: 'H. G. Abbas', bold if
    they are in the group."""
    surname, given, marks = split_name(raw)
    if member and member in DISPLAY_OVERRIDES:
        text = DISPLAY_OVERRIDES[member] + marks
    else:
        initials = " ".join(f"{g[0]}." for g in given if g)
        text = f"{initials} {surname}".strip() + marks
    return f"<b>{text}</b>" if member else text


# --------------------------------------------------------------------------- #
# members
# --------------------------------------------------------------------------- #
def load_members() -> dict[str, dict]:
    members = {}
    for d in sorted(glob.glob(os.path.join(AUTHOR_DIR, "*/"))):
        slug = os.path.basename(d.rstrip("/"))
        f = os.path.join(d, "_index.md")
        if not os.path.exists(f):
            continue
        m = re.search(r"^name:\s*(.+?)\s*$", read(f), re.M)
        name = latin_name(m.group(1)) if m else ""
        toks = set(tokens(name))
        aliases = [set(tokens(a)) for a in ALIASES.get(slug, [])]
        if not toks and not aliases:
            continue          # e.g. jeon-minsu, whose profile has no latin name
        members[slug] = {"tokens": toks, "aliases": aliases}
    return members


def match_member(bib_name: str, members: dict) -> tuple[str | None, str]:
    """Resolve a bibtex author to a profile slug. Refuses to guess: an ambiguous
    name is reported and left unlinked rather than attributed to the wrong person."""
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

    flat = "".join(sorted("".join(at)))          # "Sung Yeon" == "Sungyeon"
    sp = [s for s, m in members.items()
          if m["tokens"] and "".join(sorted("".join(sorted(m["tokens"])))) == flat]
    if len(sp) == 1:
        return sp[0], "spacing"

    sub = [s for s, m in members.items()          # one side omits a middle name
           if m["tokens"] and (m["tokens"] <= aset or aset <= m["tokens"])
           and len(m["tokens"] & aset) >= 2]
    if len(sub) == 1:
        return sub[0], "subset"
    if len(sub) > 1:
        return None, "AMBIGUOUS:" + "/".join(sorted(sub))
    return None, "external"


def match_display(bib_name: str, display: list[str]) -> str | None:
    """Find which index.md author entry ('<b>R. V. Adith†</b>') is this bib name.
    Papers use initials + surname in either order, so match structurally."""
    btoks = tokens(bib_name)
    if not btoks:
        return None
    hits = []
    for entry in display:
        et = tokens(entry)
        if len(et) < 2:
            continue
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
# existing content
# --------------------------------------------------------------------------- #
def load_pages() -> list[dict]:
    pages = []
    for idx in sorted(glob.glob(os.path.join(PUB_DIR, "*", "index.md"))):
        d = os.path.dirname(idx)
        raw = read(idx)
        def f(name, default=""):
            m = re.search(rf"^{name}:\s*(.*?)\s*$", raw, re.M)
            return m.group(1).strip().strip('"') if m else default
        am = re.search(r"^authors:\s*\[(.*?)\]\s*$", raw, re.M | re.S)
        bib = os.path.join(d, "cite.bib")
        pages.append({
            "slug": os.path.basename(d),
            "dir": d,
            "title": f("title"),
            "date": f("date"),
            "doi": norm_doi(f("doi")),
            "display": [a.strip() for a in am.group(1).split(",") if a.strip()] if am else [],
            "bib_authors": (split_authors(parse_bib(read(bib))[0].get("author", ""))
                            if os.path.exists(bib) and parse_bib(read(bib)) else []),
            "has_bib": os.path.exists(bib),
        })
    return pages


# --------------------------------------------------------------------------- #
# network
# --------------------------------------------------------------------------- #
def crossref(doi: str) -> dict:
    import requests
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}",
                         headers={"User-Agent": f"RingeLab-site ({OPENALEX_MAILTO})"},
                         timeout=30)
        if r.ok:
            return r.json()["message"]
    except Exception as exc:                                   # noqa: BLE001
        warn(f"Crossref lookup failed for {doi}: {exc}")
    return {}


SCHOLAR_USER = "uSQ8J50AAAAJ"
SCHOLAR_URL = (f"https://scholar.google.com/citations?user={SCHOLAR_USER}"
               "&hl=en&cstart=0&pagesize=100")


def scholar_cites_urls() -> dict[str, str]:
    """Map normalised title -> Google Scholar "cited by" listing URL.

    Only the *links* are taken from Scholar; the counts come from OpenAlex. Each
    link embeds the paper's Scholar cluster id(s), which are stable, so this
    needs re-running only when a paper is added -- which is why it sits behind
    --scholar rather than running every time. Scholar publishes no API and
    blocks datacentre traffic, so this works from a personal machine only.
    """
    import requests
    ua = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
    try:
        r = requests.get(SCHOLAR_URL, headers={"User-Agent": ua}, timeout=45)
        r.raise_for_status()
    except Exception as exc:                                   # noqa: BLE001
        warn(f"Google Scholar fetch failed: {exc}; keeping the stored links")
        return {}
    page = r.text
    if re.search(r"(?i)captcha|unusual traffic|not a robot", page):
        warn("Google Scholar served a bot check; keeping the stored links")
        return {}
    out = {}
    for tr in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', page, re.S):
        t = re.search(r'class="gsc_a_at"[^>]*>(.*?)</a>', tr, re.S)
        # The href is HTML-escaped ("&amp;cites="), so do not anchor on "?" or "&".
        a = re.search(r'href="([^"]*cites=[^"]*)"', tr)
        if t and a:
            out[title_key(re.sub(r"<[^>]+>", "", t.group(1)))] = html.unescape(a.group(1))
    if not out:
        warn("no Scholar cited-by links found; the profile markup may have changed")
    return out


def openalex_counts(dois: list[str]) -> dict[str, int]:
    """One request per 50 DOIs. Same source the browser uses, so the fallback
    number and the live number never disagree."""
    import requests
    out: dict[str, int] = {}
    for i in range(0, len(dois), 50):
        chunk = [d for d in dois[i : i + 50] if d]
        if not chunk:
            continue
        try:
            r = requests.get(
                "https://api.openalex.org/works",
                params={"filter": "doi:" + "|".join(chunk),
                        "select": "doi,cited_by_count",
                        "per-page": 50,
                        "mailto": OPENALEX_MAILTO},
                timeout=45)
            r.raise_for_status()
            for w in r.json().get("results", []):
                out[norm_doi(w.get("doi") or "")] = w.get("cited_by_count", 0)
        except Exception as exc:                               # noqa: BLE001
            warn(f"OpenAlex request failed: {exc}")
    return out


# --------------------------------------------------------------------------- #
# generating a page
# --------------------------------------------------------------------------- #
def slugify(entry: dict, taken: set[str]) -> str:
    if entry.get("slug"):
        return entry["slug"]
    authors = split_authors(entry.get("author", ""))
    surname = split_name(authors[0])[0] if authors else (entry.get("_key") or "paper")
    year = re.sub(r"\D", "", entry.get("year", ""))[:4] or "0000"
    base = re.sub(r"[^a-z0-9]+", "-",
                  fold(delatex(surname)).lower()).strip("-") + f"-{year}"
    slug, n = base, 1
    while slug in taken:
        n += 1
        slug = f"{base}-{chr(ord('a') + n - 2)}"
    return slug


def entry_date(entry: dict, cr: dict) -> str:
    y = re.sub(r"\D", "", entry.get("year", ""))[:4]
    mo = entry.get("month", "").strip().lower()[:3]
    month = MONTHS.get(mo) or (int(re.sub(r"\D", "", entry.get("month", "")) or 0)
                               if re.search(r"\d", entry.get("month", "")) else 0)
    day = 1
    parts = (cr.get("published") or {}).get("date-parts") or []
    if parts and parts[0]:
        p = parts[0] + [1, 1]
        y, month, day = y or str(p[0]), month or p[1], p[2]
    if not y:
        return ""
    return f"{y}-{int(month or 1):02d}-{int(day or 1):02d}"


def journal_short(name: str) -> str:
    key = " ".join(delatex(name).split()).lower()
    if key in JOURNAL_SHORT:
        return JOURNAL_SHORT[key]
    short = " ".join(delatex(name).split())
    if short:
        warn(f"no abbreviation known for journal {short!r} -- "
             f"add it to JOURNAL_SHORT in {os.path.basename(__file__)}")
    return short


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_index(entry: dict, cr: dict, members: dict) -> str:
    authors = split_authors(entry.get("author", ""))
    shown = []
    for a in authors:
        slug, _ = match_member(a, members)
        shown.append(display_name(a, slug))
    date = entry_date(entry, cr)
    today = datetime.date.today().isoformat()
    abstract = delatex(entry.get("abstract", "")) or re.sub(
        r"<[^>]+>", "", cr.get("abstract", "") or "").replace("\n", " ").strip()
    journal = journal_short(entry.get("journal") or
                            ((cr.get("container-title") or [""])[0]))
    pages = entry.get("pages") or cr.get("page") or ""
    publication = yaml_str(f"*{journal}*") if journal else '""'
    lines = [
        "---",
        f"title: {yaml_str(subscript_formulae(delatex(entry.get('title', ''))))}",
        f"date: {date}",
        f"publishDate: {min(date, today) if date else today}",
        "authors: [" + ", ".join(shown) + "]",
        'publication_types: ["2"]',
        f"abstract: {yaml_str(abstract)}",
        "featured: false",
        f"publication: {publication}",
        f"doi: {yaml_str(norm_doi(entry.get('doi', '')))}",
        f"volume: {yaml_str(entry.get('volume') or str(cr.get('volume') or ''))}",
        f"pages: {yaml_str(pages)}",
        'cover: ""',
        'highlight: ""',
        'hot: ""',
        "---",
        "",
        "",
    ]
    return "\n".join(lines)


def render_bib(entry: dict, cr: dict) -> str:
    doi = norm_doi(entry.get("doi", ""))
    keep = ["author", "title", "journal", "volume", "number", "pages",
            "year", "month", "issn", "publisher"]
    vals = dict(entry)
    if cr:
        vals.setdefault("volume", str(cr.get("volume") or ""))
        vals.setdefault("number", str(cr.get("issue") or ""))
        vals.setdefault("pages", cr.get("page") or "")
        vals.setdefault("journal", (cr.get("container-title") or [""])[0])
        issn = cr.get("ISSN") or []
        vals.setdefault("issn", issn[0] if issn else "")
    out = [f"@{entry.get('_type', 'article')}{{{doi or entry.get('_key', '')},"]
    for k in keep:
        v = (vals.get(k) or "").strip()
        if v:
            out.append(f"    {k} = {{{v}}},")
    if doi:
        out.append(f"    doi = {{{doi}}},")
        out.append(f"    url = {{https://doi.org/{doi}}},")
    out.append("}")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- #
def migrate_bib(pages: list[dict], dry: bool) -> None:
    """Rebuild publications.bib from the per-paper cite.bib files."""
    chunks, seen = [], set()
    for p in sorted(pages, key=lambda x: x["date"], reverse=True):
        f = os.path.join(p["dir"], "cite.bib")
        if not os.path.exists(f):
            warn(f"{p['slug']}: no cite.bib, cannot include in publications.bib")
            continue
        entries = parse_bib(read(f))
        if not entries:
            warn(f"{p['slug']}: cite.bib could not be parsed")
            continue
        e = entries[0]
        bib_doi = norm_doi(e.get("doi", ""))
        if bib_doi and p["doi"] and bib_doi != p["doi"]:
            warn(f"{p['slug']}: cite.bib DOI {bib_doi!r} != index.md DOI "
                 f"{p['doi']!r} -- check this paper")
        key = p["slug"]
        if key in seen:
            continue
        seen.add(key)
        body = read(f).strip()
        # re-key each entry to its content folder, so bib entry <-> page is obvious
        body = re.sub(r"^@(\w+)\s*\{[^,]*,", rf"@\1{{{key},", body, count=1)
        # 11 of the cite.bib files carry no DOI; take it from index.md so that
        # publications.bib alone is enough to identify every paper.
        if not bib_doi and p["doi"]:
            body = body[: body.rfind("}")].rstrip().rstrip(",") + (
                f",\n    doi = {{{p['doi']}}},"
                f"\n    url = {{https://doi.org/{p['doi']}}},\n}}")
        chunks.append(f"{body}\n")
    header = (
        "% RingeLab publication list -- the source of truth for the site.\n"
        "% Add a new paper by appending its bibtex entry here, then run:\n"
        "%     python3 scripts/sync_publications.py\n"
        "% The entry key becomes the URL slug (content/publication/<key>/).\n"
        f"% Regenerated from the per-paper cite.bib files on "
        f"{datetime.date.today().isoformat()}.\n\n")
    text = header + "\n".join(chunks)
    print(f"  publications.bib: {len(chunks)} entries "
          f"({len(parse_bib(read(MASTER_BIB))) if os.path.exists(MASTER_BIB) else 0} before)")
    if dry:
        print("  (dry run, not written)")
        return
    with open(MASTER_BIB, "w", encoding="utf-8") as fh:
        fh.write(text)


def create_pages(entries: list[dict], pages: list[dict], members: dict,
                 dry: bool, fetch: bool) -> list[dict]:
    """Create a content bundle for every bib entry that has no page yet."""
    by_doi = {p["doi"]: p for p in pages if p["doi"]}
    by_title = {title_key(p["title"]): p for p in pages}
    taken = {p["slug"] for p in pages}
    created = []
    for e in entries:
        doi = norm_doi(e.get("doi", ""))
        tkey = title_key(e.get("title", ""))
        if (doi and doi in by_doi) or tkey in by_title:
            continue
        near = difflib.get_close_matches(tkey, list(by_title), n=1, cutoff=0.9)
        if near:
            print(f"  ~ {e.get('_key')}: title close to existing "
                  f"{by_title[near[0]]['slug']}, skipping")
            continue
        slug = slugify(e, taken)
        taken.add(slug)
        cr = crossref(doi) if (doi and fetch) else {}
        d = os.path.join(PUB_DIR, slug)
        print(f"  + {slug}  ({e.get('title','')[:56]})")
        if dry:
            created.append({"slug": slug})
            continue
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as fh:
            fh.write(render_index(e, cr, members))
        with open(os.path.join(d, "cite.bib"), "w", encoding="utf-8") as fh:
            fh.write(render_bib(e, cr))
        created.append({"slug": slug})
    if not created:
        print("  (every bib entry already has a page)")
    return created


def build_pubmeta(pages: list[dict], members: dict, dry: bool, fetch: bool,
                  scholar: bool) -> None:
    previous = json.loads(read(OUT)) if os.path.exists(OUT) else {}
    prev_pubs = previous.get("publications", {})

    counts = openalex_counts([p["doi"] for p in pages]) if fetch else {}
    if fetch and not counts:
        warn("no citation counts fetched; keeping the values already on disk")
    cites_urls = scholar_cites_urls() if scholar else {}

    out_pubs, out_members = {}, {}
    for p in pages:
        if not p["has_bib"]:
            warn(f"{p['slug']}: no cite.bib, so its members cannot be linked")
        entry_members = []
        for bib_name in p["bib_authors"]:
            slug, why = match_member(bib_name, members)
            if slug is None:
                if why.startswith("AMBIGUOUS"):
                    warn(f"{p['slug']}: {bib_name!r} -> {why}")
                continue
            disp = match_display(bib_name, p["display"])
            if disp is None:
                warn(f"{p['slug']}: {slug} ({bib_name!r}) matches no entry in the "
                     f"index.md author line, so the name is not hyperlinked")
            entry_members.append({"slug": slug, "display": disp or "", "bib": bib_name})
            out_members.setdefault(slug, []).append(p["slug"])

        rec: dict = {"members": entry_members, "doi": p["doi"]}
        c = counts.get(p["doi"], prev_pubs.get(p["slug"], {}).get("citations"))
        if c is not None:
            rec["citations"] = c
        # Link to Scholar's cited-by listing. Kept from the previous run unless
        # --scholar refreshed it, so the normal path needs no Scholar request.
        url = cites_urls.get(title_key(p["title"]))
        if not url and cites_urls:
            near = difflib.get_close_matches(title_key(p["title"]),
                                             list(cites_urls), n=1, cutoff=0.85)
            url = cites_urls[near[0]] if near else None
        url = url or prev_pubs.get(p["slug"], {}).get("cites_url")
        if url:
            rec["cites_url"] = url
        out_pubs[p["slug"]] = rec

    order = {p["slug"]: p["date"] for p in pages}
    for slug in out_members:
        # Newest first, then by slug. Sorting on the date alone leaves papers
        # that share a date in set order, which changes between runs and would
        # show up as a spurious diff every time this is regenerated.
        by_slug = sorted(set(out_members[slug]))
        out_members[slug] = sorted(by_slug, key=lambda s: order.get(s, ""),
                                   reverse=True)

    doc = {
        "meta": {
            "generated": datetime.date.today().isoformat(),
            "citations_source": "OpenAlex (cited_by_count), refreshed live in the "
                                "browser by assets/js/citations.js",
            "script": "scripts/sync_publications.py",
        },
        "publications": out_pubs,
        "members": out_members,
    }
    linked = sum(len(v["members"]) for v in out_pubs.values())
    cited = sum(1 for v in out_pubs.values() if v.get("citations") is not None)
    print(f"  member authorships linked : {linked}")
    print(f"  members with publications : {len(out_members)}")
    linked_urls = sum(1 for v in out_pubs.values() if v.get("cites_url"))
    print(f"  publications with a count : {cited}/{len(pages)}")
    print(f"  Scholar cited-by links    : {linked_urls}/{len(pages)}")
    if dry:
        print("  (dry run, data/pubmeta.json not written)")
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--migrate-bib", action="store_true")
    ap.add_argument("--scholar", action="store_true",
                    help="also refresh the Google Scholar cited-by links "
                         "(run from a personal machine, not CI)")
    args = ap.parse_args()
    fetch = not args.no_fetch

    members = load_members()
    pages = load_pages()
    print(f"members: {len(members)}   pages: {len(pages)}")

    if args.migrate_bib:
        print("\nrebuilding publications.bib from the per-paper cite.bib files")
        migrate_bib(pages, args.dry_run)
        if not args.dry_run:
            pages = load_pages()

    if not os.path.exists(MASTER_BIB):
        print(f"!! {MASTER_BIB} not found", file=sys.stderr)
        return 1
    entries = parse_bib(read(MASTER_BIB))
    print(f"\npublications.bib: {len(entries)} entries")
    create_pages(entries, pages, members, args.dry_run, fetch)
    if not args.dry_run:
        pages = load_pages()

    print("\nrebuilding data/pubmeta.json")
    build_pubmeta(pages, members, args.dry_run, fetch, args.scholar)

    if WARNINGS:
        print(f"\n{len(WARNINGS)} warning(s):")
        for w in WARNINGS:
            print("  -", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
