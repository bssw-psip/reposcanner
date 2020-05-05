# This quick shortcut shows functionality that can be added to
# the ContributorList class in contrib.py

from github import Github
from jinja2 import FileSystemLoader, Environment
from yaml import safe_load
import re

file_loader = FileSystemLoader('views')
env = Environment(loader=file_loader)
t = env.get_template('project.yaml')

g = Github("63352f6d62ca1d73f4d1b9eeb6a3e07a5707bf33")

repos = safe_load("repolist.yaml")

# TODO: use re to search for github.com/user/repo format
# inside entries of repos['ADCD03']['urls']
# rname = re.match()

# This formatter works!
#name = "frobnitzem/libdag"
#name = "bssw-psip/reposcanner"
#name = "lanl/SICM"
repo = g.get_repo(name)
contrib = repo.get_stats_contributors()
s = t.render(r = repo, contrib = contrib)

print(s)

