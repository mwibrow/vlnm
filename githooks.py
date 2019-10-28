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


class Messenger:

    tab = 0
    tab_width = 4

    def __enter__(self):
        Messenger.tab += 1
        return self

    def __exit__(self, *args):
        Messenger.tab -= 1

    @classmethod
    def message(cls, text, styles=None):
        print(' ' * (cls.tab * cls.tab_width) +
              ''.join(style or '' for style in styles) + text + Style.RESET_ALL)

    def __call__(self, *args, **kwargs):
        self.message(*args, **kwargs)

    def indent(self):
        return self


def pre_commit():
    message = Messenger()
    message('Running pre-commit...', [Fore.YELLOW])
    with message.indent():
        message('- Checking changed files', [Fore.YELLOW])
        repo = Repo(REPO_PATH)
        diff = repo.git.diff(repo.active_branch, name_only=True)
        changed = [
            item for item in diff.split('\n') if item.endswith('.py')]
        message('- {} found'.format(len(changed)), [Fore.YELLOW])
        if changed:
            message('- Running autopep8 on files', [Fore.YELLOW])
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
