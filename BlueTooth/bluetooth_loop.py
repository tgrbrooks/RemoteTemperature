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

import bluemaestroscan  #specific bluemaestro tempo disc scanner
import json
import sys
import time
import bluetooth._bluetooth as bluez
import gspread

client = gspread.service_account()
sheet = client.open('Remote Temperature')
sheet_instance = sheet.get_worksheet(0)

dev_id = 0
FREQUENCY_SECONDS = 600

def main():
    # Set freq and log filename
    FREQUENCY_SECONDS = 10
	
    # Set MQTT credentials, open connection and start background network loop
    try:
        sock = bluez.hci_open_dev(dev_id)

    except:
        print("error accessing bluetooth device...")
        sys.exit(1)

    bluemaestroscan.hci_le_set_scan_parameters(sock)
    bluemaestroscan.hci_enable_le_scan(sock)

    while True:
        try:
            returnedList = bluemaestroscan.parse_events( sock, 10 )
            currentdatetime = time.strftime( "%Y-%m-%dT%H:%M:%S" )	# 2019-06-25T23:59:00
            print('Date Time:   {0}'.format( currentdatetime ))
            print("number of beacons found {0}".format(len(returnedList)))
            date_time = currentdatetime.split('T')

            for beacon in returnedList:
                # Publish to the MQTT channel
                try:
                    temp = float( beacon["temp"] )
                    humidity = float( beacon["humidity"] )
                    dewpoint = beacon["dewpoint"]
                    battery = beacon["battery"]

                    print("Temp: {0} C, humidity: {1}%, dewpoint: {2} C, battery: {3}%".format( temp, humidity, dewpoint, battery ))
                    # Write to file somewhere or direct to sheets
                    row = [date_time[0], date_time[1], temp, humidity, dewpoint, battery]
                    # Get rid of a row if there are too many
                    if sheet_instance.row_count > 5000:
                        sheet_instance.delete_row(2)
                    sheet_instance.append_row(row)

                except Exception as e:
                    # Null out the worksheet so a login is performed at the top of the loop.
                    time.sleep(60)
                    continue

                    # If we didn't find any matching BLE devices, wait 1 sec.; otherwise wait the speficied amount
                    if len( returnedList ) > 0:
                        time.sleep( FREQUENCY_SECONDS )
                    else:
                        time.sleep( 10 )

        except Exception as e:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            print('Append error, logging in again: ' + str(e))
            print("Sleeping for 60 seconds")
            time.sleep(60)
            continue

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Top-level exception - terminating.")
