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
"""
Author: Chai Lam Loi
Modified Date: 2019-10-09
Description: Call javascript file to get the metadata and reciews of app. Scrap Google Play.
Reference: https://medium.com/@emily971133/google-play-store-api-with-python-755bd023de87
"""

def getAppName(output):
    name = ""
    for i in range(10,100):
        if output[i] != "'":
            name = name + str(output[i])
        else:
            name = name.replace("?",'')
            name = name.replace("/",'')
            name = name.replace("\\",'')
            name = name.replace(":",'')
            name = name.replace("*",'')
            name = name.replace('"','')
            name = name.replace("<",'')
            name = name.replace(">",'')
            name = name.replace("|",'')
            return name
    return None

def getAppNameWithTitle(output):
    name = ""
    if output[11] == '"':
        endQuotePos = output.find('"', 12)
        name = output[12: endQuotePos]
        if endQuotePos == 12:
            print("name is empty string")
    else:
        name = None
    return name


        
# readName = "C:/Users/caila/Desktop/FIT4003/knowledge-zoo-api-server/extractData/androguard-master/Information/PackageNames.txt"
# storeReview = "C:/Users/caila/Desktop/FIT4003/knowledge-zoo-api-server/extractData/androguard-master/Information/Reviews/"
# storeMetadata = "C:/Users/caila/Desktop/FIT4003/knowledge-zoo-api-server/extractData/androguard-master/Information/Metadata/"
# readName = "/home/team8/extractData/androguard-master/Information/PackageNames.txt"
# storeReview = "/home/team8/extractData/androguard-master/Information/Reviews/"
# storeMetadata = "/home/team8/extractData/androguard-master/Information/Metadata/"

readName = "./PackageNames.txt"
storeReview = "./Reviews/"
storeMetadata = "./Metadata/"

packageList = []
total = 0

# Get all the package name of the apps

readFile = open(readName,"r")
for line in readFile:
   line = line.strip("\n")
   packageList.append(line)   
readFile.close()
print("Successfully get package names")
# packageList = ["com.lifeway.csbible2"]  #For debuging
# print(packageList)
# Run the review and metadata javascript file
for p in packageList:
   print("Processing " + str(total) + "/" + str(len(packageList)))
   total += 1
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
           if testError[:5] == 'Error':
               endPos = testError.find('\n')
               print("Fail get metadata " + p + ". " + testError[:endPos])
               noAPK = True
           else:
               print("Succcessfully get metadata " + p)
       else:
           print(response.exitcode)
           print("Fail get metadata" + p)
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
               print("Succcessfully get review " + p)
           else:
               print("Fail get review" + p)
               noAPK = True
       except:
           standard_err = response.stderr
           exit_code = response.exitcode
           print('Exit Status ' + str(exit_code) + ': ' + standard_err)

   # Write output
   if noAPK == False:
       metadataOutput = metadataResult.decode('utf-8')
       metadataOutput = metadataOutput.replace("[Object]","[]")
       metadataOutput = metadataOutput.replace("\n", '')
       metadataOutput = metadataOutput.replace("...","")
       metadataOutput = metadataOutput.replace("more","")
       metadataOutput = metadataOutput.replace("items","")
       metadataOutput = metadataOutput.replace("item","")

       reviewOutput = reviewResult.decode('utf-8')
       reviewOutput = reviewOutput.replace("[Object]","[]")
       reviewOutput = reviewOutput.replace("...","")
       reviewOutput = reviewOutput.replace("more","")
       reviewOutput = reviewOutput.replace("items","")
       reviewOutput = reviewOutput.replace("item","")

       # name = getAppName(metadataOutput)
       name = getAppNameWithTitle(metadataOutput)
       # Check that review and metadata is not Type Error
       if reviewOutput[0:9] == "TypeError":
           name = None
       if metadataOutput[0:9] == "TypeError":
           name = None

       if name is not None:       

           # metadataOutput = demjson.decode(metadataOutput)
           # metadataOutput["description"] = metadataOutput["description"].replace("\n", '')
           metadataOutput = json.loads(metadataOutput)
           print(type(metadataOutput))
           print(metadataOutput.keys())
           metadataJSON = json.dumps(metadataOutput, default=lambda x: None, indent=2)
   
           # reviewOutput = demjson.decode(reviewOutput)
           reviewOutput = json.loads(reviewOutput)
           print(reviewOutput[0].keys())
           reviewJSON = json.dumps(reviewOutput, default=lambda x: None, indent=2)

           writeReview = storeReview + p + "Review.txt"
           writeMetadata = storeMetadata + p + "Metadata.txt" 


           try: 

               writeMetadataFile = open(writeMetadata,"w",encoding='utf-8')
               writeMetadataFile.write(metadataJSON)
               writeMetadataFile.close()
               print("Succcessfully write metadata " + p)

               if reviewOutput[0:9] != "TypeError":
                   writeReviewFile = open(writeReview, "w",encoding='utf-8')
                   writeReviewFile.write(reviewJSON)
                   writeReviewFile.close()
                   print("Succcessfully write review " + p)
           except Exception as e:
               print(e)
               print("Fail to write to output.")
       
       else:
           print("Could not write " + p + " as name is None (App not found on google.)")

   
print("-------------All Done-----------------")
