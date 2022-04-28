[![codecov](https://codecov.io/gh/Spotifiuby/backend-songs/branch/main/graph/badge.svg?token=HQVLP3H2XY)](https://codecov.io/gh/Spotifiuby/backend-songs) ![codecov](https://github.com/Spotifiuby/backend-songs/workflows/Spotifiuby%20CI/badge.svg)

# Table of Contents
* [Setup](#setup)
* [Environment Variables](#environment-variables)
* [Tests](#tests)
* [Deploy](#deploy)
* [Docs](#docs)

# Setup
First, create a new python environment.
```
$ python3 -m venv venv
$ source ./venv/bin/activate
```

Now install all the requirements.
```
$ pip install -r requirements.txt
```

Finally, run the app.
```
$ uvicorn main:app --reload
```

If during development you add any dependency, remember to run:
```
pip freeze > requirements.txt
```

# Environment Variables
Create the `.env` file in the root folder of the project.\
It must contain the following environment variables.

Development environment:
```
CURRENT_ENVIRONMENT=development
```

Production environment:
```
MONGODB_USER={Mongo username}
MONGODB_PASSWD={Mongo password}
GOOGLE_APPLICATION_CREDENTIALS={Path to Google Credentials}
CURRENT_ENVIRONMENT=production
```

# Tests
For tests and coverage run the following.
```
coverage run -m pytest
coverage report
```

# Deploy
## Setup
Create heroku remote.
```
heroku git:remote -a spotifiuby-backend-songs
```

## Manual Deploy
After any change, run.
```
git push heroku main
```

And get the server url with
```
heroku info
```

## SSH
Use Heroku Exec to connect to a dyno.
```
heroku ps:exec
```

Or
```
heroku ps:exec --dyno=web.2
```

# Docs
To read the interactive docs go to:\
http://127.0.0.1:8000/docs
