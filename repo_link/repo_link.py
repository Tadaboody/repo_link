import re
from typing import Tuple, Optional
from pathlib import Path


def parse(link: str) -> Tuple[Path, str, Optional[str]]:
    """Given a github link returns the File path, git commit, line and collumn the link refers to"""
    # https://regex101.com/r/jBJ7PI/2
    match = re.match(
        r"https://github\.com/.+/([^/]+)/blob/([^/]+)/([^#]+)(?:#L(\d+))?", link
    )
    if match:
        groups = match.groups()
        return Path(groups[0]) / groups[2], groups[1], groups[3]
    raise ValueError("Invalid link")


def checkout(path: str):
    """Checks out the given github pathspec (commit/branch) in the local repository"""


def clone(parent_dir: Path, repo_path: str):
    """Clones the given repo in parent_dir. Raises FileAlreadyExists if the repo exists"""


def main():
    pass


if __name__ == "__main__":
    main()
