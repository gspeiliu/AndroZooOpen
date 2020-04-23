#!/usr/bin/env python
# -*- encoding: utf-8 -*-

''' repo_source_site_fdroid.py
This file is used to extract the source site of every App rested on fdroid.
'''

import os
import csv
import requests
import shutil
import tarfile

def extract_source_site(folder_path):
    ret_site_list = []
    url = 'https://gitlab.com/fdroid/fdroiddata/-/archive/master/fdroiddata-master.tar.gz'
    req = requests.get(url, stream=True)
    file_path = os.path.join(folder_path, 'fdroiddata-master.tar.gz')
    if req.status_code == 200:
            with open(file_path, 'wb') as fd:
                    for chunk in req.iter_content(chunk_size=1024):
                            fd.write(chunk)
    tar = tarfile.open(file_path, "r:gz")
    tar.extractall(path=folder_path)
    print(folder_path)
    ### execute shell command to get the source site
    find_cmd = 'find ' + folder_path + '/fdroiddata-master/metadata' + ' -name \*.yml | xargs grep -E "SourceCode|WebSite" > ' + folder_path + '/temp_site.txt'
    cat_cmd = 'cat ' + folder_path + "/temp_site.txt | awk '{print $2}' > " + folder_path + '/fdroid_source_site.txt'
    rm_cmd = folder_path + '/temp_site.txt'
    os.popen(find_cmd).read()
    os.popen(cat_cmd).read()
    os.remove(rm_cmd)
    source_site_fpath = os.path.join(folder_path, 'fdroid_source_site.txt')
    with open(source_site_fpath) as f:
        for line in f:
            row = line.strip()
            if row not in ret_site_list:
                ret_site_list.append(row)
    return ret_site_list

if __name__ == '__main__':
    extract_source_site('./')
