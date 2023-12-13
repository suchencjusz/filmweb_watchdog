# NOW AS DISCORD BOT
https://discordbotlist.com/bots/filman
https://discordbotlist.com/bots/filman
https://discordbotlist.com/bots/filman





# Filmweb Watchdog
*Have you ever wanted to get notifications from filmweb to your discord server? no? now it's possible!!!*

# Features
 - Scraping data from filmweb
 - Sending notification to discord server
	 - *using this fancy **embedded** message*

	 ![image](https://github.com/suchencjusz/filmweb_watchdog/assets/34921955/5853000c-a09a-4099-9fc3-3a309f4e4fb0)

# Installation
### Docker compose (preferred option)

```
version: "3.6"

services:
  chrome:
    image: selenium/standalone-chrome:latest
    hostname: chrome
    privileged: true
    shm_size: 2g
    ports:
      - "4444:4444"
    restart: unless-stopped

  filmweb_watchdog:
    depends_on:
      - chrome
    container_name: filmweb_watchdog
    image: suchencjusz/filmweb-watchdog:latest
    volumes:
      - type: bind
        source: ./data
        target: /data
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DOCKER_CONTAINER=True
      - LOG_LEVEL=20
    restart: unless-stopped

  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 300 filmweb_watchdog
    restart: unless-stopped
```

### Cloning a repository

 
```bash
git clone https://github.com/suchencjusz/filmweb_watchdog && cd filmweb_watchdog
pip3 install -r requirements.txt

# usage
python  main.py
```

# Configuration
[How to create webook ](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

Empty `config.json` file is created automatically when the program is started for the first time

`config.json`
```
{
	"discord": {
		"webhook_url": "YOUR DISCORD WEBHOOK URL"
	},
	"users": [
		{
			"name": "YOUR USERNAME",
			"embed_color": "CUSTOM COLOR"
		}
	],
	"schedule": false
}
```

Sample config

```
{
	"discord": {
		"webhook_url": "YOUR DISCORD WEBHOOK URL GOES HERE :O"
	},
	"users": [
		{
			"name": "sucheta348",
			"embed_color": "80cca9"
		},
		{
			"name": "dupadupadupa",
			"embed_color": "89cc09"
		}
	],
	"schedule": false
}
```

# Contributing
### You only have to open a PR! C:
