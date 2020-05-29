#!/usr/bin/python3
import os
homedir = os.environ['HOME']
TransmissionGrafFolder=str(homedir + "/Scripts/TransmissionGraf/")
GeoIPDBfile=str(TransmissionGrafFolder + "GeoLite2-City.mmdb")
TransmissionGrafFileinfo=str(TransmissionGrafFolder + ".fileinfo")
TransmissionGrafPeerinfo=str(TransmissionGrafFolder + ".peerinfo")
TransmissionGrafSummary=str(TransmissionGrafFolder + ".transmissionsummary")

TransmissionHost="192.168.0.1"
TransmissionPort="9091"
TransmissionUsername="USERNAME"
TransmissionPassword="Password"

InfluxDBUsername="USERNAME"
InfluxDBPassword="Password"
InfluxDBDatabase="Test"
InfluxDBHost="192.168.0.1"
InfluxDBPort="8081"