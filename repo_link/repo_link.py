import os
import subprocess
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Union, NamedTuple
from git import Repo, GitCommandError, Commit


PathType = Union[os.PathLike, str]


class RepoData(NamedTuple):
    user: str
    repository: str
    path: str
    commit: str
    line: Optional[str]


def parse(link: str) -> RepoData:
    """Given a github link returns the File path, git commit, line and collumn the link refers to"""
    # https://regex101.com/r/jBJ7PI/4
    link_pattern = r"https://github\.com/(?P<user>.+)/(?P<repository>[^/]+)/blob/(?P<commit>[^/]+)/(?P<path>[^#]+)(?:#L(?P<line>\d+))?"
    match = re.match(link_pattern, link)
    if match:
        groups = match.groups()
        return RepoData(**match.groupdict())
    raise ValueError("Invalid link")


def checkout(commit: str):
    """Checks out the given github pathspec (commit/branch) in the local repository"""
    repo = Repo(".")
    if repo.head.commit == repo.commit(commit):
        return
    if repo.is_dirty():
        print("Can't make checkout to linked commit, repository is dirty")
        print("Stashing...")
        repo.git.stash()
    repo.git.checkout(commit)


def clone(repo_link: str):
    """Clones the given repo in parent_dir. Raises FileAlreadyExists if the repo exists"""
    Repo().git.clone(repo_link.strip("/"))


def open_in_editor(path: PathType, line: str = "0", editor: str = os.environ["EDITOR"]):
    """Opens the file given in path and line, inside the editor"""
    command = {
        "vim": f"{editor} +{line} {path}",
        "code": f"{editor} -g {path}:{line}",
        "pycharm": f"{editor} {path}:{line}",
    }[editor]
    subprocess.run(command.split())


@contextmanager
def cd(path: PathType) -> Iterator[None]:
    old_path = Path.cwd()
    os.chdir(path)
    yield
    os.chdir(old_path)


PARENT_DIRS = [Path.home(), Path.home() / "Forks"]


def open_link(repo: Path, file: str, commit: str, line: str):
    with cd(repo):
        checkout(commit)
        open_in_editor(file, line)


def main():
    link = "https://github.com/erikrose/more-itertools/blob/master/more_itertools/recipes.py#L74"
    data = parse(link)
    existing_repos = {
        repo: path for path in PARENT_DIRS for repo in path.iterdir() if repo.is_dir()
    }
    for parent in (
        parent for parent in PARENT_DIRS if (parent / data.repository).exists()
    ):
        open_link(
            repo=parent / data.repository,
            file=data.path,
            commit=data.commit,
            line=data.line,
        )
        return
    with cd(PARENT_DIRS[0]):
        clone(link.partition("/blob")[0])
        open_link(data.repository, data.commit, data.line, file=data.path)


if __name__ == "__main__":
    main()
