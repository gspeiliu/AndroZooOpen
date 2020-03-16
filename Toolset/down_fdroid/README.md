### Get package names and repo url from F-Droid
---

* Clone fdroiddata: git clone git@gitlab.com:fdroid/fdroiddata.git
* Extract repo url from yml files under folder metadata
    ```
        find ./ -name \*.yml | xargs grep -E "SourceCode|WebSite" > temp_url.txt
        cat temp_url.txt | awk '{print $2}' > fdroid_url.txt
    ```
* Download all of the repos from Github using code under folder down\_repo
* Extract all of package names from FDroid official site ```python get_appid_fdroid.py```
