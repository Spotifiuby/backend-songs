# Table of Contents
* [Setup](#setup)
* [Environment Variables](#environment-variables)
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
GOOGLE_APPLICATION_CREDENTIALS={Path to Google Credentials}
CURRENT_ENVIRONMENT=development
```

Production environment:
```
MONGODB_USER={Mongo username}
MONGODB_PASSWD={Mongo password}
GOOGLE_APPLICATION_CREDENTIALS={Path to Google Credentials}
CURRENT_ENVIRONMENT=production
```

# Docs
To read the interactive docs go to:\
http://127.0.0.1:8000/docs