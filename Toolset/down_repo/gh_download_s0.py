import os
import csv
import wget
import subprocess

import time

from os import path

import git

from subprocess import Popen, PIPE

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

chromedriver = '~/chromedriver'

archiveMaster = '/archive/master.zip'

## Topis android embodied here with topics/android
mainHttp = 'https://github.com/topics/android?q=stars%3A'
keyAction = '+created%3A'
unscoped = '&unscoped_q=stars%3A'

downpath = "/"

options = Options()
options.add_argument('--no-sandbox')

webListFile = './webLinkListS0.txt'

TOTAL_MONTH = 12

def check_has_kotlin(folder_name):
    has_kotlin = 'No'
    kt_list = os.popen('find ./ -name \*.kt').readlines()
    if kt_list:
        has_kotlin = 'Yes'
    return has_kotlin

def check_has_test(folder_name):
    has_test = 'Yes'
    java_test = os.popen("find ./ -name \*Test.java -print0 | xargs -0 grep 'package' | awk '$1 !~/(ExampleUnitTest)/'").readlines()
    kt_test = os.popen("find ./ -name \*Test.kt -print0 | xargs -0 grep 'package' | awk '$1 !~/(ExampleUnitTest)/'").readlines()
    if not java_test and not kt_test:
        has_test = 'No'
    return has_test

def extract_email_address(folder_name):
    email_list_str = ''
    raw_email_list = []
    email_list = []
    with Popen(["/usr/bin/git", "shortlog", "-sen"], stdout=PIPE, stderr=PIPE) as p:
        output, errors = p.communicate()
        raw_email_list = output.decode('utf-8', errors='ignore').splitlines()
    for line in raw_email_list:
        spos = line.find('<')
        address = line[spos + 1:-1]
        if 'noreply' in line:
            continue
        if address not in email_list:
            email_list.append(address)
            email_list_str += address + ','
    return email_list_str[:-1]

def extractPackageName(folder, xmlPathList):
    print(xmlPathList)
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
        print(packageName)
        if packageName != '':
            has_test = check_has_kotlin(folder)
            has_kotlin = check_has_kotlin(folder)
            email_address = extract_email_address(folder)
            curr_list = [folder, packageName, has_test, has_kotlin, email_address]
            with open("../PackgeNames.csv", 'a+') as f:
                writer = csv.write(f)
                writer.writerow(curr_list)
            break

def isAndroidApp(filename):
    filefolder = filename
    try:
        os.chdir(filefolder)
    except Exception as e:
        print('Exception occur')
        print(filefolder)
        print(e)
        return False
    findRes = os.popen("find ./ -name AndroidManifest.xml -print0 | xargs -0 grep '\<activity>' | awk '$1 !~/(examples|benchmarks|tests)/'").readlines()
    if len(findRes) != 0:
        xmlPathList = os.popen("find ./ -name AndroidManifest.xml").readlines()
        extractPackageName(filefolder, xmlPathList)
        os.chdir("../")
        return True
    os.chdir("../")
    return False


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
        repo_name = url[19:]
        folder_name = url[19:].replace('/', '#')

        if path.exists(folder_name):
            continue
        try:
            git_path = 'git@github.com:' + repo_name + '.git'
            folder_path = './' + folder_name
            new_repo = git.Repo.clone_from(url=git_path, to_path=folder_path)
        except Exception as e:
            print(url)
            print(e)
        if path.exists(folder_name):
            isAndroid = isAndroidApp(folder_name)
            removeFolder = "rm -rf " + folder_name
            if not isAndroid:
                print(removeFolder)
                removeStr = os.popen(removeFolder).read()

"""
Code execute from the following for loop
Just in case, it shows how to download repos with star number ZERO
You can download any repos with arbitrary star number.
"""
monthDayLists = ['-01-01', '-02-01', '-03-01', '-04-01', '-05-01', '-06-01', '-07-01', '-08-01', '-09-01', '-10-01', '-11-01', '-12-01']
for stars in range(1):
    starsStr = str(stars)
    fullStars = starsStr + '..' + starsStr
    for year in range(2009, 2020):
        i = 0
        while i < len(monthDayLists):
            starYear = str(year)
            if i == len(monthDayLists) - 1:
                endYear = str(year + 1)
            else:
                endYear = str(year)
            time_cond = starYear + monthDayLists[i % TOTAL_MONTH] + '..' + endYear + monthDayLists[(i + 1) % TOTAL_MONTH]
            web = mainHttp + fullStars + keyAction + time_cond + unscoped + fullStars + keyAction + time_cond
            print(web)
            gh_downloads(web)
            i += 1
