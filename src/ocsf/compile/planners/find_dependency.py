from pathlib import PurePath
from typing import Optional

from ocsf.repository import Repository, extensionless, extension, as_path, RepoPath, RepoPaths, EventDefn, ObjectDefn


def find_dependency(repo: Repository, subject: str, relative_to: Optional[RepoPath] = None) -> RepoPath | None:
    """Find the target of an $include directive relative to its source file.

    Arguments:
        subject: The subject to locate as it is described in the directive. It may be a filepath, an object name, etc.
        relative_to: The file containing (or implying) the directive instruction.

    Returns: A filepath in the Repository that references the source file.
    """

    subj_path = PurePath(subject)
    files: list[str] = [subject]
    if subj_path.suffix != ".json":
        files.append(subject + ".json")

    paths: list[PurePath] = []

    if relative_to is not None:
        paths.append(PurePath(relative_to))

        if extension(relative_to) is not None:
            paths.append(PurePath(extensionless(relative_to)))

    for entry in paths:
        for path in [entry] + list(entry.parents):
            for file in files:
                k = as_path(path, file)
                if k in repo:
                    return k

    return None


def find_base(repo: Repository, subject: str, relative_to: RepoPath) -> RepoPath | None:
    rel_path = PurePath(relative_to)

    idx = rel_path.parts.index(RepoPaths.OBJECTS.value)
    if idx == -1:
        idx = rel_path.parts.index(RepoPaths.EVENTS.value)
    prefix = as_path(*rel_path.parts[:idx])

    for file in repo.files():
        if file.path.startswith(prefix):
            subj_path = PurePath(file.path)
            if subj_path.stem == subject:
                return file.path
            elif isinstance(file.data, ObjectDefn) or isinstance(file.data, EventDefn):
                if file.data.name is not None and file.data.name == subject:
                    return file.path

    if extension(relative_to) is not None:
        return find_base(repo, subject, extensionless(relative_to))

    return None
