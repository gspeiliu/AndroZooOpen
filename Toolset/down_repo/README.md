### Download Github repositories and get basic attributes
----
Updates:
```gh_download_websites.py``` used to download any repositories under topic **Android**

```get_android_repos.py``` used to download latest tree info (please refer to Github API v3 for the explanation of the tree)

```get_git_android_repos.py``` used to check if the project contains the special file **AndroidManifest.xml** 
<!--* Just by executing ```python gh_download.py``` to down repositories from Github under topic **android**.
* **Notice**
1. Execute the python script with python 3+.
2. The code downloads topic android from date **2020-02-01** to **2020-03-01**.
3. In order to avoid the access limit from github, I added anthorization token generated from github. Replace the token in the variable ```git_https_headers``` with your proprietary token.
4. The code uses **[chromedriver](https://chromedriver.chromium.org/)** to get the repository list. Replace the chromedriver location in the variable ```chromedriver```. 
5. The file named github_repo.csv generated under the same folder, it contains attributes of the downloaded repositories. One row for a repository. The attributes are: ```data_source	entry	num_commits	num_branches	num_packages	num_releases	num_stars	create_time	update_time	push_time	num_contributors	package_name	has_test	has_kotlin	email_address``` -->
