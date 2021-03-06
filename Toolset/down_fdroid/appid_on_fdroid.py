#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import csv
import requests
import urllib
from urllib import request
from lxml import etree
from bs4 import BeautifulSoup

def gen_page_num():
    x = 2
    while True:
        yield x
        x += 1

def extract_pkg_name(pkg_list):
    ret_list = []
    for item in pkg_list:
        r_slash = item.rfind('/')
        ret_list.append(item[r_slash + 1:])
    return ret_list

def extract_package(url):
    print(url)
    pkg_list = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    req = request.Request(url, headers = headers)
    try:
        text = request.urlopen(req).read()
    except Exception as e:
        print(e)
    else:
        soup = BeautifulSoup(text, 'lxml')
        div_list = soup.find_all("div", id="full-package-list")
        for div in div_list:
            for a_pkg in div.find_all('a', class_="package-header"):
                pkg_list.append(a_pkg.get('href'))
    return extract_pkg_name(pkg_list)

def extract_pkg_info(parent_path):
    ret_pkg_list = []
    categories = ['connectivity', 'development', 'games', 'graphics', 'internet', 'money', 'multimedia', 'navigation', 'phone-sms', 'reading', 'science-education', 'security', 'sports-health', 'system', 'theming', 'time', 'writing']
    all_pkg = []
    base_url = 'https://f-droid.org/en/categories/'
    for item in categories:
        url = base_url + item
        ret_list = extract_package(url)
        if not ret_list:
            continue
        all_pkg.extend(ret_list)
#    first_pkg_list = extract_package(base_url)
#    all_pkg.extend(first_pkg_list)
#    for page_num in gen_page_num():
#        url = base_url + str(page_num) + '/index.html'
#        ret_list = extract_package(url)
#        if not ret_list:
#            break
#        all_pkg.extend(ret_list)
    write_pkg = [pkg + '\n' for pkg in all_pkg]
    txt_file_path = os.path.join(parent_path, 'fdroid_pkg.txt')
    with open(txt_file_path, 'w') as f:
        f.writelines(write_pkg)
    for pkg_name in all_pkg:
        if pkg_name not in ret_pkg_list:
            ret_pkg_list.append(pkg_name)
    return ret_pkg_list

if __name__ == '__main__':
    extract_pkg_info('./')
