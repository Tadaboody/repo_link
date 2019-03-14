import pytest
from repo_link import parse


@pytest.mark.parametrize(
    ["link", "path", "line", "col"],
    [
        (
            "https://github.com/erikrose/more-itertools/blob/master/more_itertools/recipes.py#L74",
            "more-itertools/more_itertools/recipies.py",
            "master",
            "74",
            None,
        )
    ],
)
def test_parse(link, path, line, col):
    assert parse(link) == (path, line, col)
