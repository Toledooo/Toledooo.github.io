"""Quais repositórios entram no portfólio, e em que ordem. Funções puras."""
from __future__ import annotations

PORTFOLIO_TOPIC = "portfolio"
EXCLUDE_TOPIC = "no-portfolio"


def select_portfolio_repos(repos: list[dict], user: str) -> list[dict]:
    """Públicos com o topic `portfolio`, sem forks, arquivados ou `no-portfolio`."""
    skip_names = {user.lower(), f"{user.lower()}.github.io"}  # repo do perfil e do próprio site
    selected = []
    for r in repos:
        topics = set(r.get("topics") or [])
        if PORTFOLIO_TOPIC not in topics or EXCLUDE_TOPIC in topics:
            continue
        if r.get("fork") or r.get("archived") or r.get("private"):
            continue
        if r["name"].lower() in skip_names:
            continue
        selected.append(r)
    return selected


def order_repos(repos: list[dict], featured: set[str], limit: int) -> list[dict]:
    """Os `featured` primeiro; dentro de cada grupo, o push mais recente primeiro."""
    ranked = sorted(
        repos,
        key=lambda r: (r["name"] not in featured, _neg(r.get("pushed_at") or "")),
    )
    return ranked[:limit]


def _neg(iso: str) -> tuple:
    # Datas ISO ordenam como texto; invertemos cada caractere para ordem decrescente.
    return tuple(-ord(c) for c in iso)
