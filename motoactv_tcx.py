#!/usr/bin/python
# Requires ElementTree (http://effbot.org/zone/element-index.htm)
# It helps to pipe the output of this script through tidy, e.g.:
# ./motoactv_tcx.py -i rawDataCsv.csv | tidy -q -i -xml

import time
import csv
import math
import itertools
import sys
import getopt

from elementtree.ElementTree import Element, SubElement, Comment, dump, tostring
from elementtree.SimpleXMLWriter import XMLWriter

MPS_TO_MPH = 2.237

def XMLHeader():
    return '<?xml version="1.0" encoding="UTF-8"?>'

def DictToXML(inp):
    i_root = Element('item')
    for (field, val) in inp.iteritems():
        SubElement(i_root, field).text = val
        return i_root

def stringGMTimeFromEpoch(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))
        
def earliestTimeInDict(theDict):
    earliestTime = 0.0
    
    for row in theDict:
        epoch = row['timestamp_epoch']
        if earliestTime == 0:
            earliestTime = epoch
        elif epoch < earliestTime:
            earliestTime = epoch
            
        return earliestTime
def usage():
    print 'Usage: ' + sys.argv[0] + ' -i <CSV file>'
        
def main(argv):

    scale = 1.0
    pathToCSV = ""
    forceHRM = False
    removePauses = False
    sport = "Running"
    lat = 0.0
    longt = 0.0
    ylat = 37.337766
    ylong = -121.920347

    try:
        opts, args = getopt.getopt(argv, "hbpYs:i:t:l:",["scale=", "ifile=", "sport=", "location="])
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-s", "--scale"):
            scale = float(arg)
        elif opt in ("-i", "--ifile"):
            pathToCSV = arg
        elif opt in ("-t", "--sport"):
            sport = arg
        elif opt in ("-l", "--location"):
            lat, longt = arg.split(",")
            lat = float(lat)
            longt = float(longt)
        elif opt == '-Y':
            lat = ylat
            longt = ylong
        elif opt == '-b':
            forceHRM = True
        elif opt == '-p':
            removePauses = True
        
    if pathToCSV == "":
        usage()
        sys.exit(1) 
    
    f = open(pathToCSV)
    dataDict = csv.DictReader(f)
    intensity = "Resting"
    triggerMethod = "Distance"

    tcxTrackpoints = {}
    earliestEpochMS = earliestTimeInDict(dataDict)
    earliestEpoch = math.floor(int(earliestEpochMS) / 1000)

    root = Element("TrainingCenterDatabase")
    root.set("xsi:schemaLocation", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")
    root.set("xmlns:ns2", "http://www.garmin.com/xmlschemas/UserProfile/v2")
    root.set("xmlns:ns3", "http://www.garmin.com/xmlschemas/ActivityExtension/v2")
    root.set("xmlns:ns4", "http://www.garmin.com/xmlschemas/ProfileExtension/v1")
    root.set("xmlns:ns5", "http://www.garmin.com/xmlschemas/ActivityGoals/v1")
    root.set("xmlns", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

    actsElement = SubElement(root, "Activities")
    actElement = SubElement(actsElement, "Activity", Sport=sport)

    idElement = SubElement(actElement, "Id")
    idElement.text = stringGMTimeFromEpoch(earliestEpoch)

    lastTimeEpoch = 0
    
    lapElement = SubElement(actElement, "Lap", StartTime=stringGMTimeFromEpoch(earliestEpoch))
    
    totalDistanceMeters = 0
    maxSpeed = 0
    calories = 0.0
    maxBPM = 0    
    maxSpeed = 0.0
    numRows = 0
    totalBPM = 0
    epochStart = 0
    diff = 0
    
    trackpoints = list()
    
    for row in dataDict:
        speed = scale * float(row['SPEED'])
        stepRate = int(row['STEP_RATE'])

        if speed > maxSpeed:
            maxSpeed = speed

        if not removePauses or (speed > 0 and stepRate > 0):
            if epochStart != 0:
                diff += int(row['timestamp_epoch']) - epochStart
                epochStart = 0

            trackpointElement = Element("Trackpoint")
            trackpoints.append(trackpointElement)
        
            # TIME
            epochMS = row['timestamp_epoch']
            epoch = math.floor((int(epochMS) - diff) / 1000)
            timeElement = SubElement(trackpointElement, "Time")
            timeElement.text = stringGMTimeFromEpoch(epoch)

            # POSITION
            if (lat == 0.0 and longt == 0.0):
                latValue = row['LATITUDE']
                longValue = row['LONGITUDE']
            else:
                latValue = str(lat)
                longValue = str(longt)
        
            if (abs(float(latValue)) <= 180 and abs(float(longValue)) <= 180
                and abs(float(latValue)) > 0.1 and abs(float(longValue)) > 0.1):
                posElement = SubElement(trackpointElement, "Position")
                latElement = SubElement(posElement, "LatitudeDegrees")
                latElement.text = latValue
                longElement = SubElement(posElement, "LongitudeDegrees")
                longElement.text = longValue
        
            # Altitude
            alt = row['ELEVATION']
            altElement = SubElement(trackpointElement, "AltitudeMeters")
            altElement.text = alt

            # DISTANCE
            distanceMeters = str(scale * float(row['DISTANCE']))
            distElement = SubElement(trackpointElement, "DistanceMeters")
            distElement.text = distanceMeters

            # BPM
            heartRate = math.trunc(float(row['HEARTRATE']))
            if forceHRM or heartRate > 0:
                bpmElement = SubElement(trackpointElement, 'HeartRateBpm xsi:type=\"HeartRateInBeatsPerMinute_t\"')
                bpmValElement = SubElement(bpmElement, "Value")
                bpmValElement.text = str(heartRate)
                
            extElement = SubElement(trackpointElement, 'Extensions')
        
            # SPEED
            speed *= MPS_TO_MPH
            ns3Element = SubElement(extElement, 'ns3:TPX')
            speedElement = SubElement(ns3Element, 'ns3:Speed')
            speedElement.text = str(speed)
                
            if lastTimeEpoch == 0 or epoch > lastTimeEpoch:
                lastTimeEpoch = epoch

            if totalDistanceMeters == 0 or float(distanceMeters) > float(totalDistanceMeters):
                totalDistanceMeters = distanceMeters

            rowCalories = row['CALORIEBURN']
            calories = rowCalories

            if maxBPM == 0 or heartRate > maxBPM:
                maxBPM = heartRate

            numRows += 1
            totalBPM += heartRate

            # CADENCE
            cadenceElement = SubElement(trackpointElement, "Cadence")
            cadenceElement.text = str(stepRate / 2)
        elif epochStart == 0:
            epochStart = int(row['timestamp_epoch'])
        
    # TIME    
    totalTimeSeconds = lastTimeEpoch - earliestEpoch
    avgBPM = totalBPM / numRows
        
    totalTimeElement = SubElement(lapElement, "TotalTimeSeconds")
    totalTimeElement.text = str(int(totalTimeSeconds))

    # DISTANCE
    totalDistanceElement = SubElement(lapElement, "DistanceMeters")
    totalDistanceElement.text = totalDistanceMeters
    
    # MAX SPEED
    if maxSpeed > 0.0:
        maxSpeedElement = SubElement(lapElement, "MaximumSpeed")
        maxSpeedElement.text = str(maxSpeed)

    # CALORIES
    totalCalsElement = SubElement(lapElement, "Calories")
    totalCalsElement.text = str(int(float(calories)))
    
    # BPM
    if forceHRM or avgBPM > 0:
        avgBPMElement = SubElement(lapElement, 'AverageHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t"')
        avgBPMValElement = SubElement(avgBPMElement, "Value")
        avgBPMValElement.text = str(int(avgBPM))

    if forceHRM or maxBPM > 0:
        maxBPMElement = SubElement(lapElement, 'MaximumHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t"')
        maxBPMValElement = SubElement(maxBPMElement, "Value")
        maxBPMValElement.text = str(int(maxBPM))
    
    # INTENSITY
    intensityElement = SubElement(lapElement, "Intensity")
    intensityElement.text = "Active"

    #TRIGGER
    triggerElement = SubElement(lapElement, "TriggerMethod")
    triggerElement.text = "Distance"

    # Append trackpoints
    trackElement = SubElement(lapElement, "Track")    
    for trackpoint in trackpoints:
        trackElement.append(trackpoint)
    
    print XMLHeader() + tostring(Comment("Scale: "+str(scale))) + tostring(root)

main(sys.argv[1:])
