import os
import json
import subprocess
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Union, NamedTuple, Sequence
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
    print(f"Repository does not exist, cloning into {Path.cwd()}")
    Repo().git.clone(repo_link.strip("/"))


def open_in_editor(
    path: PathType, line: Optional[str] = None, editor: str = os.environ["EDITOR"]
):
    """Opens the file given in path and line, inside the editor"""
    if line:
        command = {
            "vim": f"{editor} +{line} {path}",
            "code": f"{editor} -g {path}:{line}",
            "pycharm": f"{editor} {path}:{line}",
        }[editor]
    else:
        command = f"{editor} {path}"
    subprocess.run(command.split())


@contextmanager
def cd(path: PathType) -> Iterator[None]:
    old_path = Path.cwd()
    os.chdir(path)
    yield
    os.chdir(old_path)


PARENT_DIRS = [Path.home(), Path.home() / "Forks"]


def open_file(repo: PathType, file: str, commit: str, line: Optional[str], editor: str):
    with cd(repo):
        checkout(commit)
        open_in_editor(file, line, editor=editor)


def open_link(link: str, editor: str, parents: Sequence[Path]):
    data = parse(link)
    for parent in (parent for parent in parents if (parent / data.repository).exists()):
        open_file(
            repo=parent / data.repository,
            file=data.path,
            commit=data.commit,
            line=data.line,
            editor=editor,
        )
        return
    with cd(parents[0]):
        clone(link.partition("/blob")[0])
        open_file(
            repo=data.repository,
            commit=data.commit,
            line=data.line,
            file=data.path,
            editor=editor,
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Open github link in editor")
    parser.add_argument(dest="link", type=str, help="The opened link")
    parser.add_argument(
        "--parents",
        type=str,
        nargs="+",
        help="Directories where the repository will be searched. if not found it will be cloned into the first one",
    )
    parser.add_argument(
        "--editor",
        dest="editor",
        default=None,
        help="The editor opened (default: EDITOR)",
    )
    parser.add_argument(
        "--config",
        help="A json file where command line options can be hard-coded, default:~/.repo_link_config.json",
        default="~/.repo_link_config.json",
        dest="config",
    )
    args = parser.parse_args()
    config_path = Path(args.config).expanduser()
    if config_path.exists():
        with open(config_path) as fp:
            config = json.load(fp)
        config["parents"] = [Path(parent).expanduser() for parent in config["parents"]]
        open_link(link=args.link, **config)
        return
    open_link(
        args.link,
        editor=args.editor or os.environ["EDITOR"],
        parents=[Path(parent) for parent in args.parents or []] or PARENT_DIRS,
    )


if __name__ == "__main__":
    main()
