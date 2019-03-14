import pytest
from pathlib import Path
from repo_link import parse


@pytest.mark.parametrize(
    ["link", "path", "commit", "line"],
    [
        (
            "https://github.com/erikrose/more-itertools/blob/master/more_itertools/recipes.py#L74",
            Path("more-itertools/more_itertools/recipes.py"),
            "master",
            "74",
        ),
        # No lineno
        (
            "https://github.com/thepracticaldev/dev.to/blob/master/.gitdocs.js",
            Path("dev.to/.gitdocs.js"),
            "master",
            None,
        ),
        # # Branch name with slash
        # ("https://github.com/thepracticaldev/dev.to/blob/ben/fix-js-for-comment-creation/.gitdocs.js",
        # Path("dev.to/.gitdocs.js"),
        # "ben/fix-js-for-comment-creation",
        # None)
    ],
)
def test_parse(link, path, commit, line):
    assert parse(link) == (path, commit, line)
