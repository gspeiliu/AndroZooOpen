###########
# Input:
# Output:
##########

import http.client
import argparse
import sys
import re
import requests,json
import os
import csv
import time
from time import gmtime, strftime
import json
#from BeautifulSoup import BeautifulSoup  
from bs4 import BeautifulSoup
from datetime import datetime

from collections import defaultdict

access_token = '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'
headers = {'Authorization': 'token '+access_token }

dir_name = '2016-2018'

TREE_OUT_BASE = ''

def write_result_to_file(results, file, directory ):
    filename = os.path.join(directory, file + '.json')
    with open(filename, 'w') as outfile:
        json.dump(results, outfile)


def write_repo_to_file(repo_entry):
    fp = '../Git/AndroidRepos/android_repos_{}_left.txt'.format(dir_name)
    with open(fp, 'a+') as f:
        f.write(repo_entry + '\n')

def write_empty_items(repo_entry):
    fp = '../Git/AndroidRepos/empty_items_repos_{}.txt'.format(dir_name)
    with open(fp, 'a+') as f:
        f.write(repo_entry + '\n')

def err_log(repo_entry):
    fp = '../Git/AndroidRepos/err_repos_{}_left.txt'.format(dir_name)
    with open(fp, 'a+') as f:
        f.write(repo_entry + '\n')

def repo_retrieve():
    txt_path = '/data/pei/CICD/Git/Android/{}/down_repos.txt'.format(dir_name)
    with open(txt_path) as f:
        lines = [line.strip().replace('https://github.com/', '') for line in f.readlines()]
    return lines

def repo_handled():
    txt_path = '/data/pei/CICD/Git/AndroidRepos/Android_basic_repositories.txt'
    with open(txt_path) as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def main(argv):
#    access_token = os.environ['GITHUB_TOKEN']
    #directory = '../results/config_circleci'
    payload = {}

    #url = "https://api.github.com/search/code?q=in%3Apath+filename%3Aconfig.yml+path%3A%2F.circleci"
#    url = "https://api.github.com/search/code?q=in%3Apath+filename%3Acircle.yml+path%3A%2F"
    repos = repo_retrieve()
    handled_repos = repo_handled()
    print('length repos:', len(repos))
    idx = 0
    while True:
        if idx >= len(repos):
            break
        repo = repos[idx]
        print(idx, len(repos), repo)
        if repo in handled_repos:
            idx += 1
            continue
        repo_splits = repo.split('/')
        if len(repo_splits) != 2:
            idx += 1
            continue
        user_name = repo_splits[0].strip()
        repo_name = repo_splits[1].strip()
        repo_in_search = 'repo%3A' + user_name + '%2F' + repo_name
#        url = 'https://api.github.com/search/code?q=in%3Apath+filename%3AAndroidManifest.xml+' + repo_in_search
        url = 'https://api.github.com/repos/' + repo + '/commits'
        latest_commit = ''
        try:
            r = requests.get(url, headers=headers, params=payload)
            print(r.status_code, url)
            if r.status_code == 403:
                raise ValueError('temp blocked')
            if r.status_code == 422:
                err_log(repo)
                raise TypeError('422 status returned')
            if r.status_code == 404:
                raise TypeError('404 status returned')
            data = r.json()
            for i in data:
                latest_commit = i['sha']
                break
        except (requests.exceptions.ConnectionError, ValueError) as err:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()),": Waiting for 5 mins before retrying")
            time.sleep(300)
            continue
        except (TypeError) as e:
            idx += 1
            continue
        if latest_commit:
            tree_url = 'https://api.github.com/repos/' + repo + '/git/trees/' + latest_commit + '?recursive=true'
            while True:
                try:
                    r = requests.get(tree_url, headers=headers, params=payload)
                    print(r.status_code, tree_url)
                    if r.status_code == 403:
                        raise ValueError('temp blocked')
                    if r.status_code == 422:
                        err_log(repo)
                        raise TypeError('422 status returned')
                    if r.status_code == 404:
                        raise TypeError('404 status returned')
                    data = r.json()
                    out_base = os.path.join('/data/pei/CICD/Git/AndroidRepos/trees', repo)
                    if not os.path.exists(out_base):
                        os.makedirs(out_base)
                    json_out = os.path.join('/data/pei/CICD/Git/AndroidRepos/trees', repo, 'tree.json')
                    with open(json_out, 'w') as f:
                        json.dump(data, f, indent = 2)
                except (requests.exceptions.ConnectionError, ValueError) as err:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()),": Waiting for 5 mins before retrying")
                    time.sleep(300)
                    continue
                except (TypeError) as e:
                    break
                else:
                    break
        idx += 1

def android_repo_load():
    android_repo_path = '/data/pei/CICD/Git/AndroidRepos/android_repos.txt'
    with open(android_repo_path) as f:
        lines = [line.strip() for line in f.readlines()]
    return lines


def txt_load(txt_path):
    with open(txt_path) as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def ci_android_load():
    action_android_path = '/data/pei/CICD/Git/Actions/real_android_actions.txt'
    travis_android_path = '/data/pei/CICD/Git/Travis/real_android_travis.txt'
    circle_android_path = '/data/pei/CICD/Git/Circles/real_android_circles.txt'

    actions = txt_load(action_android_path)
    travis = txt_load(travis_android_path)
    circles = txt_load(circle_android_path)

    ci_repos = []
    ci_repos.extend(actions)
    ci_repos.extend(travis)
    ci_repos.extend(circles)

#    inters = set()
#    inters.update(set(actions) & set(travis))
#    print('inter:', len(inters))
#    inters.update(set(travis) & set(circles))
#    inters.update(set(actions) & set(travis) & set(circles))
#    print('\n'.join(list(inters)))

    print('total number:', len(set(ci_repos)))

    return actions, travis, circles, ci_repos

def ci_run_android_load():
    action_android_path = '/data/pei/CICD/Git/Actions/wf_run_repos.txt'
    travis_android_path = '/data/pei/CICD/Git/Travis/travis_build_repos.txt'
    circle_android_path = '/data/pei/CICD/Git/Circles/circle_pp_wf_repos.txt'

    actions = txt_load(action_android_path)
    travis = txt_load(travis_android_path)
    circles = txt_load(circle_android_path)

    ci_repos = []
    ci_repos.extend(actions)
    ci_repos.extend(travis)
    ci_repos.extend(circles)

#    inters = set()
#    inters.update(set(actions) & set(travis))
#    print('inter:', len(inters))
#    inters.update(set(travis) & set(circles))
#    inters.update(set(actions) & set(travis) & set(circles))
#    print('\n'.join(list(inters)))

    print('total number:', len(set(ci_repos)))

    return actions, travis, circles, ci_repos

def star_classify(stars):
    if stars <= 500:
        return 500
    if stars > 500 and stars <= 1000:
        return 1000
    if stars > 1000 and stars <= 1500:
        return 1500
    if stars > 1500 and stars <= 2000:
        return 2000
    if stars > 2000 and stars <= 2500:
        return 2500
    if stars > 2500 and stars <= 3000:
        return 3000
    return 5000

def ci_test_repo_load():
    ci_test_repo_path = '/data/pei/CICD/Git/Actions/real_test_android.txt'
    with open(ci_test_repo_path) as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def repo_basic_stats():
    repos = android_repo_load()
    ci_actions, ci_travis, ci_circles, ci_repos = ci_android_load()
    ci_test_repos = ci_test_repo_load()
    basic_outs = []

    star_ci_repos = defaultdict(int)
    star_ci_wo_repos = defaultdict(int)

    year_ci_repos = defaultdict(int)
    year_ci_wo_repos = defaultdict(int)

    ci_action_year_repos = defaultdict(int)

    ci_stars = []
    ci_wo_stars = []
    ci_test_stars = []

    for idx, repo in enumerate(repos):
        repo_splits = repo.split('/')
        user_name = repo_splits[0].strip()
        repo_name = repo_splits[1].strip()
        repo_basic_path = os.path.join('/data/pei/CICD/Git/AndroidRepos/Basics', user_name, repo_name + '.txt')
        if os.path.exists(repo_basic_path):
            with open(repo_basic_path) as f:
                data = json.load(f)
            # created_at   updated_at   pushed_at   size   stargazers_count  watchers_count   forks_count  watchers  
            create_ts = data['created_at']
            create_year = datetime.strptime(str(create_ts), '%Y-%m-%dT%H:%M:%SZ').year
            if repo in ci_repos:
                year_ci_repos[create_year] += 1
            else:
                year_ci_wo_repos[create_year] += 1
            if repo in ci_actions:
                ci_action_year_repos[create_year] += 1
            updated_ts = data['updated_at']
            push_ts = data['pushed_at']
            size = data['size']
            stars = data['stargazers_count']
            curr_star = stars
            if repo in ci_repos:
                star_ci_repos[str(curr_star)] += 1
                ci_stars.append([stars])
                if repo in ci_test_repos:
                    ci_test_stars.append([stars])
            else:
                star_ci_wo_repos[str(curr_star)] += 1
                ci_wo_stars.append([stars])
            watchers_count = data['watchers_count']
            forks_count = data['forks_count']
            watchers = data['watchers']
            curr = [repo, create_ts[:4], updated_ts[:4], push_ts[:4], size, stars, watchers_count, forks_count, watchers]
            basic_outs.append(curr)
    star_repos = []
    year_repos = []

    for year, cnt in ci_action_year_repos.items():
        print(year,cnt)

    for year, cnt in year_ci_repos.items():
        year_repos.append([year, cnt, 'CI/CD'])
    for year, cnt in year_ci_wo_repos.items():
        year_repos.append([year, cnt, 'None'])

    for star, cnt in star_ci_repos.items():
        star_repos.append([star, cnt, 'CI/CD'])
    for star, cnt in star_ci_wo_repos.items():
        star_repos.append([star, cnt, 'None'])
    ci_stars_out = '/data/pei/CICD/Git/AndroidRepos/ci_stars_dist.csv'
    ci_wo_stars_out = '/data/pei/CICD/Git/AndroidRepos/ci_wo_stars_dist.csv'
    ci_test_stars_out = '/data/pei/CICD/Git/AndroidRepos/ci_test_stars_dist.csv'
    with open(ci_stars_out, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(ci_stars)
    with open(ci_wo_stars_out, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(ci_wo_stars)
    with open(ci_test_stars_out, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(ci_test_stars)
    out_path = '/data/pei/CICD/Git/AndroidRepos/repo_basics.csv'
    with open(out_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(basic_outs)
    star_out_path = '/data/pei/CICD/Git/star_repo_distribution.csv'
    year_out_path = '/data/pei/CICD/Git/year_repo_distribution.csv'
    with open(star_out_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(star_repos)
    with open(year_out_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(year_repos)

def repo_basic_retrieve():
    payload = {}

    repos = android_repo_load()
    handled_repos = repo_handled()
    print('length repos:', len(repos))
    idx = 0
    while True:
        if idx >= len(repos):
            break
        repo = repos[idx]
        print(idx, len(repos), repo)
        if repo in handled_repos:
            idx += 1
            continue
        repo_splits = repo.split('/')
        user_name = repo_splits[0].strip()
        repo_name = repo_splits[1].strip()
        if len(repo_splits) != 2:
            idx += 1
            continue
        url = 'https://api.github.com/repos/' + repo
        try:
            r = requests.get(url, headers=headers, params=payload)
            print(r.status_code, url)
            if r.status_code == 403:
                raise ValueError('temp blocked')
            if r.status_code == 422:
                err_log(repo)
                raise TypeError('422 status returned')
            if r.status_code == 404:
                raise TypeError('404 status returned')
            data = r.json()
            user_out_dir = os.path.join('/data/pei/CICD/Git/AndroidRepos/Basics', user_name)
            if not os.path.exists(user_out_dir):
                os.mkdir(user_out_dir)
            basic_out_path = os.path.join(user_out_dir, repo_name + '.txt')
            with open(basic_out_path, 'w') as f:
                json.dump(data, f, indent = 2)
        except (requests.exceptions.ConnectionError, ValueError) as err:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()),": Waiting for 5 mins before retrying")
            time.sleep(300)
            continue
        except (TypeError) as e:
            idx += 1
            continue
        idx += 1

def txt_dump(txt_path, txt_content):
    with open(txt_path, 'w') as f:
        f.write(txt_content)

def star_comparison_ci_real_run():
    repo_stars = dict()
    star_csv_path = '/data/pei/CICD/Git/AndroidRepos/repo_basics.csv'
    with open(star_csv_path) as f:
        reader = csv.reader(f)
        for row in reader:
            repo_stars[row[0]] = row[5]

    all_repos = android_repo_load()
    ci_run_actions, ci_run_travis, ci_run_circle, ci_run_repos = ci_run_android_load()
    ci_actions, ci_travis, ci_circle, ci_repos = ci_android_load()
    repo_without_ci_stars = []
    repo_withci_stars = []
    repo_cirun_stars = []
    repo_onlyci_stars = []
    for repo in all_repos:
        star = '0'
        if repo in repo_stars:
            star = str(repo_stars[repo])
        if repo in ci_repos:
            repo_withci_stars.append(star)
        else:
            repo_without_ci_stars.append(star)
    for repo in ci_repos:
        star = '0'
        if repo in repo_stars:
            star = str(repo_stars[repo])
        if repo in ci_run_repos:
            repo_cirun_stars.append(star)
        else:
            repo_onlyci_stars.append(star)

    txt_dump('/data/pei/CICD/Git/repo_without_ci_stars.txt', '\n'.join(repo_without_ci_stars))
    txt_dump('/data/pei/CICD/Git/repo_withci_stars.txt', '\n'.join(repo_withci_stars))
    txt_dump('/data/pei/CICD/Git/repo_cirun_stars.txt', '\n'.join(repo_cirun_stars))
    txt_dump('/data/pei/CICD/Git/repo_onlyci_stars.txt', '\n'.join(repo_onlyci_stars))

if __name__ == "__main__":
    main(sys.argv)
#    web_resolve()
#    repo_basic_retrieve()
#    repo_basic_stats()
#    ci_android_load()
#    star_comparison_ci_real_run()
