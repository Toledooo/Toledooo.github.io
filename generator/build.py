"""Orquestra o build: GitHub -> seleção -> textos -> HTML/CSS/JS em dist/."""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from . import art
from .config import Settings
from .content import LANGS, load_yaml, localize, project_text
from .selection import order_repos, select_portfolio_repos

PKG = Path(__file__).resolve().parent


class Source(Protocol):
    def list_repos(self, user: str) -> list[dict]: ...
    def languages(self, user: str, repo: str) -> dict[str, int]: ...
    def preview_image(self, user: str, repo: str, branch: str) -> bytes | None: ...


def build(settings: Settings, source: Source) -> list[str]:
    """Gera o site em settings.out_dir. Devolve avisos (traduções ou descrições faltando)."""
    root = settings.root
    profile = load_yaml(root / "profile.yml")
    overrides = (load_yaml(root / "projects.yml").get("projects") or {})
    strings = load_yaml(root / "strings.yml")
    warnings: list[str] = []

    repos = select_portfolio_repos(source.list_repos(settings.user), settings.user)
    featured = {n for n, cfg in overrides.items() if (cfg or {}).get("featured")}
    repos = order_repos(repos, featured, int(profile.get("max_projects", 6)))

    out = settings.out_dir
    if out.exists():
        shutil.rmtree(out)
    (out / "assets" / "previews").mkdir(parents=True)

    projects = []
    for r in repos:
        langs = source.languages(settings.user, r["name"])
        preview = source.preview_image(settings.user, r["name"], r.get("default_branch") or "main")
        preview_file = None
        if preview:
            preview_file = f"previews/{r['name']}.png"
            (out / "assets" / preview_file).write_bytes(preview)
        projects.append({"repo": r, "langs": langs, "preview": preview_file})

    now = datetime.now(timezone.utc)
    env = Environment(
        loader=FileSystemLoader(PKG / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("index.html")

    agg = art.aggregate_languages([p["langs"] for p in projects])
    for lang in LANGS:
        t = localize(strings, lang, warnings, "strings")
        p = localize(profile, lang, warnings, "profile")
        cards = []
        for item in projects:
            r = item["repo"]
            text = project_text(r, overrides, lang, warnings)
            top_langs = sorted(item["langs"], key=lambda n: -item["langs"][n])[:3]
            cards.append(
                {
                    **text,
                    "name": r["name"],
                    "url": r["html_url"],
                    "homepage": (r.get("homepage") or "").strip(),
                    "topics": [x for x in r.get("topics", []) if x != "portfolio"],
                    "languages": top_langs,
                    "stars": r.get("stargazers_count", 0),
                    "updated": (r.get("pushed_at") or "")[:7],
                    "preview": item["preview"],
                    "art": Markup(art.card_svg(r["name"], item["langs"])) if not item["preview"] else "",
                }
            )
        page_dir = out if lang == "pt" else out / lang
        page_dir.mkdir(exist_ok=True)
        base = settings.base_path
        urls = {"pt": f"{base}/", "en": f"{base}/en/"}
        html = template.render(
            lang=lang,
            t=t,
            p=p,
            projects=cards,
            pipeline=Markup(art.pipeline_svg(p.get("pipeline", []), " → ".join(p.get("pipeline", [])))),
            lang_bars=Markup(
                art.language_bars_svg(agg, t["stack"]["other_langs"], t["stack"]["languages"])
            ),
            base=base,
            self_url=urls[lang],
            alt_url=urls["en" if lang == "pt" else "pt"],
            site_url=settings.site_url,
            contact_url=settings.contact_url,
            generated=now.strftime("%Y-%m-%d"),
        )
        (page_dir / "index.html").write_text(html, encoding="utf-8")

    shutil.copytree(PKG / "static", out / "assets", dirs_exist_ok=True)
    (out / ".nojekyll").write_text("")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {settings.site_url}{settings.base_path}/sitemap.xml\n")
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.w3.org/2000/sitemap/0.9">\n'
        + "".join(
            f"  <url><loc>{settings.site_url}{settings.base_path}{path}</loc></url>\n"
            for path in ("/", "/en/")
        )
        + "</urlset>\n"
    )
    return sorted(set(warnings))
