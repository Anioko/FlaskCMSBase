import glob
import os

from libs import GitUtils
from app.utils import get_setting_val

base_path = '/app/code/compressed'
code_path = '/app/code/sweet'


def get_compressed_files(username):
    user_path = os.path.join(base_path, username)
    if not os.path.isdir(user_path):
        os.makedirs(user_path)
    files = [file for file in glob.glob(f'{user_path}/*.zip')]
    return files


def create_compressed_archive(username):
    from distutils.dir_util import copy_tree
    from shutil import rmtree
    from zipfile import ZipFile

    repo_setting = get_setting_val(('git_repo', "Git Repo"))
    repo = 'git@bitbucket.org:IbrahimGad/sweet.git'
    if repo_setting:
        if repo_setting.value:
            repo = repo_setting.value

    mygit = GitUtils(
        repo=repo,
        user={
            'ssh': '/app/shell_scripts/gitpython_ssh.sh',
            'name': 'eibrahim95',
            'email': 'eibrahim95@gmail.com',
        },
        path='/app/code/sweet'
    )
    user_path = os.path.join(base_path, username)
    if not os.path.isdir(user_path):
        os.makedirs(user_path)
    new_archive_path = os.path.join(user_path, 'alpha')
    copy_tree(code_path, new_archive_path)
    dot_git_path = os.path.join(new_archive_path, '.git')
    zip_path = os.path.join(user_path, 'alpha.zip')
    rmtree(dot_git_path)
    with ZipFile(zip_path, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(new_archive_path):
            for filename in filenames:
                # create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                # Add file to zip
                zipObj.write(filePath, os.path.basename(filePath))
    return True
