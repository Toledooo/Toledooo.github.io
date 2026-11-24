from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    user: str
    site_url: str
    base_path: str  # "" para site de usuário; "/nome-do-repo" para site de projeto
    contact_url: str
    token: str | None
    out_dir: Path
    root: Path = ROOT

    @classmethod
    def from_env(cls, out_dir: Path | None = None) -> "Settings":
        user = os.environ.get("PORTFOLIO_USER", "Toledooo")
        base_path = os.environ.get("BASE_PATH", "").strip().rstrip("/")
        if base_path and not base_path.startswith("/"):
            base_path = "/" + base_path
        return cls(
            user=user,
            site_url=os.environ.get("SITE_URL", f"https://{user.lower()}.github.io").rstrip("/"),
            base_path=base_path,
            contact_url=os.environ.get("CONTACT_URL", "").strip(),
            token=os.environ.get("GITHUB_TOKEN") or None,
            out_dir=out_dir or ROOT / "dist",
        )
