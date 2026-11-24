"""Uso:
    python -m generator                      # lê o GitHub (usa GITHUB_TOKEN se existir)
    python -m generator --fixture arq.json   # dados de exemplo, sem rede
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .build import build
from .config import Settings
from .fixtures import FixtureSource
from .github import GitHubClient, GitHubError


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="generator")
    ap.add_argument("--fixture", type=Path, help="JSON de exemplo em vez da API do GitHub")
    ap.add_argument("--out", type=Path, help="pasta de saída (padrão: dist/)")
    args = ap.parse_args(argv)

    settings = Settings.from_env(out_dir=args.out)
    source = FixtureSource(args.fixture) if args.fixture else GitHubClient(settings.token)
    try:
        warnings = build(settings, source)
    except GitHubError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1  # o build falha e o site publicado continua intacto

    for w in warnings:
        print(f"aviso: {w}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and warnings:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("### Avisos do portfólio\n" + "".join(f"- {w}\n" for w in warnings))
    print(f"site gerado em {settings.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
