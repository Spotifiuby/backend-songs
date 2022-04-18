[![codecov](https://codecov.io/gh/Spotifiuby/backend-songs/branch/main/graph/badge.svg?token=HQVLP3H2XY)](https://codecov.io/gh/Spotifiuby/backend-songs)

# Table of Contents
* [Setup](#setup)
* [Environment Variables](#environment-variables)
* [Tests](#tests)
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

# Docs
To read the interactive docs go to:\
http://127.0.0.1:8000/docs