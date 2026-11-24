from generator.content import localize, project_text


def test_localize_picks_language():
    assert localize({"pt": "oi", "en": "hi"}, "en") == "hi"


def test_localize_falls_back_and_warns():
    warnings = []
    assert localize({"pt": "oi"}, "en", warnings, "x") == "oi"
    assert warnings == ["x: falta o texto em 'en'"]


def test_localize_recurses_and_keeps_plain_values():
    data = {"a": [{"pt": "um", "en": "one"}], "b": "fixo", "c": 3}
    assert localize(data, "pt") == {"a": ["um"], "b": "fixo", "c": 3}


def test_project_text_uses_yaml_then_github_fallback():
    repo = {"name": "r", "description": "from github"}
    warnings = []
    cfg = {"r": {"description": {"pt": "texto", "en": "text"}}}
    got = project_text(repo, cfg, "en", warnings)
    assert got["description"] == "text" and got["fallback"] is False and not warnings

    got = project_text(repo, {}, "pt", warnings)
    assert got["description"] == "from github" and got["fallback"] is True
    assert warnings and "projects.yml" in warnings[0]


def test_project_text_missing_translation_marks_fallback():
    repo = {"name": "r", "description": ""}
    cfg = {"r": {"description": {"pt": "so pt"}}}
    got = project_text(repo, cfg, "en", [])
    assert got["description"] == "so pt" and got["fallback"] is True
