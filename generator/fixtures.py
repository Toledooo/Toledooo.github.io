"""Fonte de dados offline, só para desenvolvimento e testes (nada disso vai ao site real)."""
from __future__ import annotations

import json
from pathlib import Path


class FixtureSource:
    def __init__(self, path: Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self._repos = data["repos"]
        self._langs = data.get("languages", {})

    def list_repos(self, user: str) -> list[dict]:
        return self._repos

    def languages(self, user: str, repo: str) -> dict[str, int]:
        return self._langs.get(repo, {})

    def preview_image(self, user: str, repo: str, branch: str) -> bytes | None:
        return None
