#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import csv
import gzip
import tarfile
import requests

import threading
import time

import shutil

from datetime import date

from down_repo import gh_download
from down_md_rev import retrieve_meta_review
from down_fdroid import appid_on_fdroid
from down_fdroid import repo_source_site_fdroid

LAST_DATE = '2020-04-01'
CURR_DATE = date.today().isoformat()
PARENT_PATH = ''

TIME_INTERVAL = 7 * 24 * 60 * 60

mainHttp = 'https://github.com/topics/android?q=created%3A'
unscoped = '&unscoped_q=created%3A'

def pkg_on_androzoo():
    ## download csv file from androzoo
    csv_fpath = os.path.join('./', 'AndroZoo', 'latest.csv')
#    if not os.path.isdir(androzoo_path):
#        os.mkdir(androzoo_path)
    ret_pkg_list = []
#    url = 'https://androzoo.uni.lu/static/lists/latest.csv.gz'
#    req = requests.get(url, stream=True)
#    file_path = os.path.join(androzoo_path, 'latest.csv.gz')
#    if req.status_code == 200:
#        with open(file_path, 'wb') as fd:
#            for chunk in req.iter_content(chunk_size=1024):
#                fd.write(chunk)
#    csv_fpath = os.path.join(androzoo_path, 'latest.csv')
#    with open(file_path, 'rb') as f_in:
#        with open(csv_fpath, 'wb') as f_out:
#            shutil.copyfileobj(f_in, f_out)
    with open(csv_fpath) as f:
        reader = csv.reader(f)
        ret_pkg_list = [row for row in reader]
    return ret_pkg_list

def is_on_androzoo(pkg_name, andro_pkg_list):
    if pkg_name not in andro_pkg_list:
        return False
    return True

def is_on_fdroid(pkg_name, fd_pkg_list):
    for row in fd_pkg_list:
        if pkg_name == row[5]:
            return True
    return False

def retrieve_latest_uploaded():
    global LAST_DATE, CURR_DATE, mainHttp, unscoped, PARENT_PATH
    time_slot = LAST_DATE + '..' + CURR_DATE
    website = mainHttp + time_slot + unscoped + time_slot
    ## download repo starts
    ## create new folder to store downloaded repos
    git_repo_path = os.path.join(PARENT_PATH, 'Github')
    if not os.path.isdir(git_repo_path):
        os.mkdir(git_repo_path)
    web_url_list = gh_download.github_url_retrieve(website, git_repo_path)
    LAST_DATE = CURR_DATE
    return web_url_list

def retrieve_fdroid():
    global PARENT_PATH
    fdroid_path = os.path.join(PARENT_PATH, 'FDroid')
    if not os.path.isdir(fdroid_path):
        os.mkdir(fdroid_path)
    fdroid_site_list = repo_source_site_fdroid.extract_source_site(fdroid_path)
    fdroid_pkg_list = appid_on_fdroid.extract_pkg_info(fdroid_path)
    return fdroid_site_list, fdroid_pkg_list

def update_checked_sites(untracked_list):
    checked_site_path = os.path.join('./', 'checked_git_urls.txt')
    untracked_str = ''
    for item in untracked_list:
        untracked_str += item + '\n'
    with open(checked_site_path, 'a+') as f:
        f.write(untracked_str)

def get_checked_sites():
    checked_git_list = []
    checked_site_path = os.path.join('./', 'checked_git_urls.txt')
    with open(checked_site_path) as f:
        for line in f:
            row = line.strip()
            if row not in checked_git_list:
                checked_git_list.append(row)
    return checked_git_list

def get_untracked_urls(fdroid_url_list):
    ### get already tracked urls
    checked_urls = get_checked_sites()
    ### get the latest uploaded urls
    gh_url_list = retrieve_latest_uploaded()
    down_url_list = []
    for item in gh_url_list:
        if item not in down_url_list and item not in checked_urls:
            down_url_list.append(item)
    for item in fdroid_url_list:
        if item.startswith('https://github.com') and item not in down_url_list and item not in checked_urls:
            down_url_list.append(item)
    return down_url_list

def check_google_fdroid(androzoo_pkg_list, fd_pkg_list):
    global PARENT_PATH
    final_github_repo_rows = []
    ### read csv file and check if the app is on Google and FDroid
    ### this will update the new genereated csv file
    ### ADD three attributes on_gooleplay on_androzoo on_fdroid
    github_repo_path = os.path.join(PARENT_PATH, 'Github', 'github_repo.csv')

    print(github_repo_path)
    git_rows = []
    with open(github_repo_path) as f:
        reader = csv.reader(f)
        git_rows = [row for row in reader]
    ### check if the App is on Google Play
    for row in git_rows:
        pkg_name = row[11]
        print(pkg_name)
        print(row)
        on_google = 'Yes' if retrieve_meta_review.metaRevRetrieve(pkg_name, PARENT_PATH) else 'No'
        on_androzoo = 'Yes' if is_on_androzoo(pkg_name, androzoo_pkg_list) else 'No'
        on_fdroid = 'Yes' if is_on_fdroid(pkg_name, fd_pkg_list) else 'No'
        curr_row = row[:12]
        curr_row.extend([on_google, on_androzoo, on_fdroid])
        curr_row.extend(row[12:])
        final_github_repo_rows.append(curr_row)

    final_github_repo_path = os.path.join(PARENT_PATH, 'final_github_repo.csv')
    with open(final_github_repo_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(final_github_repo_rows)

def update():
    global PARENT_PATH
    fd_sites, fd_pkgs = retrieve_fdroid()
    androzoo_pkgs = pkg_on_androzoo()
    down_url_list = get_untracked_urls(fd_sites)
    repo_download_path = os.path.join(PARENT_PATH, 'Github')
    gh_download.github_repo_download(down_url_list, repo_download_path)
    check_google_fdroid(androzoo_pkgs, fd_pkgs)
    update_checked_sites(down_url_list)

def timer_handler():
    global timer, TIME_INTERVAL
    CURR_DATE = date.today().isoformat()
    if not os.path.isdir(os.path.join(os.getcwd(), CURR_DATE)):
        os.mkdir(CURR_DATE)
    PARENT_PATH = os.path.join(os.getcwd(), CURR_DATE)
    update()
    timer = threading.Timer(TIME_INTERVAL, timer_handler)
    timer.start()

if __name__ == '__main__':
    ### create new folder to store current updates
    timer_handler()
