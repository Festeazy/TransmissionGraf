#!/usr/bin/python3

#/usr/bin/python3 /home/titan/Scripts/TransmissionGraf/TG.py
#https://github.com/Festeazy/TranmissionGraf
#V0.01 - Baseline - provided basic info
#V0.02 - Added Geo Mapping for peers
#Current
#V0.03 - Plans to add Leech/Peer Ratio
#Dont really know what Im doing but here you go! 


import os
import re
import sys
import time
import sys
import socket 
from influxdb import InfluxDBClient
import geoip2.database
import datetime
import pygeohash as pgh 
import config
import logging
##Above -- Imports

logging.basicConfig(filename=str(config.TransmissionGrafFolder) + 'TG.log',level=logging.INFO)
print ("Logging Activated")
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')

# logging.info(str(config.TransmissionPort))
# logging.info(str(config.TransmissionUsername))
# logging.info(str(config.TransmissionPassword))
# logging.info(str(config.InfluxDBUsername))
# logging.info(str(config.InfluxDBPassword))
# logging.info(str(config.InfluxDBDatabase))
# logging.info(str(config.InfluxDBHost))
# logging.info(str(config.InfluxDBPort))
# logging.info(str(config.TransmissionGrafFolder))
# logging.warning(str(config.TransmissionGrafFolder))

##Below - Set variables for InfluxDBClient
CurrentScript = sys.argv[0]  
hostname = socket.gethostname()
measurement_name = (hostname + ":Transmissoin:Status:" + CurrentScript) #Specific measurement name for Hostname + Script Name
measurement_time = datetime.datetime.utcnow() ##Time Variable to ensure all writes are synced to this Specific Script Execution
print (measurement_name) 
##Above - Set variables for InfluxDBClient
logging.info(str(measurement_time))

def SendConfig(): #Create and Send InfluxDB body with file information 
    body = [
        {
            "measurement": measurement_name,
            "time": measurement_time,
            "tags": {
                "Name": Name,
                "Hash": Hash,
                "Status": Status
            },
            "fields": {
                "DownSpeed": float(KBDownloadingSpeed),
                "UpSpeed": float(KBUploadingSpeed),
                "Total": float(KBTotalSize),
                "Downloaded": int(KBsDownloaded),
                "Uploaded": float(KBsUploaded),
                #"Ratio": float(Var.Ratio),
                "ETASeconds": int(ETASeconds),
                "Percent": float(IPercent),
                "Status": Status
            }
        }
    ]
    print ("Body has been built, Sending Config Message now")
    ifclient = InfluxDBClient(config.InfluxDBHost,config.InfluxDBPort,config.InfluxDBUsername,config.InfluxDBPassword,config.InfluxDBDatabase)
    print ("Connected to Influx")
    print ("Writing to Influx")
    ifclient.write_points(body)
    print ("Sent to Influx")

    
def SendIPinfo():## function to create write info to InfluxDB per Peer connected
    print ("Gathering IP Info")
    PeerinfoCMD = "transmission-remote  " + str(config.TransmissionHost) + ":" + str(config.TransmissionPort) + " -n " + str(config.TransmissionUsername) + ":" + str(config.TransmissionPassword) + " -t " + torrentnumber + ' -pi | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}" > ' + str(config.TransmissionGrafPeerinfo)
    print (PeerinfoCMD)
    Peerinfo = os.popen(PeerinfoCMD)
    time.sleep(.2)
    PeerinfoFile = str(config.TransmissionGrafPeerinfo)
    peerinfo = open(PeerinfoFile, "r")
    peers = peerinfo.readlines()
    for peer in peers:
        IP = str(peer)[:-1]
        logging.info(IP)
        #GeoIP(IP)    
        reader = geoip2.database.Reader(config.GeoIPDBfile)
        response = reader.city(str(IP))
        Lat = response.location.latitude
        ISO = response.country.iso_code
        Long = response.location.longitude
        State = response.subdivisions.most_specific.name
        City = response.city.name
        Country = response.country.name
        Zip = response.postal.code
        IPAddress = IP
        Geohash1 = pgh.encode(Lat,Long)
        Geohash = ('"' + Geohash1  + '"')
        Geopoint = (Lat,Long)
        print (Country)
        print (State)
        print (City)
        print (Zip)
        print (Long)
        print (Lat)
        print (ISO)
        print (IPAddress)
        print (Geohash)
        print (Geopoint)
        time.sleep(.2)
        reader.close()
                
        IPBody = [
            {
                "measurement": measurement_name,
                "time": measurement_time,
                "tags": {  
                    "Name": Name,
                    "Status": Status,
                    "CurrentScript": str(CurrentScript),
                    "ISO": str(ISO),
                    "Lat": float(Lat),
                    "Long": float(Long),
                    "Geopoint": str(Geopoint),
                    "IP": str(IPAddress)
                            },
                "fields": {
                    "ISO": str(ISO),
                    "Lat": float(Lat),
                    "Long": float(Long),
                    "Geohash": str(Geohash1),
                    "Geopoint": str(Geopoint),
                    "State": str(State),
                    "City": str(City),
                    "IP": str(IP),
                    "Country": str(Country),
                    "Metric": "1",
                    "Hash": str(Hash),
                    "Name": str(Name)
                }
            }
        ]
        print ("Body has been built, Sending IP Info now")
        ifclient = InfluxDBClient(config.InfluxDBHost,config.InfluxDBPort,config.InfluxDBUsername,config.InfluxDBPassword,config.InfluxDBDatabase)
        print ("Connected to Influx")
        print ("Writing to Influx")
        # write the measurement
        ifclient.write_points(IPBody)
        print ("Wrote to Influx")
        peerinfo.close()

    print ("")
##Above --  Sending Config to Influxdb

CmdSummary = "transmission-remote  " + str(config.TransmissionHost) + ":" + str(config.TransmissionPort) + " -n " + str(config.TransmissionUsername) + ":" + str(config.TransmissionPassword) + " -l > " + str(config.TransmissionGrafSummary)
stream = os.popen(CmdSummary)
#stream = os.popen(Transmission)
TransmissionSummarty = stream.read()
#print (TransmissionSummarty)
TransmissionSummary = str(config.TransmissionGrafSummary)
##number and letter string modifcations
Numberonly = re.compile('[^0-9]')
Letteronly = re.compile('[^A-Za-z]')
count = len(open(TransmissionSummary).readlines())
torrentnumbers = count-2
f = open(TransmissionSummary, "r")
lines = f.readlines()[1:-1]
## Start Loop for number of lines in summary minus 2 
for line in lines: 
    #print(line) 
    number = str(re.split("\s+", line)[1:2])
    torrentnumber = Numberonly.sub('', number) 
    Command = "transmission-remote  " + str(config.TransmissionHost) + ":" + str(config.TransmissionPort) + " -n " + str(config.TransmissionUsername) + ":" + str(config.TransmissionPassword) + " -t " + torrentnumber + " -i > " + str(config.TransmissionGrafFileinfo)
    stream = os.popen(Command)
    #print (stream)
    time.sleep(.2)
    f2 = open(str(config.TransmissionGrafFileinfo))
    lines=f2.readlines()
    print (lines)
    ID = str(lines[1])[6:-1]
    
    Name = str(lines[2])[8:-1]
    Hash = str(lines[3])[9:-1]
    Magnet = str(lines[4])[10:-1]
    Status = str(lines[7])[9:-1]
    Location = str(lines[8])[12:-1]
    Percent = str(lines[9])[16:-2]
    ETA = str(lines[10])[7:-1]
    DownloadSpeed = str(lines[11])[18:-1]
    UploadSpeed = str(lines[12])[16:-1]
    Availability = str(lines[14])[16:-2]
    TotalSize = str(lines[15])[15:-1]
    Downloaded = str(lines[16])[14:-1]
    Uploaded = str(lines[17])[12:-1]
    Ratio = str(lines[18])[8:-1]
    DownloadTime = str(lines[26])[1:-1]
    #days,hrs,se
    ##Printing Results
    f2.close()
    print ("------------------------------------------- BEGINING -------------------------")
    print ("ID :" + str(ID))
    print ("Name :" + str(Name))
    print ("Hash :" + str(Hash))
    #print ("Magnet :" + str(Magnet))
    print ("Status :" + str(Status))
    print ("Location :" + str(Location))
    print ("Percent :" + str(Percent))
    if Percent == ("nan"):
        Percent = str("0.00")
    print ("ETA :" + str(ETA))
    mymatch = re.search(r'\((.+)\)', str(lines[10])[7:-1]) ## Getting the seconds for ETA for Influx
    ETASeconds1 = mymatch.group(0)
    print ("ETA Seconds :" + str(ETASeconds1))
    ETASeconds = Numberonly.sub('', ETASeconds1) 
    print ("Download Speed :" + str(DownloadSpeed))
    print ("Upload Speed :" + str(UploadSpeed))
    print ("Availability :" + str(Availability))
    print ("Total Size :" + str(TotalSize))
    if str(TotalSize)[1:3] == "na":
        TotalSize = str("0.00 MB")
    else:
        mymatch1 = re.search(r'\((.+)\)',TotalSize) 
        WantedSize = str(mymatch1.group(0))[1:-11]
        
        print ("Wanted Size :" + str(WantedSize))
    print ("Downloaded :" + str(Downloaded))
    print ("Uploaded :" + str(Uploaded))
    if Uploaded[:4] == ("None"):
        Uploaded = str("0.00 MB")
    else:
        print ("Uploaded dont match")
    print ("Ratio :" + str(Ratio))

    time.sleep(.2)    
    
    
    
    
    #print ("Downloaded for :" + str(DownloadTime))
    DownloadTime1 = re.search(r'\((.+)\)', str(lines[26])[1:-1])
    DownloadTimeSeconds1 = mymatch.group(0)
    DownloadTimeSeconds = Numberonly.sub('', DownloadTimeSeconds1) 
    print ("Downloaded for Seconds :" + DownloadTimeSeconds)

    ## Convert to Influx Data

    ##Speed Conversions
    DownloadSpeedUnit = Letteronly.sub('', DownloadSpeed)  #Download Speed Conversions
    KBDownloadingSpeed = Numberonly.sub('', DownloadSpeed) 
    
    if DownloadSpeedUnit == "MB":
        KBDownloadingSpeed = float(KBDownloadingSpeed)*1000
    print ("Downloading Speed :" + KBDownloadingSpeed + DownloadSpeedUnit)
    ###uploading below
    UploadSpeedUnit = Letteronly.sub('', UploadSpeed)  #Upload Speed Conversions   
    KBUploadingSpeed = Numberonly.sub('', UploadSpeed)  
    if UploadSpeedUnit == "MB":
        KBUploadingSpeed = float(KBUploadingSpeed)*1000
    print ("Uploading Speed kB:" + KBUploadingSpeed + UploadSpeedUnit)
    ## Speed Conversions
    
    #Total Conversions
   
    
    TotalSizeUnit1 = Letteronly.sub('', TotalSize) 
    TotalSizeUnit = TotalSizeUnit1[:2]

    
    
    TotalSize = Numberonly.sub('', WantedSize)
    if TotalSizeUnit == "MB":
        KBTotalSize = float(TotalSize)*100
    elif TotalSizeUnit == "GB":
        KBTotalSize = float(TotalSize)*100000
    print ("Total Size KB:" + str(KBTotalSize) + TotalSizeUnit)


    #unit Conversions for Downloaded/Uploaded
    #GB,MB to kb
    DownloadUnit = Letteronly.sub('', Downloaded) 
    print ("Downloaded unit :" + DownloadUnit) #Getting unit for downloaded amount
    
    DownloadedNumber = Numberonly.sub('', Downloaded)  #Getting Number for Downloaded Amount
    print ("Downloaded Number :" + DownloadedNumber)
    
    if DownloadUnit == "MB":    # if only MB's downloaded 
        KBsDownloaded = float(DownloadedNumber)*100
        print ("KB Downloaded :" + str(KBsDownloaded) + str(DownloadUnit))
    elif DownloadUnit == "GB":  # if only gb's downloaded 
        KBsDownloaded = int(DownloadedNumber)*10000
        print ("KB Downloaded :" + str(KBsDownloaded) + str(DownloadUnit))
    elif DownloadUnit == "kB":  # if only gb's downloaded 
        KBsDownloaded = int(DownloadedNumber)*1
        print ("KB Downloaded :" + str(KBsDownloaded) + str(DownloadUnit))    
    else:
        KBsDownloaded = int(0)
        print ("KB Downloaded :" + str(KBsDownloaded) + str(DownloadUnit))
    
    UploadUnit = Letteronly.sub('', Uploaded) 
    print ("Uploaded unit :" + UploadUnit)

    UploadedNumber = Numberonly.sub('', Uploaded)   ##str(lines[17])[12:-4]
    print ("UploadedNumber  :" + UploadedNumber)
    if UploadUnit == "MB":
        KBsUploaded = float(UploadedNumber)*100
    elif UploadUnit == "GB":
        KBsUploaded = float(UploadedNumber)*10000
    elif UploadUnit == "kB":
        KBsUploaded = float(UploadedNumber)*1
    print ("KB Uploaded :" + str(KBsUploaded))
    IPercent = float(Percent)
    print ("Influx Percent" + str(IPercent))
    ##End of Loop
    time.sleep(.2)
    SendConfig()
    print ("Sending Config")
    time.sleep(.2)
    f.readlines()  
    SendIPinfo()  #For the torrent ID we are on, we will loop through all peers 
    print ("----------------------------- End of Info --------------------------------")
f.close()
##End of File
