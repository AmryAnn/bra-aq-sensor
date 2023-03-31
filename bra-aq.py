#!/usr/bin/env python3

# -----------------------------------------------------------------------------
#                 Example Code for Qwiic Kit for Raspberry Pi
# -----------------------------------------------------------------------------
# Qwiic Starter Kit Demo for Raspberry Pi
# Read data from the BME280, SGP40, and VCNL4040 proximity sensor. Then display
# the data on the screen, the Micro OLED, and send MQTT data to Cayenne.
# Modified by: Ho Yun "Bobby" Chan @ SparkFun Electronics
# Modified Date: December 7, 2022
# By: Michelle Shorter @ SparkFun Electronics
# Original Creation Date: May 29, 2019
#
# For the hookup instructions and kit go to:
#      https://learn.sparkfun.com/tutorials/qwiic-kit-for-raspberry-pi-v2-hookup-guide
#
# This code is beerware/beefware; if you see me (or any other SparkFun employee)
# at the local, and you've found our code helful, please buy us a beer/burger!
#
# Distributed as-is; no warranty is given
# -----------------------------------------------------------------------------

#Must download Qwiic Python Library - https://github.com/sparkfun/qwiic_py
from __future__ import print_function, division
import paho.mqtt.client as mqtt
import qwiic
import qwiic_sgp40    #Need to specify the SGP40
import time
import sys
import csv

#These values are used to give BME280 and SGP40 some time to take samples and log data to Cayenne
initialize=True
n=2
u=60

#MQTT Cayenne setup - you will need your own username, password and clientid
#To setup a Cayenne account go to https://mydevices.com/cayenne/signup/
username = "d4e96770-bf92-11ed-b0e7-e768b61d6137"
password = "29a9b05465389b3bfda761f1b95fc402ff445350"
clientid = "5f0f0b80-c515-11ed-b0e7-e768b61d6137"
mqttc=mqtt.Client(client_id = clientid)
mqttc.username_pw_set(username, password = password)
mqttc.connect("mqtt.mydevices.com", port=1883, keepalive=60)
mqttc.loop_start()

#Qwiic Board define
prox = qwiic.QwiicProximity()
bme = qwiic.QwiicBme280()
my_sgp40 = qwiic_sgp40.QwiicSGP40()
oled = qwiic.QwiicMicroOled()

#Begin statements
prox.begin()
bme.begin()
my_sgp40.begin()
oled.begin()

#Setup OLED
oled.clear(oled.ALL)
oled.display()
oled.set_font_type(1)

#set MQTT topics (we are not setting topics for everything)
topic_bme_temp = "v1/" + username + "/things/" + clientid + "/data/1"
topic_bme_hum = "v1/" + username + "/things/" + clientid + "/data/2"
topic_bme_pressure = "v1/" + username + "/things/" + clientid + "/data/3"
topic_bme_altitude = "v1/" + username + "/things/" + clientid + "/data/4"

topic_prox_proximity = "v1/" + username + "/things/" + clientid + "/data/5"
topic_prox_ambient = "v1/" + username + "/things/" + clientid + "/data/6"

topic_sgp40_voc_index = "v1/" + username + "/things/" + clientid + "/data/7"



#Loop runs until we force an exit or something breaks
while True:
    try:
        if initialize==True:
            print ("Initializing: BME280 and SGP40 are taking samples before printing and publishing data!")
            print (" ")

        else:
            n=1 #set n to 1 to read sensor data once in loop

        for n in range (0,n):
            #print ("n = ", n) #used for debugging for loop

            #Proximity Sensor variables - these are the available read functions
            #There are additional functions not listed to set thresholds, current, and more
            proximity = prox.get_proximity()
            ambient = prox.get_ambient()
            white = prox.get_white()
            #close = prox.is_close()
            #away = prox.is_away()
            #light = prox.is_light()
            #dark = prox.is_dark()
            #id = prox.get_id()

            #BME280 sensor variables
            #reference pressure is available to read or set for altitude calculation
            #referencePressure = bme.get_reference_pressure()
            #bme.set_reference_pressure(referencePressure)

            pressure = bme.get_reference_pressure() #in Pa
            altitudem = bme.get_altitude_meters()
            altitudef = bme.get_altitude_feet()
            humidity = bme.read_humidity()
            tempc = bme.get_temperature_celsius()
            tempf = bme.get_temperature_fahrenheit()
            dewc = bme.get_dewpoint_celsius()
            dewf = bme.get_dewpoint_fahrenheit()

            #SGP40 sensor variable
            voc_index = my_sgp40.get_VOC_index()

            #Give some time for the BME280 and SGP40 to initialize when starting up
            if initialize==True:
                time.sleep(10)
                initialize=False
                print ("Finished initializing")
                print ("") #blank line for easier readability

        #printing time and some variables to the screen
        #https://docs.python.org/3/library/time.html
        #print (time.strftime("%a %b %d %Y %H:%M:%S", time.localtime())) #24-hour time
        print (time.strftime("%a %b %d %Y %I:%M:%S%p", time.localtime())) #12-hour time

        print ("BME280 \t | Temperature: %.1f \xb0F" %tempf)
        #print ("BME280 \t | Temperature: %.1f \xb0C" %tempc)
        print ("BME280 \t | Humidity: %.1f %%RH" %humidity)
        print ("BME280 \t | Pressure: %.2f atm" %(pressure/101300))
        #print ("BME280 \t | Altitude: %.2f m" %altitudem)
        print ("BME280 \t | Altitude: %.2f ft" %altitudef)

        print ("VCNL4040 | Distance Value: %.2f " %proximity)
        print ("VCNL4040 | Ambient Light: %.2f" %ambient)

        print ("SGP40 \t | VOC Index: %.2f" %voc_index)

        print (" ") #blank line for easier readability

        with open('aq.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            fields = ['Temp(f)', 'Humidity', 'Pressure(atm)', 'Altitude(f)', 'Proximity(cm)',
                    'AmbientLight', 'VOCindex']
            values = [tempf, humidity, int(pressure/101300), altitudef, proximity, ambient, voc_index]
            writer.writerow(fields)

        if u==60:
            #send data every 90 seconds to Cayenne, u=900

            #publishing data to Cayenne (we are not publishing everything)
            mqttc.publish (topic_bme_temp, payload = tempf, retain = True)
            mqttc.publish (topic_bme_hum, payload = humidity, retain = True)
            mqttc.publish (topic_bme_pressure, payload = int(pressure/101300), retain = True)
            mqttc.publish (topic_bme_altitude, payload = altitudef, retain = True)

            mqttc.publish (topic_prox_proximity, payload = proximity, retain = True)
            mqttc.publish (topic_prox_ambient, payload = ambient, retain = True)

            mqttc.publish (topic_sgp40_voc_index, payload = voc_index, retain = True)
            u=0 #reset to 0 to begin logging data after another 15 minutes

        #displaying data to the OLED (we are only displaying a few things because of screen size)
        #with font(1) a y difference of 16 is good spacing for each line
        #we are converting values to int before printing for space (and we don't really need better resolution)
        oled.clear(oled.PAGE)

        oled.set_cursor(0,0)
        oled.print("Tmp:")
        oled.print(int(tempf))
        oled.print("F")
        #oled.print(int(tempc))
        #oled.print("C")

        oled.set_cursor(0,16)
        oled.print("RH%:") #Relative Humidity
        oled.print(int(humidity))

        oled.set_cursor(0,32)
        oled.print("VOCi:") #hPa is a more typical output and helps with spacing
        oled.print(voc_index)

        oled.display()

        with open('aq.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            #for value in values:
            writer.writerow(values)


        # update u
        u = u+1
        print("u = %i" %u)
        print (" ") #blank line for easier readability

        #delay (number of seconds) so we are not constantly displaying data and overwhelming devices
        time.sleep(1)


    #if we break things or exit then exit cleanly
    except (EOFError, SystemExit, KeyboardInterrupt):
        mqttc.disconnect()
        print("\nDisconnect MQTT and exit demo.")
        sys.exit()
