import re
from dataclasses import replace
from pathlib import Path

import pytest

from generator.build import build
from generator.config import ROOT, Settings
from generator.fixtures import FixtureSource
from generator.github import GitHubError

FIXTURE = Path(__file__).parent / "fixtures" / "repos.json"


@pytest.fixture
def site(tmp_path):
    settings = replace(Settings.from_env(), out_dir=tmp_path / "dist", contact_url="")
    warnings = build(settings, FixtureSource(FIXTURE))
    return settings.out_dir, warnings


def test_builds_both_languages_and_assets(site):
    out, _ = site
    for f in ("index.html", "en/index.html", "assets/style.css", "assets/main.js", ".nojekyll", "sitemap.xml"):
        assert (out / f).exists(), f


def test_pages_have_language_and_alternates(site):
    out, _ = site
    pt = (out / "index.html").read_text()
    en = (out / "en/index.html").read_text()
    assert '<html lang="pt-BR">' in pt and '<html lang="en">' in en
    assert 'hreflang="en"' in pt and 'hreflang="pt-BR"' in en
    assert 'href="/en/"' in pt and 'href="/"' in en


def test_only_selected_projects_are_rendered(site):
    out, _ = site
    html = (out / "index.html").read_text()
    assert "api-exemplo" in html and "rpa-exemplo" in html
    for hidden in ("sem-topic", "um-fork", "arquivado", "excluido"):
        assert hidden not in html


def test_profile_text_rendered_in_each_language(site):
    out, _ = site
    assert "Desenvolvedor Python" in (out / "index.html").read_text()
    assert "Python Developer" in (out / "en/index.html").read_text()


def test_no_leftover_template_values(site):
    out, _ = site
    for page in ("index.html", "en/index.html"):
        html = (out / page).read_text()
        assert "None" not in html and "{{" not in html and "{%" not in html


def test_warnings_report_missing_project_texts(site):
    _, warnings = site
    assert any("api-exemplo" in w and "projects.yml" in w for w in warnings)
    assert any("rpa-exemplo" in w and "sem descrição" in w for w in warnings)


def test_contact_button_only_when_url_set(tmp_path):
    base = replace(Settings.from_env(), out_dir=tmp_path / "a", contact_url="")
    build(base, FixtureSource(FIXTURE))
    assert "Abrir chamado" not in (base.out_dir / "index.html").read_text()

    with_url = replace(base, out_dir=tmp_path / "b", contact_url="https://chamados.exemplo.dev")
    build(with_url, FixtureSource(FIXTURE))
    html = (with_url.out_dir / "index.html").read_text()
    assert 'href="https://chamados.exemplo.dev"' in html and "Abrir chamado" in html


def test_base_path_prefixes_asset_and_language_links(tmp_path):
    s = replace(Settings.from_env(), out_dir=tmp_path / "d", base_path="/portfolio")
    build(s, FixtureSource(FIXTURE))
    html = (s.out_dir / "index.html").read_text()
    assert 'href="/portfolio/assets/style.css"' in html and 'href="/portfolio/en/"' in html


def test_markup_in_repo_data_is_escaped(tmp_path):
    class Evil(FixtureSource):
        def list_repos(self, user):
            r = dict(super().list_repos(user)[0], description="<script>alert(1)</script>")
            return [r]

    s = replace(Settings.from_env(), out_dir=tmp_path / "d")
    build(s, Evil(FIXTURE))
    html = (s.out_dir / "index.html").read_text()
    assert "<script>alert(1)</script>" not in html
    assert not re.search(r"<script>alert", html)


def test_api_failure_propagates_so_the_build_fails(tmp_path):
    class Broken(FixtureSource):
        def list_repos(self, user):
            raise GitHubError("boom")

    s = replace(Settings.from_env(), out_dir=tmp_path / "d")
    with pytest.raises(GitHubError):
        build(s, Broken(FIXTURE))
