### Download Github repositories and get basic attributes
----
* Just by executing ```python gh_download.py``` to down repositories from Github under topic **android**.
* **Notice**
1. Execute the python script with python 3+.
2. The code downloads topic android from date **2020-02-01** to **2020-03-01**.
3. In order to avoid the access limit from github, I added anthorization token generated from github. Replace the token in the variable ```git_https_headers``` with your proprietary token.
4. The code uses **[chromedriver](https://chromedriver.chromium.org/)** to get the repository list. Replace the chromedriver location in the variable ```chromedriver```. 
