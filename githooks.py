"""
Git hooks scripts.
"""
import os
import sys

import autopep8
from colorama import init as colorama_init, Fore, Style
from git import Repo


REPO_PATH = os.path.abspath(os.path.dirname(__file__))

colorama_init()


def message(text, styles=None):
    print(''.join(style or '' for style in styles) + text + Style.RESET_ALL)


def pre_commit():
    message('Running pre-commit...', [Fore.YELLOW])
    message('   - Checking changed files', [Fore.YELLOW])
    repo = Repo(REPO_PATH)
    diff = repo.git.diff(repo.active_branch, name_only=True)
    changed = [
        item for item in diff.split('\n') if item.endswith('.py')]
    message('   - {} found'.format(len(changed)), [Fore.YELLOW])
    if changed:
        message('   - Running autopep8 on files', [Fore.YELLOW])
        options = autopep8.parse_args([
            '--global-config=.pep8',
            '--in-place'] + changed)
        autopep8.fix_multiple_files(changed, options)
    message('...done.', [Fore.YELLOW])
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
