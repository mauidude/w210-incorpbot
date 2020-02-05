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

To run Incorpbot after you've successfully installed it, simply run the following command to start the web server:

```bash
docker-compose up flask app
```

You can point your browser to http://localhost:5000 to visit the site.

## Contributing

If you are adding a new third-party dependency, you will need to do run `pip freeze > requirements.txt` and check that change in with your code changes to ensure others have that dependency installed when running incorpbot.
