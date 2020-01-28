# Incorpbot

## Prerequisites

* Docker
* Docker Compose

## Installation

These steps need to only be done once:

1. First clone the repository:

        git clone git@github.com:mauidude/w210-incorpbot
        cd w210-incorpbot


2. Run setup to create Elasticsearch index and load documents:

        docker-compose up setup

**Note** you will need to rebuild your docker container if any changes are made to the files. Do this by running the following:

```bash
docker-compose build
```

## Running

To run Incorpbot after you've successfully installed it, simply run the following command:

```bash
docker-compose run query
```

You can now ask questions once you see the prompt to enter your question.

## Contributing

If you are adding a new third-party dependency, you will need to do run `pip freeze > requirements.txt` and check that change in with your code changes to ensure others have that dependency installed when running incorpbot.
