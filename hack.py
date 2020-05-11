# This quick shortcut shows functionality that can be added to
# the ContributorList class in contrib.py

from github import Github, GithubException
from jinja2 import FileSystemLoader, Environment
from yaml import safe_load
import re
from time import sleep
from pathlib import Path
from datetime import datetime as dt

file_loader = FileSystemLoader('views')
env = Environment(loader=file_loader)
project = env.get_template('project.yaml')

def contribs(g, name):
    repo = g.get_repo(name)
    contrib = repo.get_stats_contributors()
    if contrib is None:
        contrib = []
    return project.render(r = repo, contrib = contrib)

def main():
    out = Path('data')
    g = Github("63352f6d62ca1d73f4d1b9eeb6a3e07a5707bf33")

    with open("repolist.yaml") as f:
        repos = safe_load(f)

    # Comb through repos
    repo_re = re.compile("github.com/([^/]*)/([^/]*)$")
    for proj, args in repos.items():
        for url in args['urls']:
            m = repo_re.search(url)
            if m is None:
                print("Skipping: %s"%url)
                continue

            # plan file output location
            fname = "%s.%s.yaml"%(m[1],m[2])
            repofile = out / proj / fname
            if repofile.exists(): # already checked
                continue

            # gather data
            repo = "%s/%s"%(m[1],m[2])
            try:
                s = contribs(g, repo)
            except GithubException:
                print("Unable to open %s"%repo)
                continue

            # output to file
            print("Writing: %s"%url)
            (out / proj).mkdir(exist_ok=True)
            with open(repofile, 'w') as f:
                f.write("# Gathered on %s\n"%str(
                    dt.now().strftime("%Y-%m-%d %H:%M")))
                f.write(s)
        sleep(1)

main()
