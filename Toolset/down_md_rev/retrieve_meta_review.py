from Naked.toolshed.shell import *
import json
import sys
import demjson
import re


import os
import time
import requests

import elementpath
from xml.etree import ElementTree as ET

pkgNameFile = "./PackageNames.txt"
storeReview = "./Reviews/"
storeMetadata = "./Metadata/"

def metaRevDirCreate(parent_path):
    meta_path = os.path.join(parent_path, 'Metadata')
    rev_path = os.path.join(parent_path, 'Reviews')
    if not os.path.isdir(meta_path):
        os.mkdir(meta_path)
    if not os.path.isdir(rev_path):
        os.mkdir(rev_path)

# packageList = ["com.lifeway.csbible2"]  #For debuging
# print(packageList)
# Run the review and metadata javascript file
def metaRevRetrieve(p, parent_path):
    hasMDRV = False
    # Run getMetaData.js
    metadata = 'node getMetadata.js ' + p
    noAPK = False
    metadataResult = ""
    reviewResult = ""
    try:
        response = muterun(metadata)
        if response.exitcode == 0:
            metadataResult = response.stdout
            testError = metadataResult.decode('utf-8')
            if testError.startswith('Error'):
                print("Fail to get metadata " + p + ". " + testError.split('\n')[0])
                noAPK = True
            else:
                print("Succcessfully get metadata " + p)
        else:
            print("Fail get metadata " + p + ". Exitcode: " + str(response.exitcode))
            noAPK = True
    except:
        standard_err = response.stderr
        exit_code = response.exitcode
        print('Exit Status ' + str(exit_code) + ': ' + standard_err)
 
    if noAPK == False:
        # Run getReview.js
        review = 'node getReview.js ' + p
        try:
            response = muterun(review)
            if response.exitcode == 0:
                reviewResult = response.stdout
                testError = reviewResult.decode('utf-8')
                if testError.startswith('Error'):
                    print('Fail to get reviews ' + p + '. ' + testError.split('\n')[0])
                else:
                    print("Succcessfully get review " + p)
            else:
                print("Fail get review" + p)
                noAPK = True
        except:
            print('Exit Status ' + str(response.exitcode) + ': ' + response.stderr)
 
    # Write output
    if noAPK == False:
        metadataOutput = metadataResult.decode('utf-8')
 
        reviewOutput = reviewResult.decode('utf-8')    
 
        # metadataOutput = demjson.decode(metadataOutput)
        # metadataOutput["description"] = metadataOutput["description"].replace("\n", '')
        metadataOutput = json.loads(metadataOutput)
        metadataJSON = json.dumps(metadataOutput, default=lambda x: None, indent=2, ensure_ascii=False)
    
        # reviewOutput = demjson.decode(reviewOutput)
        reviewOutput = json.loads(reviewOutput)
        reviewJSON = json.dumps(reviewOutput, default=lambda x: None, indent=2, ensure_ascii=False)
 
        metaRevDirCreate(parent_path)
        writeMetadataFile = os.path.join(parent_path, 'Metadata', p + "-Metadata.json")
        writeReviewFile = os.path.join(parent_path, 'Reviews', p + "-Review.json")

        try:
            with open(writeMetadataFile, 'w') as f:
                f.write(metadataJSON)
 
            with open(writeReviewFile, 'w') as f:
                f.write(reviewJSON)
            hasMDRV = True
        except Exception as e:
            print(e)
            print("Fail to write to output.")
    return hasMDRV

def getMetaRev(parent_path):
    packageList = []
    appOnGoogle = 0
    with open(pkgNameFile) as f:
        for raw_line in f:
            line = raw_line.strip()
            if line not in packageList:
                packageList.append(line)
    total = len(packageList)
    print("Successfully get total %d package names" % total)
    for idx, pkgName in enumerate(packageList):
        print("Processing " + str(idx) + "/" + str(total))
        onGoogle = metaRevRetrieve(pkgName, parent_path)
        if onGoogle:
            appOnGoogle += 1
    print('the number of App on Google Play is:', appOnGoogle)


if __name__ == '__main__':
    parent_path = './'
    getMetaRev(parent_path)
    print("-------------All Done-----------------")
