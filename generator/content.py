"""Carregamento dos YAML e escolha de idioma com fallback."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

LANGS = ("pt", "en")


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: esperava um mapa YAML na raiz")
    return data


def is_leaf(value: Any) -> bool:
    """Um mapa cujas chaves são só idiomas ({pt:..., en:...}) é um texto traduzível."""
    return isinstance(value, dict) and bool(value) and set(value) <= set(LANGS)


def localize(value: Any, lang: str, warnings: list[str] | None = None, where: str = "") -> Any:
    """Troca cada {pt, en} pelo texto do idioma. Se faltar, usa o outro e registra aviso."""
    if is_leaf(value):
        text = value.get(lang)
        if text:
            return text
        other = next((v for v in value.values() if v), "")
        if other and warnings is not None:
            warnings.append(f"{where or '?'}: falta o texto em '{lang}'")
        return other
    if isinstance(value, dict):
        return {k: localize(v, lang, warnings, f"{where}.{k}" if where else k) for k, v in value.items()}
    if isinstance(value, list):
        return [localize(v, lang, warnings, f"{where}[{i}]") for i, v in enumerate(value)]
    return value


def project_text(
    repo: dict, overrides: dict, lang: str, warnings: list[str]
) -> dict[str, Any]:
    """Título, descrição e links de um projeto no idioma pedido.

    Retorna também `fallback`: True quando o texto veio de outro idioma
    ou da descrição do GitHub (nesse caso o site mostra um aviso discreto).
    """
    name = repo["name"]
    cfg = overrides.get(name) or {}
    where = f"projects.{name}"

    title = localize(cfg.get("title"), lang, warnings, f"{where}.title") or name

    desc_cfg = cfg.get("description")
    fallback = False
    if desc_cfg:
        description = localize(desc_cfg, lang, warnings, f"{where}.description")
        fallback = is_leaf(desc_cfg) and not desc_cfg.get(lang)
    else:
        description = (repo.get("description") or "").strip()
        fallback = bool(description)
        if description:
            warnings.append(f"{where}: sem entrada em projects.yml (usando a descrição do GitHub)")
        else:
            warnings.append(f"{where}: sem descrição (nem em projects.yml, nem no GitHub)")

    links = localize(cfg.get("links") or [], lang, warnings, f"{where}.links")
    return {"title": title, "description": description, "links": links, "fallback": fallback}
