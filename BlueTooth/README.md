_Cloned from <https://github.com/psyciknz/OpenHAB-Scripts>_

# Blue Maestro BLE to MQTT publisher

This repository contains Python scripts for scanning for Blue Maestro BLE temperature sensors and publishing to MQTT.

## Files

* `bluemaestroscan.py`: contains functions for scanning and parsing advertisement payload
* `mqtt.bluetooth.loop.py`: main Python script added by JWJ, based on the original files. Uses **paho-mqtt** to publish to MQTT. Configuration of MQTT server and topic names are in `config.json`.  
  NB: assumes that the MQTT server uses TLS _and_ username/password authentication.
* `config.json`: configuration for `mqtt.bluetooth.loop.py`. Encrypted with `git-crypt`. 

### Git-crypt

Config files are _symmetrically_ encrypted with `git-crypt`. Key is in 1PW.

Refer to git-crypt docs for info about initializing and unlocking.

If you are not me, then you need to create your own `config.json` file. See the next section for syntax.

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
			"timestamp": "bluemaestro/timestamp"
		},
		"bluetooth": {
			"frequency": 1,
			"log": "ble-log.txt"
		}
	}

### MQTT auth

The `mqtt.bluetooth.loop.py` file assumes the MQTT server uses username/password authentication with credentials specified in the config file.

Also, the connection is opened using TLS with CA certificate path specified in the `MQTT.TLS_CERT` parameter. On Linux-based systems, this is usually `/etc/ssl/certs/ca-certificates.crt`. Mac OS, however, uses Keychain to handle certififactes so you need to download the CA certificate and specify the path.

## Permissions
To grant permissions to the BLE subsystem/driver to run as non-admin user, read here: <https://stackoverflow.com/a/42306883/1632704>.

Hm... I actually never got the permissions working even though I followed all steps in the above article. But since I'm running the scripts as a service as a system user, it all works anyway.

## Running as service

Info about running Python scripts as service: <http://www.diegoacuna.me/how-to-run-a-script-as-a-service-in-raspberry-pi-raspbian-jessie/>

1. Copy the `bluemaestro-mqtt.service` file to `/lib/systemd/system/`.
2. Run:

    ```sudo chmod 644 /lib/systemd/system/bluemaestro-mqtt.service
    chmod +x /home/openhabian/OpenHAB-Scripts/BlueTooth/mqtt.bluetooth.loop.py
    sudo systemctl daemon-reload
    sudo systemctl enable bluemaestro-mqtt.service
    sudo systemctl start bluemaestro-mqtt.service
    ```

🐯
