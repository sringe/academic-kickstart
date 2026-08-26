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

## Refresh citation counts and publication↔member links

```bash
python3 scripts/update_pub_meta.py
```

This regenerates `data/pubmeta.json`, which holds two things the site cannot work out
at build time:

- **Google Scholar citation counts.** Scholar has no API, so the script parses the
  profile page. It blocks datacentre traffic — run it from a normal machine, never
  from CI. `--offline` rebuilds only the member links and keeps existing counts;
  a failed fetch leaves the counts on disk untouched rather than zeroing them.
- **Which group members co-authored which paper.** Publication front matter stores
  formatted display names (`<b>S. Y. Kim</b>†`), not usernames, so the links are
  derived from the full names in each publication's `cite.bib` and matched against
  `content/authors/*/`. Ambiguous names are reported as warnings and left unlinked
  rather than guessed at.

Run it after adding a publication or a member page, then commit the JSON. Read any
warnings it prints — they mean a name needs an entry in the `ALIASES` table at the
top of the script.

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
