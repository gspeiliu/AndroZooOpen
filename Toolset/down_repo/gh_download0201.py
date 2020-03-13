import os
import wget
import subprocess
import datetime

import csv
import time

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

from zipfile import ZipFile

chromedriver = '/home/peiliu/chromedriver'

archiveMaster = '/archive/master.zip'

mainHttp = 'https://github.com/topics/android?q=created%3A'
unscoped = '&unscoped_q=created%3A'
lastTimestamp = '2020-01-01'

downpath = "/"

options = Options()
options.add_argument('--no-sandbox')

webListFile = './webLinkListTillNow.txt'

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


def noPkgName2File(fpath, content):
        with open(fpath, 'a+') as f:
                f.write(content + "\n")

cnt = 0
packageNames = ''

def extractPackageName(folder, xmlPathList):
    print(xmlPathList)
    global cnt, packageNames
    hasPkgName = False
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
            hasPkgName = True
            hasTest = 'Yes'
            java_test = os.popen("find ./ -name \*Test.java -print0 | xargs -0 grep 'package' | awk '$1 !~/(ExampleUnitTest)/'").read()
            kt_test = os.popen("find ./ -name \*Test.kt -print0 | xargs -0 grep 'package' | awk '$1 !~/(ExampleUnitTest)/'").read()
            if len(java_test) == 0 and len(kt_test) == 0:
                hasTest = 'No'
            packageNames = packageNames + folder + '\t' + packageName + '\t' + hasTest + '\n'
            cnt = cnt + 1
            if cnt == 100:
                # write to packageNameList.txt file and rest cnt to 0
                fpath = "../PackageNames.txt"
                with open(fpath, 'a+') as f:
                    f.write(packageNames)
                cnt = 0
                packageNames = ''
            break
    if not hasPkgName:
        with open('./NoPkgNameFolder.txt', 'a+') as f:
            f.write(folder + '\n')



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
        folderName = url[rslashpos + 1:]
        userName = url[19:rslashpos]
        fullName = userName + '#' + folderName
        repo_name = url[19:]
        folder_name = url[19:].replace('/', '#')

        if path.exists(fullName):
            continue
        try:
            git_path = 'git@github.com:' + repo_name + '.git'
            folder_path = './' + folder_name
            new_repo = git.Repo.clone_from(url=git_path, to_path=folder_path)
        except Exception as e:
            print(url)
            print(e)
        else:
            isAndroid = isAndroidApp(folder_name)
            removeFolder = "rm -rf " + folder_name
            if not isAndroid:
                print(removeFolder)
                removeStr = os.popen(removeFolder).read()

def check_has_kotlin(folder_name):
    has_kotlin = 'No'
    os.chdir(folder_name)
    kt_list = os.popen('find ./ -name \*.kt').readlines()
    if kt_list:
        has_kotlin = 'Yes'
    os.chdir("../")
    return has_kotlin

def extract_email_address(folder_name):
    address_list = []
    os.chdir(folder_name)
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
        email_list.append(address)
    os.chdir("../")
    return email_list

def extract_kotlin_mail():
    csv_list = []
    with open('all_PackageNames.txt') as f:
        line_list = f.readlines()
        for line in line_list:
            curr_list = []
            row_list = line.split('\t')
            has_kotlin = check_has_kotlin(row_list[0])
            mail_list = extract_email_address(row_list[0])
            curr_list.extend(row_list[:-1])
            curr_list.append(row_list[-1][:-1])
            curr_list.append(has_kotlin)
            curr_list.append(mail_list)

            csv_list.append(curr_list)
    with open("final_package.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerows(csv_list)



if __name__ == '__main__':
    extract_kotlin_mail()
#    timeSlot = lastTimestamp + '..2020-02-01'
#    web = mainHttp + timeSlot + unscoped + timeSlot
#    gh_downloads(web)
#    # write to packageNameList.txt file and rest cnt to 0
#    fpath = "./PackageNames.txt"
#    with open(fpath, 'a+') as f:
#        f.write(packageNames)
#

