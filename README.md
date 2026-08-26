# RingeLab site — maintenance notes

Source for **ringelab.com**. Everything below the horizontal rule is the upstream
Academic Kickstart README, kept for reference.

## Preview locally

```bash
./view.sh          # http://localhost:1313, live-reloads on save
```

The Academic theme is pinned to Hugo 0.64 and does **not** build with current Hugo,
so `view.sh` uses a pinned `hugo 0.111.3 extended` binary rather than whatever is on
`PATH`. Override with `HUGO=/path/to/hugo ./view.sh`. Get the binary from
[the Hugo releases page](https://github.com/gohugoio/hugo/releases/tag/v0.111.3);
the default location is `/Users/ringe/software/bin/hugo-0.111.3`.

## Add a publication

Append its BibTeX entry to [`publications.bib`](publications.bib) and run:

```bash
python3 scripts/sync_publications.py
```

That is the whole workflow. The script will

1. create `content/publication/<key>/index.md` and `cite.bib` — the entry key
   becomes the URL slug — filling gaps from Crossref, abbreviating the journal,
   subscripting formulae (`CO2` → `CO<sub>2</sub>`), and writing the author line in
   the site's style with group members in bold;
2. rebuild `data/pubmeta.json`, linking each paper to the group members who
   co-authored it, so their names hyperlink to their profiles and the paper appears
   on each of their pages.

Existing pages are never rewritten, so hand-edits are safe. Useful flags:
`--dry-run` (report only), `--no-fetch` (no network), `--migrate-bib` (rebuild
`publications.bib` from the per-paper `cite.bib` files).

Two things BibTeX cannot express, so add them by hand if you want them: `featured:
true`, and a cover image (`featured.png` in the paper's folder). Equal-contribution
and corresponding-author markers **do** carry through if you write them in the bib
entry, attached to the surname — `author = {Ringe†*, Stefan and ...}`.

Read any warnings the script prints. They mean either a name needs an entry in the
`ALIASES` table or a journal needs one in `JOURNAL_SHORT`, both at the top of the
script. An ambiguous name is always reported and left unlinked rather than guessed
at, so nobody's paper is attributed to the wrong person.

## How citation counts stay current

Counts come from **OpenAlex**, refreshed in the visitor's browser by
[`assets/js/citations.js`](assets/js/citations.js) — one request covers every paper
on the page. **The site never needs rebuilding for the numbers to be current.**

`data/pubmeta.json` also carries a count from the same source, rendered at build
time so that browsers without JavaScript still show something. Because both come
from OpenAlex, the number never jumps when the page loads.

Google Scholar is deliberately not used: it publishes no API, sends no CORS header
(so a browser can never read it), and blocks automated traffic. Its counts run
roughly 15–20% higher than OpenAlex because it also counts preprints and theses.
Matching Scholar would mean a scheduled scrape from a real machine, which cannot
be done from CI and is against Scholar's terms.

## Members and alumni

The Members and Alumni pages are both generated from `content/authors/*/`; neither
contains a hand-written list. A person appears wherever their `user_groups` says:

- Members page — `Professor`, `Postdocs`, `PhD Students`, `Master Students`,
  `Undergrads and Interns`, `Co-supervised Members`, … (see
  [`content/people/people.md`](content/people/people.md))
- Alumni page — `Alumni`, rendered as cards by
  [`layouts/shortcodes/alumni.html`](layouts/shortcodes/alumni.html)

An empty `user_groups` means the person appears on **neither** page. Alumni cards
read the optional `alumni_role`, `alumni_period`, `alumni_position`, `alumni_link`
and `alumni_link_label` fields; whatever is missing is simply left out.

## Publish

```bash
./deploy.sh
```

Builds into `public/` and pushes that to `sringe/sringe.github.io`, which GitHub
Pages serves at ringelab.com. `public/` is a submodule and must be initialised first
(`git submodule update --init --depth 1 public`) or the script fails.

---

<p align="center"><a href="https://sourcethemes.com/academic/" target="_blank" rel="noopener"><img src="https://sourcethemes.com/academic/img/logo_200px.png" alt="Academic logo"></a></p>

# Academic Kickstart: The Template for [Academic Website Builder](https://sourcethemes.com/academic/)

[**Academic**](https://github.com/gcushen/hugo-academic) makes it easy to create a beautiful website for free using Markdown, Jupyter, or RStudio. Customize anything on your site with widgets, themes, and language packs. [Check out the latest demo](https://academic-demo.netlify.com/) of what you'll get in less than 10 minutes, or [view the showcase](https://sourcethemes.com/academic/#expo).

**Academic Kickstart** provides a minimal template to kickstart your new website.

- 👉 [**Get Started**](#install)
- 📚 [View the **documentation**](https://sourcethemes.com/academic/docs/)
- 💬 [Chat with the **Academic community**](https://spectrum.chat/academic) or [**Hugo community**](https://discourse.gohugo.io)
- 🐦 Twitter: [@source_themes](https://twitter.com/source_themes) [@GeorgeCushen](https://twitter.com/GeorgeCushen) [#MadeWithAcademic](https://twitter.com/search?q=%23MadeWithAcademic&src=typd)
- 💡 [Request a **feature** or report a **bug**](https://github.com/gcushen/hugo-academic/issues)
- ⬆️ **Updating?** View the [Update Guide](https://sourcethemes.com/academic/docs/update/) and [Release Notes](https://sourcethemes.com/academic/updates/)
- :heart: **Support development** of Academic:
  - ☕️ [**Donate a coffee**](https://paypal.me/cushen)
  - 💵 [Become a backer on **Patreon**](https://www.patreon.com/cushen)
  - 🖼️ [Decorate your laptop or journal with an Academic **sticker**](https://www.redbubble.com/people/neutreno/works/34387919-academic)
  - 👕 [Wear the **T-shirt**](https://academic.threadless.com/)
  - :woman_technologist: [**Contribute**](https://sourcethemes.com/academic/docs/contribute/)

[![Screenshot](https://raw.githubusercontent.com/gcushen/hugo-academic/master/academic.png)](https://github.com/gcushen/hugo-academic/)

## Install

You can choose from one of the following four methods to install:

* [**one-click install using your web browser (recommended)**](https://sourcethemes.com/academic/docs/install/#install-with-web-browser)
* [install on your computer using **Git** with the Command Prompt/Terminal app](https://sourcethemes.com/academic/docs/install/#install-with-git)
* [install on your computer by downloading the **ZIP files**](https://sourcethemes.com/academic/docs/install/#install-with-zip)
* [install on your computer with **RStudio**](https://sourcethemes.com/academic/docs/install/#install-with-rstudio)

Then [personalize your new site](https://sourcethemes.com/academic/docs/get-started/).

## Ecosystem

* **[Academic Admin](https://github.com/sourcethemes/academic-admin):** An admin tool to import publications from BibTeX or import assets for an offline site
* **[Academic Scripts](https://github.com/sourcethemes/academic-scripts):** Scripts to help migrate content to new versions of Academic

## License

Copyright 2017-present [George Cushen](https://georgecushen.com).

Released under the [MIT](https://github.com/sourcethemes/academic-kickstart/blob/master/LICENSE.md) license.

[![Analytics](https://ga-beacon.appspot.com/UA-78646709-2/academic-kickstart/readme?pixel)](https://github.com/igrigorik/ga-beacon)
