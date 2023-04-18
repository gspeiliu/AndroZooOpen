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
last_ts = '2014-01-01'

# https://github.com/
GIT_LEN = 19

git_https_headers = {'Authorization': 'token ' + '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'}

out_dir = '/data/pei/CICD/Git/Android/2014-2016'


options = Options()
options.add_argument('--no-sandbox')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")

def gh_downloads(website, out_name):
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    driver = webdriver.Chrome(chromedriver, options=options)
    wait = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)

    driver.get(website)
    while True:
        try:
            # more_button = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ajax-pagination-btn btn'))).click()
            time.sleep(10)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ajax-pagination-btn')))
            driver.implicitly_wait(10) # seconds
            eles = driver.find_elements_by_css_selector('button.ajax-pagination-btn')
            if len(eles) == 0:
                break
            driver.find_elements_by_css_selector('button.ajax-pagination-btn.btn.btn-outline.color-border-default.f6.mt-0.width-full')[0].click()
            print('Execute click')
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
    for result in driver.find_elements_by_css_selector('a.text-bold.wb-break-word'):
        website = result.get_attribute("href")
        if website != '':
            web_urls_str = web_urls_str + website + '\n'
            web_url_list.append(website)

    driver.quit()

    print(len(web_url_list))
    download_urls = os.path.join(out_dir, 'download_urls_{}.txt'.format(out_name))

    with open(download_urls, 'a+') as f:
        f.write('\n'.join(web_url_list))

if __name__ == '__main__':
#    time_slot = last_ts + '..' + curr_ts
    for year in range(2014, 2016):
        for month in range(1, 13):
            for day in range(1, 29, 3):
                curr_ts = str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2)
                time_slot = last_ts + '..' + curr_ts
                if last_ts == curr_ts:
                    continue
                web = mainHttp + time_slot + unscoped + time_slot
                out_dir_name = curr_ts
                print(web)
                last_ts = curr_ts
                gh_downloads(web, curr_ts)
#    download_with_url_lst(download_urls)
