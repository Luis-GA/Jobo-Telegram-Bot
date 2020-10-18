# Jobo-Telegram-Bot

This is a Telegram Bot to monitor events of [JOBO](https://www.madridcultura.es/jobo)

[![Watch the demo](https://raw.githubusercontent.com/Luis-GA/Jobo-Telegram-Bot/master/images/telegram.png)](https://telegram.me/avisojobot)

## Features
    - Subscribe to the monitoring stream to be alerted of new events
    - Unsubscribe
    - Get the current events available in the platform

## Architecture

The architecture is based in three components:
- MongoDB as a DB
- Docker container as the Telegram Bot
- JOBO as the Online Ticket sales

![Watch the demo](https://raw.githubusercontent.com/Luis-GA/Jobo-Telegram-Bot/master/images/diagram.png)

The Docker container is a Python-slim image called [luisupm/jobo](https://hub.docker.com/repository/docker/luisupm/jobo).
It is divided in three modules:
- Telegram Bot that manages the IO of the Telegram interface.
- NEAS (New Events Alarm System) that monitors the new events in the Jobo Website.
- Scraper that is in charge to translate from the HTML events webpage to a simple data-structure to be managed.


## Demo
[![Watch the demo](https://raw.githubusercontent.com/Luis-GA/Jobo-Telegram-Bot/master/images/demo.gif)](https://www.youtube.com/watch?v=sFIftHo5CL8)

## How to run

### Pre-requirements

- [Docker installed](https://docs.docker.com/get-docker/)
- [Telegram Bot Token](https://core.telegram.org/bots)
- [Jobo account](https://form.jotformeu.com/72793534290361?_ga=2.175108578.1312958825.1518707411-409130683.1504078903)
- [Atlas MongoDB account](https://www.mongodb.com/cloud/atlas)

### Run 

Write in the console:
```console
foo@bar:~$ docker run --restart always -e MONGODB=<Altas Connection String> -e JOBO_USER=<Registered Email> -e JOBO_PASSWORD=<Registered Password> -e TOKEN=<Telegram Bot Token> luisupm/jobo
```





