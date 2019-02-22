import os
from setuptools import setup, find_packages

here = os.path.split(os.path.realpath(__file__))[0]

class MustGivePackageName(Exception):
    pass

modules = os.listdir(os.path.join(here, 'src'))
if len(modules) > 1:
    raise MustGivePackageName('You have multiple folders in src/.  '
                    'Add the package name manually to the setup.py')
else:
    package_name = modules[0]

class NotTrueOrFalse(Exception):
    pass
def read_bool_file(txt):
    tf = txt.strip()
    if tf == 'True':
        return True
    if tf == 'False':
        return False
    else:
        return None

with open(os.path.join(here, 'runs_on_tile')) as f:
    runs_on_tile = read_bool_file(f.read())

with open(os.path.join(here, 'runs_on_server')) as f:
    runs_on_server = read_bool_file(f.read())

if runs_on_tile is None:
    raise NotTrueOrFalse('There must be a file called runs_on_tile in the top level.  The contents of the file must be True or False')
if runs_on_server is None:
    raise NotTrueOrFalse('There must be a file called runs_on_server in the top level.  The contents of the file must be True or False')


def pull_repo_name_from_url(url):
    """
    Takes a git url and returns the repo name
    e.g.
    url = "git+ssh://git@github.com/my-organization/some-git-dependency.git#egg=some-git-dependency-0"
    returns "some-git-dependency"
    """
    repo_with_egg = url.split('/')[-1]
    repo, egg = repo_with_egg.split('#')
    assert repo.endswith('.git')
    repo = repo[:-4]
    return "tumalow.{0}".format(repo)

def get_dependency(req):
    """
    From the requirements entry, returns requirement and dependency link
    """
    if not req.startswith('git+'):
        #this is a normal pip package
        return req, None
    else:
        #this is a github repo
        repo = pull_repo_name_from_url(req)
        return repo, req

def make_classifiers(tile, server):
    """
    Hijack the classifiers section with un-approved strings.
    """
    classifiers = []
    if tile:
        classifiers.append('Tumalow :: SmartTile')
    if server:
        classifiers.append('Tumalow :: Server')
    return classifiers
classifiers = make_classifiers(runs_on_tile, runs_on_server)

with open(os.path.join(here, 'install_requires.txt')) as f:
    reqs = f.readlines()
reqs = [r.strip() for r in reqs]
#remove "comments"
reqs = [r for r in reqs if not r.startswith('#')]
install_requires = []
dependency_links = []
for req in reqs:
    require, dependency = get_dependency(req)
    install_requires.append(require)
    if dependency is not None:
        dependency_links.append(dependency)

with open(os.path.join('src', package_name, '__version__')) as f:
    version = f.read().strip()

#namespace with tumalow to avoid conflicts with public Pypi packages
pip_name = 'tumalow.{0}'.format(package_name)

setup(
    name=pip_name, #pip install this name
    version=version, 
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    classifiers=classifiers
)
