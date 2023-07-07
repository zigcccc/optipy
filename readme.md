[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=zigcccc_optipy&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=zigcccc_optipy)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=zigcccc_optipy&metric=coverage)](https://sonarcloud.io/summary/new_code?id=zigcccc_optipy)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=zigcccc_optipy&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=zigcccc_optipy)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=zigcccc_optipy&metric=bugs)](https://sonarcloud.io/summary/new_code?id=zigcccc_optipy)

# Optipy

Optipy is a playground FastAPI project. It has no real meaning other than me learning how to use this framework (and dive more into BE development in general).


## Requirements
- Python version >=3.x
- PostgreSQL
- AWS LocalStack

## How to run this project locally?
- pull the code
- create new PostgreSQL DB and assign a super to it
- copy the `.env.example` file and make necessary changes
- create virtual env
  - `python -m venv env`
- active virtual env
  - `source ./env/bin/activate`
- install requirements
  - `pip install -r requirements.txt`
- run the AWS LocalStack
  - `localstack start -d`
- run the app
  - `uvicorn app:main --reload`
  - *Note: you don't need the reload flag if you don't plan to make any chagnes to the code*