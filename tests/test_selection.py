import json
from pathlib import Path

from generator.selection import order_repos, select_portfolio_repos

REPOS = json.loads((Path(__file__).parent / "fixtures" / "repos.json").read_text())["repos"]


def names(repos):
    return [r["name"] for r in repos]


def test_filters_topic_fork_archived_excluded_and_special_repos():
    selected = select_portfolio_repos(REPOS, "Toledooo")
    assert sorted(names(selected)) == ["api-exemplo", "rpa-exemplo"]


def test_private_repos_never_selected():
    private = {**REPOS[0], "name": "segredo", "private": True}
    assert "segredo" not in names(select_portfolio_repos([private], "Toledooo"))


def test_order_featured_first_then_most_recent_push():
    selected = select_portfolio_repos(REPOS, "Toledooo")
    assert names(order_repos(selected, set(), 6)) == ["rpa-exemplo", "api-exemplo"]
    assert names(order_repos(selected, {"api-exemplo"}, 6)) == ["api-exemplo", "rpa-exemplo"]


def test_order_respects_limit():
    selected = select_portfolio_repos(REPOS, "Toledooo")
    assert len(order_repos(selected, set(), 1)) == 1
