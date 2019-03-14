import os
import subprocess
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Tuple, Union
from git import Repo


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


def checkout(path: Path, commit: str):
    """Checks out the given github pathspec (commit/branch) in the local repository"""
    repo = Repo(path)
    repo.git.checkout(commit)


def clone(parent_dir: Path, repo_path: str):
    """Clones the given repo in parent_dir. Raises FileAlreadyExists if the repo exists"""


def open_in_editor(path: Path, line: str, editor=os.environ["EDITOR"]):
    """Opens the file given in path and line, inside the editor"""
    command = {
        "vim": f"{editor} +{line} {path}",
        "code": f"{editor} -g {path}:{line}",
        "pycharm": f"{editor} {path}:{line}",
    }[editor.strip(".exe")]
    subprocess.run(command.split())


PathType = Union[os.PathLike, str]


@contextmanager
def cd(path: PathType) -> Iterator[None]:
    old_path = Path.cwd()
    os.chdir(path)
    yield
    os.chdir(old_path)


def main():
    FILE_PATH = Path(__file__)
    open_in_editor(FILE_PATH, 4)


if __name__ == "__main__":
    main()
