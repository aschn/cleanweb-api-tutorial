# cleanweb-api-tutorial
Talk about APIs for the Berkeley Cleanweb working group.

THe ipython notebook walks through building an API client like the GitHub client in ```github_client.py```.

## Set up

```
# clone this repo and enter the directory
cd cleanweb-api-tutorial

# make a python virtual environment
mkvirtualenv cleanweb-api-tutorial

# install the requirements
pip install -r requirements.txt

# set up environment variables for your GitHub credentials
export GITHUB_USERNAME=[yourname]
export GITHUB_PASSWORD=[yourpw]

# start the ipython notebook
ipython notebook
```