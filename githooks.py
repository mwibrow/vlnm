"""
Git hooks scripts.
"""
import os
import sys

import autopep8
from git import Repo

REPO_PATH = os.path.abspath(os.path.dirname(__file__))


def pre_commit():
    repo = Repo(REPO_PATH)
    diff = repo.git.diff(repo.active_branch, name_only=True)
    changed = [
        item for item in diff.split('\n') if item.endswith('.py')]

    options = autopep8.parse_args([
        '--global-config=.pep8',
        '--in-place'] + changed)
    autopep8.fix_multiple_files(changed, options)

    return True


HOOKS = {
    'pre-commit': pre_commit
}


def main(argv):
    for arg in argv:
        if arg[2:] in HOOKS:
            if not HOOKS[arg[2:]]():
                sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
