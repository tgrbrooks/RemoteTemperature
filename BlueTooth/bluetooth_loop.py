# Blue Maestro Tempo Disk Scanner
# Takes all values from the scanned tempo disc and sends to a google sheet
# requires pybluez and gspread.
# Also requires bluemaestroscan.py in the same directory as this has the specifics for decoding
#  the advertising packets for the Blue Maestro Tempo Disc https://www.bluemaestro.com/product/tempo-disc-temperature/
# Unsure if there are any other Blue Maetro products that it would work with.
# David@andc.nz 15/12/2016

# Credit jcs 6/8/2014 as basis

# Modified 2019-06 by JWJ:
#	- no longer uses Homie
#	- uses "simple" MQTT with topics defined in config file
#	- MQTT server info is defined in config file

# Modified 2020-10 by tgrbrooks:
#       - Doesn't use MQTT, sends to google sheet instead

import bluemaestroscan  #specific bluemaestro tempo disc scanner
import json
import sys
import time
import bluetooth._bluetooth as bluez
import csv
import gspread

# --------- USER CONFIGURATION -------------
# How often to take a reading
FREQUENCY_SECONDS = 30

# Open up google sheet interface
# Requires the API key in a json file at ~/.config/gspread/service_account.json
# Also requires the sheet to be shared with the service account
client = gspread.service_account()
sheet = client.open('Remote Temperature')
sheet_instance = sheet.get_worksheet(0)

dev_id = 0

def main(sock):
    # Set up for scanning
    bluemaestroscan.hci_le_set_scan_parameters(sock)
    bluemaestroscan.hci_enable_le_scan(sock)

    # Loop until killed
    while True:
        try:
            returnedList = bluemaestroscan.parse_events( sock, 10 )
            currentdatetime = time.strftime( "%Y-%m-%dT%H:%M:%S" )	# 2019-06-25T23:59:00
            print('Date Time:   {0}'.format( currentdatetime ))
            print("number of beacons found {0}".format(len(returnedList)))
            date_time = currentdatetime.split('T')

            for beacon in returnedList:
                # Publish to the google sheet
                try:
                    temp = float( beacon["temp"] )
                    humidity = float( beacon["humidity"] )
                    dewpoint = beacon["dewpoint"]
                    battery = beacon["battery"]

                    print("Temp: {0} C, humidity: {1}%, dewpoint: {2} C, battery: {3}%".format( temp, humidity, dewpoint, battery ))
                    # Write to file somewhere and direct to sheet
                    bluemaestroscan.hci_disable_le_scan(sock)
                    row = [date_time[0], date_time[1], temp, humidity, dewpoint, battery]
                    with open("/home/pi/Documents/RemoteTemperature/data.csv", "a") as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow(row)
                    # Get rid of a row if there are too many
                    if sheet_instance.row_count > 5000:
                        sheet_instance.delete_row(2)
                    sheet_instance.append_row(row)
                    time.sleep( FREQUENCY_SECONDS )
                    bluemaestroscan.hci_enable_le_scan(sock)

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
        sock = bluez.hci_open_dev(dev_id)
        main(sock)
    except (KeyboardInterrupt, SystemExit):
        bluemaestroscan.hci_disable_le_scan(sock)
        sock.close()
        print("Top-level exception - terminating.")
        sys.exit(1)
