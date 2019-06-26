_Cloned from <https://github.com/psyciknz/OpenHAB-Scripts>_

# Bluemaestro BLE to MQTT publisher

**NB:** Only the files in `./BlueTooth` has been verified. All other files have not been touched; refer to the original repo for info.

## Files

* `bluemaestroscan.py`: contains functions for scanning and parsing advertisement payload
* `mqtt.bluetooth.loop.py`: added by JWJ. Uses **paho-mqtt** to publish to MQTT. Configuration of MQTT server and topic names are in `config.json`.  
  NB: assumes that the MQTT server uses TLS _and_ username/password authentication.
* `mqtt.bluetooth.py`: original simple MQTT publisher. Looping.
* `mqtt.homie.bluetooth.py`: original Homie-based publisher. Never got this working.
* `mqtt.homie.bluetooth.noloop.py`: as above, but one-shot.
* `homie-bluetooth.json`: configuration for the Homie-based publishers. Encrypted with `git-crypt`.
* `config.json`: configuration for `mqtt.bluetooth.loop.py`. Encrypted with `git-crypt`. 

### Git-crypt

Config files are _symmetrically_ encrypted with `git-crypt`. Key is in 1PW.

Refer to git-crypt docs for info about initializing and unlocking.

### Config.json

Sample `Config.json` file:

	{
		"MQTT": {
			"HOST": "something.cloudmqtt.com",
			"PORT": 12343,
			"KEEPALIVE": 10,
			"USERNAME": "username",
			"PASSWORD": "password",
			"TLS_CERT": "/etc/ssl/certs/ca-certificates.crt"
		},
		"topics": {
			"temp": "/bluemaestro/temp",
			"humidity": "/bluemaestro/humidity",
			"dewpoint": "/bluemaestro/dewpoint",
			"battery": "/bluemaestro/battery"
		},
		"bluetooth": {
			"frequency": 1,
			"log": "ble-log.txt"
		}
	}

### MQTT auth

The `mqtt.bluetooth.loop.py` file assumes the MQTT server uses username/password authentication with credentials specified in the config file.

Also, the connection is opened using TLS with CA certificate path specified in the `MQTT.TLS_CERT` parameter.
