import pytest
from pathlib import Path
from repo_link import parse, RepoData


@pytest.mark.parametrize(
    ["link", "data"],
    [
        (
            "https://github.com/erikrose/more-itertools/blob/master/more_itertools/recipes.py#L74",
            RepoData(
                path="more_itertools/recipes.py",
                repository="more-itertools",
                user="erikrose",
                commit="master",
                line="74",
                base_link="https://github.com",
            ),
        ),
        # No lineno
        (
            "https://github.com/thepracticaldev/dev.to/blob/master/.gitdocs.js",
            RepoData(
                path=".gitdocs.js",
                user="thepracticaldev",
                repository="dev.to",
                commit="master",
                base_link="https://github.com",
                line=None,
            ),
        ),
        # # Branch name with slash
        # ("https://github.com/thepracticaldev/dev.to/blob/ben/fix-js-for-comment-creation/.gitdocs.js",
        # Path("dev.to/.gitdocs.js"),
        # "ben/fix-js-for-comment-creation",
        # None)
    ],
)
def test_parse(link, data):
    assert parse(link) == data
