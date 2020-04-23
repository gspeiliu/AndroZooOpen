import os
import wget
import csv
import time

import requests

import subprocess
import datetime

import elementpath
from xml.etree import ElementTree as ET

from subprocess import Popen, PIPE

import git
from os import path

from git_clone import git_clone

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

chromedriver = '/home/peiliu/chromedriver'

mainHttp = 'https://github.com/topics/android?q=created%3A'
unscoped = '&unscoped_q=created%3A'
last_ts = '2020-02-01'

# https://github.com/
GIT_LEN = 19

git_https_headers = {'Authorization': 'token ' + 'b445153a8589bec2e59fc414a9245d8f2a546ee7'}

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')

def get_repo_attrib(folder_name):
    attrib_list = ['github']

    repo_entry = folder_name.replace('#', '/')
    repo_root_url = 'https://github.com/'
    git_api_root = 'https://api.github.com/repos/'
    weburl = repo_root_url + repo_entry

    attrib_list.append(repo_entry)

    html_text = requests.get(weburl).text
    print(weburl)

    git_api_url = git_api_root + repo_entry

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
        attrib_list.append(number)
        start = start + pos + step

    try:
        repo_json = requests.get(git_api_url, headers=git_https_headers).json()
    except Exception as e:
        print(e)
        return []
    create_time = repo_json['created_at']
    update_time = repo_json['updated_at']
    push_time = repo_json['pushed_at']
    stars_num = repo_json['stargazers_count']
    # get contributors
    # sleep 2 minutes in order to avoid the access limit from github
    git_contri_api = git_api_url + 'contributors'
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

    attrib_list.append(stars_num)
    attrib_list.append(create_time)
    attrib_list.append(update_time)
    attrib_list.append(push_time)
    attrib_list.append(all_contri)

    return attrib_list

def is_android_app(folder_name, parent_path):
    try:
        curr_path = os.getcwd()
        folder_path = os.path.join(parent_path, folder_name)
        os.chdir(folder_path)
    except Exception as e:
        print('Exception occur')
        print(folder_name)
        print(e)
        return False
    find_res = os.popen("find ./ -name AndroidManifest.xml -print0 | xargs -0 grep '\<activity>' | awk '$1 !~/(examples|benchmarks|tests)/'").readlines()
    if len(find_res) != 0:
        xml_path_list = os.popen("find ./ -name AndroidManifest.xml").readlines()
        extract_info_list = extract_repo_detail(xml_path_list)
        repo_attrib = get_repo_attrib(folder_name)
        if not repo_attrib:
            os.chdir(curr_path)
            return False, []
        repo_attrib.extend(extract_info_list)
        print(repo_attrib)
        os.chdir(curr_path)
        return True, repo_attrib
    os.chdir(curr_path)
    return False, []

def is_kotlin_exist():
    has_kotlin = 'No'
    kt_list = os.popen('find ./ -name \*.kt').readlines()
    if kt_list:
        has_kotlin = 'Yes'
    return has_kotlin

def is_test_exist():
    has_test = 'No'
    java_list = os.popen("find ./ -name \*Test.java -print0 | xargs -0 grep 'package' | awk '$1 !~/(ExampleUnitTest)/'").readlines()
    kt_list = os.popen("find ./ -name \*Test.kt -print0 | xargs -0 grep 'package' | awk '$1 !~/(ExampleUnitTest)/'").readlines()
    if java_list or kt_list:
        has_test = 'Yes'
    return has_test

def extract_email_address():
    raw_email_list = []
    email_address_list = []
    email_address_str = ''
    with Popen(["/usr/bin/git", "shortlog", "-sen"], stdout=PIPE, stderr=PIPE) as p:
        output, errors = p.communicate()
        raw_email_list = output.decode('utf-8', errors='ignore').splitlines()
    for line in raw_email_list:
        spos = line.find('<')
        address = line[spos + 1:-1]
        if 'noreply' in line:
            continue
        if address in email_address_list:
            continue
        email_address_list.append(address)
        email_address_str += address + ','
    if email_address_str:
        return email_address_str[:-1]
    else:
        return email_address_str

def extract_repo_detail(xml_path_list):
    print(xml_path_list)
    curr_detail_list = []
    has_pkg_name = False
    for xml_path in xml_path_list:
        if len(xml_path) == 0:
            continue
        tree = None
        try:
            tree = ET.parse(xml_path[:-1])  ### get rid of the last char '\n'
        except Exception as e:
            print(e)
            continue
        root = tree.getroot()
        if 'package' not in root.attrib:
            continue
        pkg_name = root.attrib['package']
        print(pkg_name)
        if pkg_name != '':
            has_pkg_name = True
            has_test = is_test_exist()
            has_kotlin = is_kotlin_exist()
            curr_detail_list = [pkg_name, has_test, has_kotlin]
            break
    if has_pkg_name:
        # extract email addresses
        email_address_str = extract_email_address()
        curr_detail_list.append(email_address_str)
    return curr_detail_list

def github_repo_download(web_url_list, parent_path):
    # len(web_url_list)
    for url in web_url_list:
        repo_name = url[GIT_LEN:]
        folder_name = url[GIT_LEN:].replace('/', '#')

        if path.exists(folder_name):
            continue
        try:
            git_path = 'git@github.com:' + repo_name + '.git'
            folder_path = os.path.join(parent_path, folder_name)
            new_repo = git.Repo.clone_from(url=git_path, to_path=folder_path)
        except Exception as e:
            print(url)
            print(e)
        else:
            is_android, curr_row = is_android_app(folder_name, parent_path)
            rm_folder = "rm -rf " + folder_name
            if not is_android:
                print(rm_folder)
                re_str = os.popen(rm_folder).read()
            else:
                # write to the csv file
                csv_file_path = os.path.join(parent_path, 'github_repo.csv')
                with open(csv_file_path, 'a+') as f:
                    writer = csv.writer(f)
                    writer.writerow(curr_row)

def github_url_retrieve(website, parent_path):
    print(website)
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    driver = webdriver.Chrome(chromedriver, options=options)
    wait = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)

    driver.get(website)
    while True:
        try:
            # more_button = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ajax-pagination-btn btn'))).click()
            time.sleep(5)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ajax-pagination-btn')))
            driver.implicitly_wait(5) # seconds
            eles = driver.find_elements_by_css_selector('button.ajax-pagination-btn')
            if len(eles) == 0:
                break
            driver.find_elements_by_css_selector('button.ajax-pagination-btn')[0].click()
        except StaleElementReferenceException:
            pass
        except NoSuchElementException:
            break
        except TimeoutException:
            break
    # wait for results to load
    # wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'footer')))

    # parse results
    web_urls_str = ''
    web_url_list = []
    for result in driver.find_elements_by_css_selector('a.text-bold'):
        website = result.get_attribute("href")
        if website != '':
            web_urls_str = web_urls_str + website + '\n'
            web_url_list.append(website)

    driver.quit()

    print(len(web_url_list))

    download_urls_path = os.path.join(parent_path, 'download_urls.txt')
    with open(download_urls_path, 'a+') as f:
        f.write(web_urls_str)

    return web_url_list

def github_download(new_date):
    time_slot = last_ts + '..' + new_date
    web = mainHttp + time_slot + unscoped + time_slot
    print(web)
    web_url_list = github_url_retrieve(web, './')
    github_repo_download(web_url_list, './')

if __name__ == '__main__':
    github_download('2020-03-01')
