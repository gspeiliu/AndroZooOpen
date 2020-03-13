from Naked.toolshed.shell import *
import json
import sys
import csv
import demjson
import re


import os
import time
import requests

import elementpath
from xml.etree import ElementTree as ET

#all_folder = [d for d in os.listdir('.') if os.path.isdir(d)]

google_packages = []

git_https_headers = {'Authorization': 'token ' + 'xxxxxxxxxxxxxxxxxxxxxxx'}

def get_repo_attrib(weburl):
    attrib = ''
    attrib_list = []
    html_text = requests.get(weburl).text
    print(weburl)

    repo_root_url = 'https://github.com'
    root_len = len(repo_root_url)
    git_api_root = 'https://api.github.com/repos'
    user_plus_repo = weburl[root_len:]
    git_api_url = git_api_root + user_plus_repo

    attrib = attrib + user_plus_repo + '\t'
    pos = html_text.find(r'span class="num text-emphasized"')
    if pos < 0:
        print("Page not found")
        return attrib_list
# show data as sequence: commits branches packages releases contributors
    step = 100
    start = 0

    for i in range(4):
        pos = html_text[start:].find(r'span class="num text-emphasized"')
        content_list = html_text[start + pos: start + pos + step].split('\n')
        number = content_list[1].strip()
        attrib_name = content_list[3].strip()
        attrib = attrib + number + '\t'
        attrib_list.append(number)
        start = start + pos + step

    repo_json = requests.get(git_api_url, headers=git_https_headers).json()

    create_time = repo_json['created_at']
    update_time = repo_json['updated_at']
    push_time = repo_json['pushed_at']
    stars_num = repo_json['stargazers_count']
    # get contributors
    # sleep 2 minutes in order to avoid the access limit from github
    git_contri_api = git_api_url + '/contributors'
    contri = requests.get(git_contri_api)
    all_contri = 0
    link_text = contri.headers.get('Link')
    if link_text is not None:
        last_page = contri.headers.get('Link').split(',')[1].split(';')[0].split('<')[1].split('>')[0]
        rpos = last_page.rfind('=')
        page_num = int(last_page[rpos + 1:])
        last_page_num = len(requests.get(last_page).json())
        all_contri = last_page_num + (page_num - 1) * 30
    else:
        all_contri = len(contri.json())

    attrib = attrib + str(stars_num) + '\t' + create_time + '\t' + update_time + '\t' + push_time + '\t' + str(all_contri) + '\t'
    attrib_list.append(stars_num)
    attrib_list.append(create_time)
    attrib_list.append(update_time)
    attrib_list.append(push_time)
    attrib_list.append(all_contri)
    print(attrib)
    return attrib_list

root_url = 'https://github.com/'
csv_line = ''
csv_list = []
def gen_final_csv():
    with open('PackageNames.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            # row[0] folder name
            partial_url = row[0].replace('#','/')
            curr_list = [partial_url]
            print(partial_url)
            url = root_url + partial_url
            repo_attrib = get_repo_attrib(url)
            if not repo_attrib:
                continue
            curr_list.extend(repo_attrib)
            curr_list.extend(row[1:])
            csv_list.append(curr_list)
    with open('gen_final.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(csv_list)

if __name__ == '__main__':
    gen_final_csv()
