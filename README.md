# Adhan Cast

A Dockerized Python worker that fetches prayer times from the Mawaqit API based on geolocation and streams the Adhan to a local Chromecast device.

## Usage

1. Create A Mawaqit account if you don't have one. [register](https://mawaqit.net/en/backoffice/register/)
2. Choose your an Adhan link [Here](https://www.islamcan.com/audio/adhan) and a reminder Ayah link [Here](https://everyayah.com/).
3. Fill the environment variables in the .env file.

```bash
latitude=0.0 # The latitude of the location
longitude=0.0 # The longitude of the location
username="user@email.com" # Mawaqit account
password="**********" # Mawaqit password
chromecast="google home mini" # The friendly name of the chromecast device
adhan_link=https://www.islamcan.com/audio/adhan/azan2.mp3 # The link to the Adhan mp3 file
reminder_link=https://everyayah.com/data/Alafasy_128kbps/002153.mp3 # The link to the reminder mp3 file
reminder_before=60 # how many minutes before the prayer the reminder should be played
```

4. Start the docker container.

```bash
docker compose up -d --build
```

## Inspired by

[homeassistant-mawaqit](https://github.com/sbou88/homeassistant-mawaqit)
