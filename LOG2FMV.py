import datetime
import os
import fnmatch
import xml.etree.ElementTree as ET
import subprocess
import flirpy.io.seq
from tkinter import filedialog
from tkinter import *
import glob
import shutil

def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    print(filename)

def set_dir():
    sourcePath = folder_path.get()
    os.chdir(sourcePath)  # Provide the path here

def get_duration(file):
    """Get the duration of a video using ffprobe."""
    cmd = 'ffprobe -i "{}" -show_entries format=duration -v quiet -of csv="p=0"'.format(file)
    output = subprocess.check_output(
        cmd,
        shell=True, # Let this run in the shell
        # stderr=subprocess.STDOUT
    )
    # return round(float(output))  # ugly, but rounds your seconds up or down
    return float(output)

def output_avi(file):
    """Create avi file from frames using ffmpeg"""
    cmd = 'ffmpeg -r 30 -s 640x480 -i ./' + file + '/preview/frame_%6d.png -vcodec libx264 -crf 25  -y -pix_fmt yuv420p ./output/' + file + '.mp4'
    output = subprocess.check_output(
        cmd,
        shell=True, # Let this run in the shell
        # stderr=subprocess.STDOUT
    )
    # return round(float(output))  # ugly, but rounds your seconds up or down
    return get_duration('./output/' + file + '.mp4')

# Data Table format:
# 0      1      2      3      4      5      6      7      8      9      10     11
# Time   Lat    Lon    Alt    Head   PRoll  PPit   SensR  SensE  SensAz HFOV   VFOV

# timeZone = input('Enter time zone: ')
# timeOffset = int(timeZone) * 3600 * 100000

# VARIABLES #########
sensRelRoll = 0
sensRelPit = -90
platRoll = 0
platPit = 0
sensRelAz = 0
hFOV = 45
vFOV = 35

logPattern = '*.gpx'
vidPattern = '*.seq'

mainDir = "Z:/Data/Wildlife/Thermal/Landtrust/2019/Data/3-11-19_pm/"
dirList = ["./East/FLIR", "./West/FLIR"]
x = 0

for flights in dirList:
    os.chdir(mainDir)
    os.chdir(dirList[x])
    print(os.getcwd())
    fileList = os.listdir('.')
    # os.mkdir('./output')
    # Find the number of video files so we can create a list of appropriate length
    i = 0
    for entry in fileList:
        if fnmatch.fnmatch(entry, vidPattern):
            i = i + 1

    logFileName = 'null'
    vidFile = [[0 for y in range(4)] for z in range(int(i))]

    i = 0

    # Iterate through fileList, find log file and save file name, find video files, save names and durations in list
    for entry in fileList:
        if fnmatch.fnmatch(entry, logPattern):
            logFileName = entry
        elif fnmatch.fnmatch(entry, vidPattern):
            vidFile[i][0] = entry

            # print("Splitting SEQ file...")
            # splitter = flirpy.io.seq.splitter("./")
            # splitter.process(entry)

            # vidFile[i][1] = round(output_avi(vidFile[i][0][0:18]))
            # print("Cleaning up...")
            # shutil.rmtree("./" + vidFile[i][0][0:18], ignore_errors=TRUE)

            vidFile[i][1] = round(get_duration('./output/' + vidFile[i][0][0:18] + '.mp4'))

            ye = int(vidFile[i][0][0:4])  # Read in each data value to its own variable, maybe a list would be more elegant. Known limitation: When we reach the year 10,000 this will break. I pity the poor sap who is counting deer in 8,000 years
            mo = int(vidFile[i][0][4:6])
            da = int(vidFile[i][0][6:8])
            ho = int(vidFile[i][0][9:11])
            mi = int(vidFile[i][0][11:13])
            se = int(vidFile[i][0][13:15])
            vDT = datetime.datetime(ye, mo, da, ho, mi, se)  # Reformat into a date time format and write that shit into a new variable
            vidFile[i][2] = 1000000*int(vDT.timestamp())  # Re-reformat into UNIX epoch microseconds and write that shit into an even newer variable
            vidFile[i][3] = int(vidFile[i][2] + (vidFile[i][1])*1000000)
            i = i + 1

    # create element tree object
    tree = ET.parse(logFileName)

    # get root element
    root = tree.getroot()

    # Create table to hold telemetry data
    trkpts = [[0 for y in range(8)] for z in range(1 + len(root.findall('./{http://www.topografix.com/GPX/1/1}trk/{http://www.topografix.com/GPX/1/1}trkseg/{http://www.topografix.com/GPX/1/1}trkpt')))]
    i = 0

    for items in root.findall('./{http://www.topografix.com/GPX/1/1}trk/{http://www.topografix.com/GPX/1/1}trkseg/{http://www.topografix.com/GPX/1/1}trkpt'):
        trkpts[i][0] = items.find('{http://www.topografix.com/GPX/1/1}time').text
        trkpts[i][1] = items.get('lat')
        trkpts[i][2] = items.get('lon')
        trkpts[i][3] = items.find('{http://www.topografix.com/GPX/1/1}ele').text
        trkpts[i][4] = items.find('{http://www.topografix.com/GPX/1/1}course').text
        trkpts[i][5] = items.find('{http://www.topografix.com/GPX/1/1}roll').text
        trkpts[i][6] = items.find('{http://www.topografix.com/GPX/1/1}pitch').text
        ye = int(trkpts[i][0][0:4])  # Read in each data value to its own variable, maybe a list would be more elegant. Known limitation: When we reach the year 10,000 this will break. I pity the poor sap who is counting deer in 8,000 years
        mo = int(trkpts[i][0][5:7])
        da = int(trkpts[i][0][8:10])
        ho = int(trkpts[i][0][11:13])
        mi = int(trkpts[i][0][14:16])
        se = int(trkpts[i][0][17:19])
        tDT = datetime.datetime(ye, mo, da, ho, mi,se)  # Reformat into a date time format and write that shit into a new variable
        trkpts[i][7] = int(1000000 * int(tDT.timestamp())) # + timeOffset  # Re-reformat into UNIX epoch microseconds and write that shit into an even newer variable
        i = i + 1

    i = 0
    vidTele = [0 for z in range(len(vidFile))]

    # Things are getting a little crazy here getting the telemetry pared down. Basically, this code block iterates through the list of video files,
    # and runs a loop within that loop that find the index values of the trkpts list that correspond to the start and end of the video.
    for vids in vidFile[:]:
        j = 0
        start = 0
        end = 0
        for tele in trkpts[:]:
            if vids[2] == tele[7] and start == 0:
                start = j
            if vids[2] < tele[7] and start == 0:
                start = j
            if vids[3] == tele[7]:
                end = j
            if vids[3] < tele[7]:
                end = j
                break
            j = j + 1
        vidTele[i] = trkpts[start:end]
        # Setup output matrix and write headers
        numLines = int(1 + (len(vidTele[i])))
        dataTable = [[0 for y in range(12)] for z in range(numLines)]
        dataTable[0][0] = 'UNIX Time Stamp'
        dataTable[0][1] = 'SensorLatitude'
        dataTable[0][2] = 'SensorLongitude'
        dataTable[0][3] = 'SensorAltitude'
        dataTable[0][4] = 'PlatformHeading'
        dataTable[0][5] = 'PlatformRoll'
        dataTable[0][6] = 'PlatformPitch'
        dataTable[0][7] = 'SensorRelativeRoll'
        dataTable[0][8] = 'SensorRelativeElevation'
        dataTable[0][9] = 'SensorRelativeAzimuth'
        dataTable[0][10] = 'HorizontalFOV'
        dataTable[0][11] = 'VerticalFOV'

        k = 0
        for item in vidTele[:]:
            output = open('./output/' + str(vidFile[k][0][0:18]) + '.csv', 'w')
            output.write(str(dataTable[0][0]) + ',' + str(dataTable[0][1]) + ',' + str(dataTable[0][2]) + ',' + str(
                dataTable[0][3]) + ',' + str(dataTable[0][4]) + ',' + str(dataTable[0][5]) + ',' + str(
                dataTable[0][6]) + ',' + str(dataTable[0][7]) + ',' + str(dataTable[0][8]) + ',' + str(
                dataTable[0][9]) + ',' + str(dataTable[0][10]) + ',' + str(dataTable[0][11]) + '\n')
            if item != 0:
                for piece in item[:]:
                    output.write(str(piece[7]) + ',' + str(piece[1]) + ',' + str(piece[2]) + ',' + str(piece[3]) + ',' + str(
                        piece[4]) + ',' + str(platPit) + ',' + str(platRoll) + ',' + str(sensRelRoll) + ',' + str(
                        sensRelPit) + ',' + str(sensRelAz) + ',' + str(hFOV) + ',' + str(vFOV) + '\n')
                output.close()
                k = k + 1
        i = i + 1
    i = 0
    x = x + 1
i=0