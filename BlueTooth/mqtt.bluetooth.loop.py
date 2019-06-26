# Blue Maestro Tempo Disk Scanner for MQTT
# Takes all values from the scanned tempo disc and using the MAC id pushes each topic into MQTT
# requires paho.mqtt client and bluez.
# Also requires bluemaestroscan.py in th esame directory as this has the specifics for decoding
#  the advertising packets for the Blue Maestro Tempo Disc https://www.bluemaestro.com/product/tempo-disc-temperature/
# Unsure if there are any other Blue Maetro products that it would work with.
# David@andc.nz 15/12/2016

# Credit jcs 6/8/2014 as basis

# Modified 2019-06 by JWJ:
#	- no longer uses Homie
#	- uses "simple" MQTT with topics defined in config file
#	- MQTT server info is defined in config file

#import bluemaestroscan  #specific bluemaestro tempo disc scanner
import json
import sys
import argparse
import time
import logging
#import bluetooth._bluetooth as bluez
import logging
import paho.mqtt.client as mqtt # pip install paho-mqtt
import paho.mqtt.publish as publish
import ssl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dev_id = 0
FREQUENCY_SECONDS = 600
LOG = "/var/log/mqtt.home.bluetooth.log"

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)


def main( configfile='homie-bluetooth.json' ):
	# Read config
	print "Loading config from: " + configfile
	with open( configfile ) as json_file:  
		config = json.load( json_file )

	print "Configuration:"
	print config

	# Initialize MQTT client
	mqttc = mqtt.Client()	# Default parameters. Auto-generate client name
	# Assign event callbacks
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect
	mqttc.on_publish = on_publish
	mqttc.on_subscribe = on_subscribe

	MOSQUITTO_HOST = config["MQTT"]["HOST"]
	MOSQUITTO_PORT = config["MQTT"]["PORT"]
	MOSQUITTO_KEEPALIVE = config["MQTT"]["KEEPALIVE"]
	MOSQUITTO_USER = config["MQTT"]["USERNAME"]
	MOSQUITTO_PWD = config["MQTT"]["PASSWORD"]
	mqttc.username_pw_set( MOSQUITTO_USER, MOSQUITTO_PWD )

	# Set freq and log filename
	FREQUENCY_SECONDS =config["bluetooth"]["frequency"]
	LOG = config["bluetooth"]["log"]
	logging.basicConfig(filename=LOG, level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')   

	auth = {
		'username':MOSQUITTO_USER,
		'password':MOSQUITTO_PWD
	}

	tls = {
  		'ca_certs':config["MQTT"]["TLS_CERT"]
	}

	publish.single( config["topics"]["humidity"], payload=55.2, hostname=MOSQUITTO_HOST, port=MOSQUITTO_PORT, keepalive=MOSQUITTO_KEEPALIVE, auth=auth, tls=tls, protocol=mqtt.MQTTv311 )
	print "Done2"
	# JWJ test
	#print "Connection to {0}:{1}".format( MOSQUITTO_HOST, MOSQUITTO_PORT )
	#mqttc.connect( MOSQUITTO_HOST, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE )
	#mqttc.loop_start()

	#while True:
	#	print "Publishing to {0}".format( config["topics"]["temp"] )
	#	mqttc.publish( config["topics"]["temp"], 12 )
	#	time.sleep( 5 )
	# /JWJ test

	try:
		sock = bluez.hci_open_dev(dev_id)
		logging.info("ble thread started")

	except:
		print "error accessing bluetooth device..."
		logging.info("error accessing bluetooth device...")
	    	sys.exit(1)
	
	bluemaestroscan.hci_le_set_scan_parameters(sock)
	bluemaestroscan.hci_enable_le_scan(sock)


	while True:
		try:
			returnedList = bluemaestroscan.parse_events( sock, 10 )
			nodes = {}
			print "-------------------------------------------------------------------------------------------------------"
			logging.info("-------------------------------------------------------------------------------------------------------")
			mac = ""
			temp = 0
			currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
			print('Date Time:   {0}'.format(currentdate))
			logging.info('Date Time:   {0}'.format(currentdate))
			for beacon in returnedList:
				val = returnedList[beacon]
				print beacon, val
				mac = returnedList["mac"]
				temp = returnedList["temp"]
		
				print "number of beacons found {0}".format(len(returnedList))
				logging.info("number of beacons found {0}".format(len(returnedList)))
				if len(returnedList) > 0:
					print "%s/temperature = %.2f" % (returnedList["mac"],returnedList["temp"])
					logging.info("%s/temperature = %.2f" % (returnedList["mac"],returnedList["temp"]))
					# Publish to the MQTT channel
					try:
						temp = float(returnedList["temp"])
						humidity = float(returnedList["humidity"])
						dewpoint = returnedList["dewpoint"]
						battery = returnedList["battery"]

						print "Temp: {0} C, humidity: {1}%, dewpoint: {2} C, battery: {3}%".format( temp, humidity, dewpoint, battery )
						time.sleep(1)

					except Exception,e:
						# Null out the worksheet so a login is performed at the top of the loop.
						logging.error('Append error, logging in again: ' + str(e))
						logging.error("Sleeping for 60 seconds")
						time.sleep(60)
						continue
				else:
					print "Sleeping for 30 seconds" 
					logging.info("Sleeping for 30 seconds" )
					time.sleep(30)
                        logging.info("Sleeping for %s seconds" % FREQUENCY_SECONDS)
                        print("Sleeping for %s seconds" % FREQUENCY_SECONDS)
			time.sleep(FREQUENCY_SECONDS)

		except Exception,e:
	       	# Error appending data, most likely because credentials are stale.
			# Null out the worksheet so a login is performed at the top of the loop.
			print('Append error, logging in again: ' + str(e))
			print "Sleeping for 60 seconds"
			time.sleep(60)
			continue

if __name__ == '__main__':
    try:
        parser= argparse.ArgumentParser(description="MQTT Based Bluetooth Reader")
        parser.add_argument('-c','--configfile', help='Configuration filename (json)',required=True)
        args = parser.parse_args()
        main(args.configfile)
    except (KeyboardInterrupt, SystemExit):
        print "quitting."

