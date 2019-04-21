import os
import json
import subprocess
import re
import argparse
from pathlib import Path
from typing import Optional, Union, NamedTuple, Sequence, TypeVar, Callable
from git import Repo  # type: ignore


PathType = Union[os.PathLike, str]
T = TypeVar("T")


class RepoData(NamedTuple):
    user: str
    repository: str
    path: str
    commit: str
    base_link: str
    line: Optional[str]

    def clone_link(self):
        """A URL that allows to clone the repository from"""
        return f"{self.base_link}/{self.user}/{self.repository}"


def parse(link: str) -> RepoData:
    """Given a github link returns the File path, git commit, line and collumn the link refers to"""
    # https://regex101.com/r/jBJ7PI/4
    link_pattern = r"(?P<base_link>https://github\.com)/(?P<user>.+)/(?P<repository>[^/]+)/blob/(?P<commit>[^/]+)/(?P<path>[^#]+)(?:#L(?P<line>\d+))?"
    match = re.match(link_pattern, link)
    if match:
        groups = match.groups()
        return RepoData(**match.groupdict())
    raise ValueError("Invalid link")


def checkout(repo: Repo, commit: str):
    """Checks out the given github pathspec (commit/branch) in the local repository"""
    if repo.head.commit == repo.commit(commit):
        return
    if repo.is_dirty():
        print("Can't make checkout to linked commit, repository is dirty")
        print("Stashing...")
        repo.git.stash()
    repo.git.checkout(commit)


def clone(repo_link: str, target_path: Path) -> Repo:
    """Clones the given repo in parent_dir. Raises FileAlreadyExists if the repo exists"""
    print(f"Repository does not exist, cloning into {target_path}")
    return Repo.clone_from(repo_link.strip("/"), str(target_path))


def open_in_editor(path: PathType, editor: str, line: Optional[str] = None):
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


PARENT_DIRS = [Path.home(), Path.home() / "Forks"]


def open_file(repo: Repo, data: RepoData, editor: str):
    """Opens file corresponding to the given description in the given git repo"""
    checkout(repo, data.commit)
    open_in_editor(
        path=Path(repo.working_dir) / data.path, line=data.line, editor=editor
    )


def find_in_sequence(
    sequence: Sequence[T], predicate: Callable[[T], bool]
) -> Optional[T]:
    """Returns the element that satisfies the predicate, if exists"""
    return next((element for element in sequence if predicate(element)), None)


def find_repo(parents: Sequence[Path], data: RepoData) -> Optional[Repo]:
    """Returns a Repo object that fits the given RepoData in one of the parent directories, if found"""
    parent = find_in_sequence(
        parents, lambda parent: (parent / data.repository).exists()
    )
    if parent:
        return Repo(parent / data.repository)
    return None


def open_link(link: str, editor: str, parents: Sequence[Path]):
    data = parse(link)
    repo = find_repo(parents, data) or clone(
        data.clone_link(), parents[0] / data.repository
    )
    open_file(repo=repo, data=data, editor=editor)


def main():
    args = parse_args()
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


def parse_args() -> argparse.Namespace:
    """Parse command line arguments, will exit if user asked for help"""

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
    return args


if __name__ == "__main__":
    main()
