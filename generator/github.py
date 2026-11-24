"""Acesso à API pública do GitHub. Qualquer falha levanta GitHubError."""
from __future__ import annotations

import requests

API = "https://api.github.com"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_PREVIEW_BYTES = 3 * 1024 * 1024
PREVIEW_PATH = "docs/preview.png"


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None = None, session: requests.Session | None = None):
        self._s = session or requests.Session()
        self._s.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "portfolio-generator",
            }
        )
        if token:
            self._s.headers["Authorization"] = f"Bearer {token}"

    def _get(self, path: str, **params):
        try:
            r = self._s.get(f"{API}{path}", params=params or None, timeout=20)
        except requests.RequestException as e:
            raise GitHubError(f"GET {path} falhou: {e}") from e
        if r.status_code == 404:
            return None
        if not r.ok:
            raise GitHubError(f"GET {path} -> {r.status_code}: {r.text[:200]}")
        return r.json()

    def list_repos(self, user: str) -> list[dict]:
        repos: list[dict] = []
        page = 1
        while True:
            batch = self._get(
                f"/users/{user}/repos", per_page=100, page=page, type="owner", sort="pushed"
            )
            if batch is None:
                raise GitHubError(f"usuário {user!r} não encontrado")
            repos += batch
            if len(batch) < 100:
                return repos
            page += 1

    def languages(self, user: str, repo: str) -> dict[str, int]:
        return self._get(f"/repos/{user}/{repo}/languages") or {}

    def preview_image(self, user: str, repo: str, branch: str) -> bytes | None:
        """Baixa docs/preview.png do repositório, se existir e for um PNG válido."""
        meta = self._get(f"/repos/{user}/{repo}/contents/{PREVIEW_PATH}", ref=branch)
        if not isinstance(meta, dict) or meta.get("type") != "file" or not meta.get("download_url"):
            return None
        if meta.get("size", 0) > MAX_PREVIEW_BYTES:
            return None
        try:
            # requests.get (sem a sessão) para não enviar o token a outro domínio.
            r = requests.get(meta["download_url"], timeout=20)
        except requests.RequestException as e:
            raise GitHubError(f"download de {PREVIEW_PATH} em {repo} falhou: {e}") from e
        if not r.ok or not r.content.startswith(PNG_MAGIC) or len(r.content) > MAX_PREVIEW_BYTES:
            return None
        return r.content
