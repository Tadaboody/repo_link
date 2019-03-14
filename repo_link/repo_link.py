from typing import Tuple
from pathlib import Path
from git import Repo


def parse(link: str) -> Tuple[str, str, int, int]:
    """Given a github link returns the Repository name , git commit, line and collumn the link refers to"""


def checkout(path: str):
    """Checks out the given github pathspec (commit/branch) in the local repository"""


def clone(parent_dir: Path, repo_path: str):
    """Clones the given repo in parent_dir. Raises FileAlreadyExists if the repo exists"""
