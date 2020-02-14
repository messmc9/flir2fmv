import os
import fnmatch
import arcpy
arcpy.ImportToolbox('C:\Program Files (x86)\ArcGIS\Desktop10.6\ArcToolbox\Toolboxes\Full Motion Video Tools.tbx')
avgEle = 200
vidPattern = '*.mp4'

mainDir = 'Z:/Data/Wildlife/Thermal/Landtrust/2019/Data/3-8-19_am/West/FLIR/output/'
os.chdir(mainDir)
print(os.getcwd())
fileList = os.listdir('.')

for entry in fileList:
    if fnmatch.fnmatch(entry, vidPattern):
        arcpy.VideoMultiplexer_FMV(input_video_file=mainDir + entry[0:18] + ".mp4", input_metadata_file=mainDir + entry[0:18] + ".csv", output_video_file=mainDir + entry[0:18] + ".ts", metadata_field_mapping_file="", calculate_coordinates="true", average_elevation=avgEle, time_shift_observations_file="", bit_rate="Use input video bit rate", custom_bit_rate="-1")
