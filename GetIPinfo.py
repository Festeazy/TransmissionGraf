#!/usr/bin/python

#https://github.com/maxmind/GeoIP2-python

import datetime
import psutil
from influxdb import InfluxDBClient
import geoip2.database
import socket 
import sys



print str(sys.argv[1])

print str(sys.argv[1])


print(socket.gethostname())

reader = geoip2.database.Reader('/home/titan/Scripts/Grafana/GeoLite2-City.mmdb')
response = reader.city(str(sys.argv[1]))

Lat = response.location.latitude
ISO = response.country.iso_code
Long = response.location.longitude
State = response.subdivisions.most_specific.name
City = response.city.name
Country = response.country.name
Zip = response.postal.code
IP = str(sys.argv[1])
print (Country)
print (State)
print (City)
print (Zip)
print (Long)
print (Lat)
print (ISO)
print (IP)
reader.close()



# influx configuration - edit these
ifuser = "PASSWORD"
ifpass = "PASSWORD"
#ifdb   = "DATABASE"
ifdb   = "Test"
ifhost = "192.168.0.1"
ifport = 8081
hostname = socket.gethostname()
measurement_name = (hostname + ":Locations")
print (measurement_name)
# take a timestamp for this measurement
time = datetime.datetime.utcnow()

# format the data as a single measurement for influx
body = [
    {
        "measurement": measurement_name,
        "time": time,
        "tags": {
            "key": ISO,
            "latitude": Lat,
            "longitude": Long,
            "name": Country
            },
        "fields": {

            "latitude": Lat,
            "longitude": Long,
            "State": State,
            "City": City,
            "key": ISO,
            "IPAdress": IP,
            "name": Country,
            "metric": 1
         

            
        }
    }
]

# connect to influx
ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)

# write the measurement
ifclient.write_points(body)
