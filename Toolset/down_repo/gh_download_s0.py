import os
import wget
import subprocess

import time

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

mainHttp = 'https://github.com/topics/android?q=stars%3A'
keyAction = '+created%3A'
unscoped = '&unscoped_q=stars%3A'

downpath = "/"

options = Options()
options.add_argument('--no-sandbox')

webListFile = './webLinkListS0.txt'

# def get_field_text_if_exists(item, selector):
#     """Extracts a field by a CSS selector if exists."""
#     try:
#         return item.find_element_by_css_selector(selector).text
#     except NoSuchElementException:
#         return ""


# def get_link_if_exists(item, selector):
#     """Extracts an href attribute value by a CSS selector if exists."""
#     try:
#         return item.find_element_by_css_selector(selector).get_attribute("href")
#     except NoSuchElementException:
#         return ""


# wget the repo zip archive file
# unzip the archive
# cd into the folder
# find ./ -name *.xml | xargs grep '\<activity>'
# if there are some activity exists in some xml file
# then the repo is android app
# else the repo is not android app

def isAndroidApp(filename):
    filefolder = filename
    try:
        print("trying to change directory:" + filefolder)
        os.chdir(filefolder)
    except Exception as e:
        print('Exception occur')
        print(filefolder)
        print(e)
        return False
    findRes = os.popen("find ./ -name AndroidManifest.xml -print0 | xargs -0 grep '\<activity>' | awk '$1 !~/(examples|benchmarks|tests)/'").read()
    os.chdir("../")
    if len(findRes) != 0:
        return True
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
        rslashpos = url.rfind('/')
        folderName = url[rslashpos + 1:]
        userName = url[19:rslashpos]
        fullName = userName + '#' + folderName

        if path.exists(fullName):
            continue
        try:
            git_clone(url)
        except Exception as e:
            print(url)
            print(e)
        else:
            filefolder = os.popen("ls -lt | grep '^d' | head -1 | awk '{print $9}'").read()[:-1]
            if filefolder.find(folderName) < 0:
                print('file name not found')
                os.popen('rm -rf ' + filefolder)
                continue
            fullName = userName + '#' + filefolder
            mvCmd = 'mv ' + filefolder + ' ' + fullName
            cmdRes = os.popen(mvCmd).read()
            isAndroid = isAndroidApp(fullName)
            removeFolder = "rm -rf " + fullName
            if not isAndroid:
                print(removeFolder)
                removeStr = os.popen(removeFolder).read()

fullStars = '0..0'
timeList = ['2019-12-01..2020-01-01']

for item in timeList:
    web = mainHttp + fullStars + keyAction + item + unscoped + fullStars + keyAction + item
    gh_downloads(web)

#monthDayLists = ['-01-01', '-02-01', '-03-01', '-04-01', '-05-01', '-06-01', '-07-01', '-08-01', '-09-01', '-10-01', '-11-01', '-12-01']
#for stars in range(1):
#    starsStr = str(stars)
#    fullStars = starsStr + '..' + starsStr
#    for year in range(2017, 2020):
#        i = 0
#        yearStr = str(year)
#        if year != 2009:
#            lastYearStr = str(year - 1)
#            fullMonth = lastYearStr + monthDayLists[11] + '..' + yearStr + monthDayLists[0]
#            web = mainHttp + fullStars + keyAction + fullMonth + unscoped + fullStars + keyAction + fullMonth
#            gh_downloads(web)
#            print(web)
#        while i < len(monthDayLists) - 1:
#            fullMonth = yearStr + monthDayLists[i] + '..' + yearStr + monthDayLists[i + 1]
#            web = mainHttp + fullStars + keyAction + fullMonth + unscoped + fullStars + keyAction + fullMonth
#            print(web)
#            gh_downloads(web)
#            i += 1
#        if year == 2019:
#            nextYearStr = str(year + 1)
#            fullMonth = yearStr + monthDayLists[11] + '..' + nextYearStr + monthDayLists[0]
#            web = mainHttp + fullStars + keyAction + fullMonth + unscoped + fullStars + keyAction + fullMonth
#            gh_downloads(web)
#            print(web)
#
