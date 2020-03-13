import os
import wget
import subprocess
import csv

import requests
from bs4 import BeautifulSoup

import git

from subprocess import Popen, PIPE

import time

from os import path

import elementpath
from xml.etree import ElementTree as ET

from git_clone import git_clone

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from zipfile import ZipFile

chromedriver = '/home/peiliu/chromedriver'

archiveMaster = '/archive/master.zip'

mainHttp = 'https://github.com/topics/android?q=stars%3A'
keyAction = '+created%3A'
unscoped = '&unscoped_q=stars%3A'

downpath = "/"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

webListFile = './webLinkList100+.txt'

cnt = 0
packageNames = ''

def getEmailAddress(fpath, email_list):
    addresses = ''
    for line in email_list:
        spos = line.find('<')
        address = line[spos + 1:-1]
        if 'noreply' in line:
            continue
        addresses = addresses + address + "\n"
    with open(fpath, 'a+') as f:
        f.write(addresses)

def getConcretNum(html, key):
    pos = html.find(key)
    partial = html[pos - 20:pos]
    last_close = partial.find('>')
    next_start = partial.find('<')
    num = partial[last_close + 1: next_start]
    return num


def getBasicInfo(folder_name):
    ret_str = ''
    entry = folder_name.replace('#', '/')
    url = 'https://gitlab.com/' + entry
    html_str = requests.get(url).text
    soup = BeautifulSoup(html_str, 'lxml')
    star_num = soup.select('a[class="count"]')[0].string[:-1]
    commit_num = getConcretNum(html_str, 'Commits')
    branch_num = getConcretNum(html_str, 'Branch')
    tag_num = getConcretNum(html_str, 'Tags')
    # get create and last activity time
    time_entry = folder_name.replace('#', '%2F')
    time_url = 'https://gitlab.com/api/v4/projects/' + time_entry
    ret_json = requests.get(time_url).json()
    create_at = ret_json['created_at']
    last_activity = ret_json['last_activity_at']
    ret += commit_num + '\t' + branch_num + '\t' + tag_num + '\t' + star_num + '\t' + create_at + '\t' + last_activity
    return ret

                                        

def isAndroidApp(folder_name):
    hasPkgName = False
    filefolder = folder_name
    global packageNames, cnt
    try:
        print("trying to change directory:" + filefolder)
        os.chdir(filefolder)
    except Exception as e:
        print('Exception occur')
        print(filefolder)
        print(e)
        return False
    findRes = os.popen("find ./ -name AndroidManifest.xml -print0 | xargs -0 grep '\<activity>' | awk '$1 !~/(examples|benchmarks|tests)/'").read()
    if len(findRes) != 0:
        xmlPathList = os.popen("find ./ -type f -name AndroidManifest.xml").readlines()

        for xmlPath in xmlPathList:
            if len(xmlPath) == 0:
                continue
            tree = None
            try:
                tree = ET.parse(xmlPath[:-1])
            except Exception as e:
                print(e)
                continue
            root = tree.getroot()
            if 'package' not in root.attrib:
                continue
            packageName = root.attrib['package']
            if packageName != '':
                hasPkgName = True
                test_exist = 'No'
                hasKotlin = 'Yes'
                java_test = os.popen("find ./ -name \*Test.java -print0 | xargs -0 grep 'package' | awk '$1 !~/(ExampleUnitTest.java)/'").readlines()
                kt_test = os.popen("find ./ -name \*Test.kt -print0 | xargs -0 grep 'package' | awk '$1 !~/(ExampleUnitTest.kt)/'").readlines()
                has_kotlin = os.popen('find ./ -name \*.kt').readlines()
                if len(has_kotlin) == 0:
                    hasKotlin = 'No'
                else:
                    hasKotlin = 'Yes'
                if len(java_test) == 0 and len(kt_test) == 0:
                    test_exist = 'No'
                else:
                    test_exist = 'Yes'
#                 email_path = "../Emails/" + filefolder + "-mail.txt"
# #                email_list = os.popen('git shortlog -sen').readlines()
#                 email_list = []
#                 with Popen(["/usr/bin/git", "shortlog", "-sen"], stdout=PIPE, stderr=PIPE) as p:
#                     output, errors = p.communicate()
#                     email_list = output.decode('utf-8', errors='ignore').splitlines()
                # getEmailAddress(email_path, email_list)
                # basicInfo = getBasicInfo(folder_name)
                ret_list = getRepoInfo(folder_name)
                basicInfo = ''
                mail_list = None
                for it, val in enumerate(ret_list):
                    if it == (len(ret_list - 1)):
                        mail_list = val
                    basicInfo += str(val) + '\t'

                packageNames = packageNames + filefolder + '\t' + basicInfo + packageName + '\t' + test_exist + '\t' + hasKotlin + '\n'
                cnt += 1
                if cnt == 100:
                    fpath = "../PackageNames.txt"
                    with open(fpath, 'a+') as f:
                        f.write(packageNames)
                    cnt = 0
                    packageNames = ''
                break
        os.chdir("../")
        if not hasPkgName:
            with open("./NoPkgNames.txt", "a+") as f:
                f.write(filefolder + "\n")
        return True
    os.chdir("../")
    return False

def get_clone_command(website):
    ret_cmd = ''
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    driver = webdriver.Chrome(chromedriver, options=options)
    try:
        wait = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)
        driver.get(website)
        more_button = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'css-shc4i4')))
        driver.find_elements_by_css_selector('button.css-shc4i4')[0].click()
        input_list = driver.find_elements_by_css_selector('input.css-1rmy9fa')
        for item in input_list:
            cmd = item.get_attribute("value")
            if cmd != '':
                ret_cmd = cmd
    except Exception as e:
        print(e)
    return ret_cmd

def gh_downloads(website):
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
    webStr = ''
    webLists = []
    for result in driver.find_elements_by_css_selector('a.text-bold'):
        website = result.get_attribute("href")
        if website != '':
            webStr = webStr + website + '\n'
            webLists.append(website)

    driver.quit()

    print(len(webLists))

    with open(webListFile, 'a+') as f:
        f.write(webStr)
    # len(webLists)
    for url in webLists:
        rslashpos = url.rfind('/')
        repo_name = url[19:]
        folder_name = url[19:].replace('/', '#')

        if path.exists(folder_name):
            continue
        try:
             git_path = 'git@github.com:' + repo_name + '.git'
             folder_path = './' + folder_name
             new_repo = git.Repo.clone_from(url=git_path, to_path=folder_path)
             print(new_repo)
        except Exception as e:
            print(url)
            print(e)
        else:
            isAndroid = isAndroidApp(folder_name)
            removeFolder = "rm -rf " + folder_name
            rmv = 'rsync --delete-before -d ./delete/ ./' + folder_name
            if not isAndroid:
                print(removeFolder)
                rmv_str = os.popen(rmv).read()
                removeStr = os.popen(removeFolder).read()

def git_clone(item_list):
    for item in item_list:
        folder_name = item.replace('/', '#')

        if path.exists(folder_name):
            continue
        try:
             git_path = 'git@github.com:' + item + '.git'
             folder_path = './' + folder_name
             new_repo = git.Repo.clone_from(url=git_path, to_path=folder_path)
             print(new_repo)
        except Exception as e:
            print(url)
            print(e)
        else:
            isAndroid = isAndroidApp(folder_name)
            removeFolder = "rm -rf " + folder_name
            rmv = 'rsync --delete-before -d ./delete/ ./' + folder_name
            if not isAndroid:
                print(removeFolder)
                rmv_str = os.popen(rmv).read()
                removeStr = os.popen(removeFolder).read()



def getOnePageItems(page_url):
    html_str = requests.get(page_url).text
    soup = BeautifulSoup(html_str, 'html.parser')
    item_list = []
    a_list = soup.select('a[class="repo-link"]')
    for item in a_list:
        print(item.get('href')[1:])
        item_list.append(item.get('href')[1:])
    return item_list

# get all of the basic info about the repo
def getCommitInfo(commit_url):
    reg_mail = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    total_num = 0
    total_email = []
    commit_json = requests.get(commit_url).json()
    total_num += len(commit_json['values'])
    for item in commit_json['values']:
        raw_info = item['author']['raw']
        start_pos = raw_info.find('<')
        end_pos = raw_info.find('>')
        if start_pos < 0 or end_pos < 0:
            continue
        mail_address = raw_info[start_pos + 1 : end_pos]
        if re.match(reg_mail, mail_address):
            commit_email.append(mail_address)
    if 'next' in commit_json:
        next_num, next_mail = getCommitsEmails(commit_json['next'])
        total_num += next_num
        total_email.extend(next_mail)
    return total_num, total_email

def getAttrNum(attr_url):
    attr_json = requests.get(attr_url).json()
    total_num = 0
    total_num += len(attr_json['values'])
    if 'next' in attr_json:
        next_num = getAttrNum(attr_json['next'])
        total_num += next_num
    return total_num

def getRepoInfo(folder_name):
    base_url = 'https://api.bitbucket.org/2.0/repositories/'
    ret_list = []
    req_url = base_url + folder_name
    res_json = requests.get(req_url).json()
    create_on = res_json['created_on']
    update_on = res_json['updated_on']
    ## try to get the number of watchers, tags, branches, and commits, emails.
    branch_num = getAttrNum(res_json['links']['branches']['href'])
    tag_num = getAttrNum(res_json['links']['tags']['href'])
    watch_num = getAttrNum(res_json['links']['watchers']['href'])
    commit_num, commit_mail = getCommitInfo(res_json['links']['commits']['href'])
    ret_list.append(create_on)
    ret_list.append(update_on)
    ret_list.append(branch_num)
    ret_list.append(tag_num)
    ret_list.append(watch_num)
    ret_list.append(commit_num)
    ret_list.append(commit_mail)
    return ret_list



def repo_download():
    csv_line_list = []
    with open('./item_list.csv') as f:
        reader = csv.reader(f)
        csv_line_list = [row for row in reader]
    for csv_line in csv_line_list:
        web_url = csv_line[0]
        folder_name = csv_line[1].replace('/', '#')
        # try to download
        try:
            download_cmd = web_url + " " + folder_name
            ret = os.popen(download_cmd).read()
        except Exception as e:
            print(e)
            continue
        isAndroid = isAndroidApp(folder_name)
        removeFolder = "rm -rf " + folder_name
        rmv = 'rsync --delete-before -d ./delete/ ./' + folder_name
        if not isAndroid:
            print(removeFolder)
            rmv_str = os.popen(rmv).read()
            removeStr = os.popen(removeFolder).read()
    global packageNames
    if packageNames != '':
        fpath = "./PackageNames.txt"
        with open(fpath, 'a+') as f:
            f.write(packageNames)

def getAllItems():
    all_item = []
#    first_page_url = 'https://gitlab.com/search?utf8=%E2%9C%93&snippets=&scope=&repository_ref=&search=android'
#    all_item.extend(getOnePageItems(first_page_url))
    page_front = 'https://bitbucket.org/repo/all/'
    page_tail = '?name=android'
    # whole page 2496
    for page_num in range(1, 2496, 1):
        page_url = page_front + str(page_num) + page_tail
        all_item.extend(getOnePageItems(page_url))
    return all_item

def item2csv():
    all_item = getAllItems()
    to_csv = []
    base_url = 'https://bitbucket.org/'
    for item in all_item:
        line_list = []
        clone_cmd = get_clone_command(base_url + item)
        if clone_cmd == '':
            continue
        line_list.append(clone_cmd)
        line_list.append(item)
        print(line_list)
        to_csv.append(line_list)
    with open('./item_list.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(to_csv)



if __name__ == '__main__':
    if not os.path.isfile('./item_list.csv'):
        item2csv()
    repo_download()

