#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

def git_android_check():
    tree_base = '/data/pei/CICD/Git/AndroidRepos/trees'
    android_repos = set()
    names = os.listdir(tree_base)
    for name in names:
        user_base = os.path.join(tree_base, name)
        repos = os.listdir(user_base)
        for repo in repos:
            tree_json_path = os.path.join(tree_base, name, repo, 'tree.json')
            if os.path.exists(tree_json_path):
                with open(tree_json_path) as f:
                    tree = json.load(f)
                    files = tree['tree']
                    for f in files:
                        fpath = f['path']
                        if fpath == 'AndroidManifest.xml' or fpath.endswith('/AndroidManifest.xml'):
                            android_repos.add(name + '/' + repo)
    out_path = '/data/pei/CICD/Git/AndroidRepos/Android_tree_check_Sept.txt'
    with open(out_path, 'w') as f:
        f.write('\n'.join(list(android_repos)))

if __name__ == '__main__':
    git_android_check()
