import csv
import re
from collections import OrderedDict
import pygeoj

almaFile = open('C:\\Users\\srapp\\Desktop\\Alma_to_AGSL_Nautical\\RussiaChartWBB.csv', encoding='utf8') # path to the exported csv from Alma

almaReader = csv.reader(almaFile)
almaData = list(almaReader)

print('The index for 034 is: ' + str(almaData[0].index('034')))

# Output CSV with OIM Fields
outputCSV = open('C:\\Users\\srapp\\Desktop\\Alma_to_AGSL_Nautical\\Alma2CSV.csv', 'w', newline='', encoding='utf8') 
header = ['label',           
          'west',
          'east',
          'north',
          'south',
          'location',
          'scale',
          'title',
          'edition',
          'available',
          'physHold',
          'digHold',
          'thumbUrl',
          'iiifUrl',
          'downloadUrl',
          'websiteUrl',
          'primeMer',
          'bathLines',
          'bathInterv',
          'projection',
          'publisher',
          'datePub',
          'color',
          'instCallNo',
          'recId',
          'note'
         ]
outputWriter = csv.DictWriter(outputCSV, fieldnames=header, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
outputWriter.writeheader()
# Now we have a CSV with only the header.

# funciton DMS2DD takes a dictionary version of DMS and outputs a float DD
def DMS2DD(DMS): #DMS is a dictionary containing Dir, D, M, and S
    neg = ['W', 'S']
    if DMS['dir'] in neg:
        # DD Value is negative
        h = -1
    else:
        #DD Value is positive
        h = 1
        
    #DD = d + (min/60) + (sec/3600) 
    DD = 0.0
    DD = (int(DMS['d']) + (int(DMS['m'])/60) + (float(DMS['s']/3600))) * h
    return DD #returns DD as float

#This little function will clean brackets off of date strings
def cleanDate(dirtyDate):
    dirtyDate = dirtyDate.strip().replace('[','').replace(']','')
    return dirtyDate

def processRow(row):
    # Create the dictionary for the row:
    rowDict = {}
    for field in header:
        rowDict[field] = None        

    # the re module was already imported above

    ####### Populate the OIM fields ################

    ############################
    ##### From the 034 field ###
    ############################

    # The float versions of the extents are rounded to 8 decimal points.  That's a precision of just over 1mm at the equator.

    #Find the index for 034:
    i = almaData[0].index('034')

    ## scale
    scaleRegex = re.compile(r'(\$b\s)(\d*)')
    scaleMO = scaleRegex.search(row[i])
    if not scaleMO is None:
        scale = int(scaleMO[2])
    else:
        scale = None
        
    rowDict['scale'] = scale

    ## north    
    #Get Southernmost Extent
    southRegex = re.compile(r'(\$g\s)(\D)(\d{3})(\d{2})(\d*)')
    southMO = southRegex.search(row[i])
    if not southMO is None:
        southDMS = {
            'dir':southMO[2],
            'd':int(southMO[3]),
            'm':int(southMO[4]),
            's':float(southMO[5])
        }
        north = DMS2DD(southDMS)
    else:
        north = None
    if not north is None:
        north = round(north, 8)    
    
    rowDict['north'] = north

    ## south
    #Get Northernmost Extent
    northRegex = re.compile(r'(\$f\s)(\D)(\d{3})(\d{2})(\d*)')
    northMO = northRegex.search(row[i])
    if not northMO is None:
        northDMS = {
            'dir':northMO[2],
            'd':int(northMO[3]),
            'm':int(northMO[4]),
            's':float(northMO[5])
        }
        south = DMS2DD(northDMS)
    else:
        south = None

    if not south is None:
        south = round(south, 8)
    
    rowDict['south'] = south
    
    ## west
    #Get westernmost Extent
    westRegex = re.compile(r'(\$d\s)(\D)(\d{3})(\d{2})(\d*)')
    westMO = westRegex.search(row[i])
    if not westMO is None:
        westDMS = {
            'dir':westMO[2],
            'd':int(westMO[3]),
            'm':int(westMO[4]),
            's':float(westMO[5])
        }
        west = DMS2DD(westDMS)
    else:
        west = None

    if not west is None:
        west = round(west, 8)
    
    rowDict['west'] = west
    
    ## east
    #Get easternmost Extent
    eastRegex = re.compile(r'(\$e\s)(\D)(\d{3})(\d{2})(\d*)')
    eastMO = eastRegex.search(row[i])
    if not eastMO is None:
        eastDMS = {
            'dir':eastMO[2],
            'd':int(eastMO[3]),
            'm':int(eastMO[4]),
            's':float(eastMO[5])
        }
        east = DMS2DD(eastDMS)
    else:
        east = None
    
    if not east is None:
        east = round(east, 8)    
    
    rowDict['east'] = east    

    ##########################
    ### From the 110 Field ###
    ##########################

    ## publisher

    #Find the index for 110:
    i = almaData[0].index('110')

    #This will probably need to be changed for other series that aren't the Great Britian Hydrographic Office
    #But that's okay for now!

    publisherRegex = re.compile(r'(\$a\s)(.*)(\$b\s)(.*)')
    publisherMO = publisherRegex.search(row[i])
    if not publisherMO is None:
        publisher = publisherMO[2].strip().strip('.') + ' ' + publisherMO[4].strip().strip('.')
    else:
        publisher = ''

    publisher = publisher[:256] # 256 character limit

    rowDict['publisher'] = publisher

    ##########################
    ### From the 852 Field ###
    ##########################

    ## label

    #Find the index for 852:
    i = almaData[0].index('852')

    # Grab the label field (title part 2, usually a sheet number)

    recordRegex = re.compile(r'(\$h\s)(.*)(\$z?)')
    recordMO = recordRegex.search(row[i])
    if not recordMO is None:
        label = recordMO.group(2).strip()
    else:
        label = ''

    label = label[:50] # Field limited to 50 characters 

    rowDict['label'] = label

    recordRegex = re.compile(r'(\$h\s)(.*)(\$z?)')
    instcallMO = recordRegex.search(row[i])
    if not instcallMO is None:
        instCallNo = recordMO[2].strip()
    else:
        instCallNo = ''

    instCallNo = instCallNo[:50] # Field limited to 50 characters 

    rowDict['instCallNo'] = instCallNo

    ##########################
    ### From the 245 Field ###
    ##########################

    ## title

    #Find the index for 245:
    i = almaData[0].index('245')

    # Grab the "Location" field (Title part 1, usually the text title)

    locationRegex = re.compile(r'(\$a\s)(.*)(\$)')
    locationMO = locationRegex.search(row[i])
    if not locationMO is None:
        title = locationMO[2].strip().strip('/').strip()
    else:
        title = ''

    title = title[:50] #Geodex field is limited to 50 characters

    rowDict['title'] = title
    
    ##########################
    ### From the 300 Field ###
    ##########################

    ## color

    i = almaData[0].index('300')

    # Get Map Production Information

    # if $b is present, will indicate if color or photocopy
    # if $b is not present, monochrome
    # GDX codes:
    #     Positive Photocopy: 34
    #     Printed map - colored: 31
    #     printed map - monochrome: 33

    productionRegex = re.compile(r'(\$b\s)(.*)(;)')
    productionMO = productionRegex.search(row[i])

    if productionMO is None: # It's Monochrome
        color = 33
    elif 'color' in str(productionMO[2]):
        color = 31
    elif 'copy' in str(productionMO[2]):
        color = 34
    else:
        color = None        

    rowDict['color'] = color

    ##########################
    ### From the 264 Field ###
    ##########################

    ## datePub

    i = almaData[0].index('264')

    # Grab the date from the Alma '264' field

    dateRegex = re.compile(r'(\$c\s)(\[?\d\d\d\d\]?)')
    dateMO = dateRegex.search(row[i])

    if not dateMO is None:
        datePub = dateMO[2]
        datePub = cleanDate(datePub)
        if len(datePub) != 4:
            datePub = -999
        else:
            datePub = int(datePub)
            if datePub < 1452:
                datePub = -999
            elif datePub > 2050:
                datePub = -999
            rowDict['datePub'] = datePub
    else:
        datePub = None

    ##########################
    ### From the 500 Field ###
    ##########################

    ## note

    i = almaData[0].index('500')

    # Grab the full note from the Alma '500' field

    recordRegex = re.compile(r'(.*)')
    noteMO = recordRegex.search(row[i])
    if not noteMO is None:
        note = noteMO[0].strip()
    else:
        note = ''   

    rowDict['note'] = note

    ##########################
    ### From the 946 Field ###
    ##########################

    ## recId

    i = almaData[0].index('946')

    # Grab the recId from the Alma '946' field    

    recordRegex = re.compile(r'(\$a\s)(.*)')
    recMO = recordRegex.search(row[i])
    if not recMO is None:
        recId = recMO[2].strip()
    else:
        recId = ''   

    rowDict['recId'] = recId

    ##########################
    ### From the 250 Field ###
    ##########################
    
    ## edition

    i = almaData[0].index('250')

    # Grab the edition from the Alma $a MARC Sub-field   

    recordRegex = re.compile(r'(\$a\s)(.*)')
    editionMO = recordRegex.search(row[i])
    if not editionMO is None:
        edition = editionMO[2].strip()
    else:
        edition = ''   

    rowDict['edition'] = edition

##    # PUBLISHER
##    i = almaData[0].index('264')
##
##    # Grab the "publisher" from the $b MARC Sub-field
##
##    recordRegex = re.compile(r'(\$b\s)(.*)(\s\$c)')
##    publisherMO = recordRegex.search(row[i])
##    if not publisherMO is None:
##        publisher = projectionMO[2].strip()
##    else:
##        publisher = ''
##
##    publisher = publisher[:50] # Field limited to 50 characters 
##
##    rowDict['publisher'] = publisher

    ## available
    available = 1

    # physHold
    physHold = 'yes'


    ##########################
    ### From the 255 Field ###
    ##########################
    
    ## projection

    i = almaData[0].index('255')

    # Grab the "projection" from the $b MARC Sub-field

    recordRegex = re.compile(r'(\$b\s)(.*)(\s\$c)')
    projectionMO = recordRegex.search(row[i])
    if not projectionMO is None:
        projection = projectionMO[2].strip()
    else:
        projection = ''

    projection = projection[:50] # Field limited to 50 characters 

    rowDict['projection'] = projection

    ## primeMer

    primeMer = 131 #Greenwich   

    # populate all the series fields into the row dictionary
    rowDict['label'] = label    
    rowDict['west'] = west
    rowDict['east'] = east
    rowDict['north'] = north
    rowDict['south'] = south    
    rowDict['scale'] = scale
    rowDict['title'] = title
    rowDict['edition'] = edition
    rowDict['available'] = available
    rowDict['physHold'] = physHold
    rowDict['primeMer'] = primeMer
    rowDict['projection'] = projection
    rowDict['publisher'] = publisher
    rowDict['datePub'] = datePub
    rowDict['color'] = color
    rowDict['recId'] = recId
    rowDict['note'] = note
#### Unused fields - we will add these in later    
##    rowDict['date'] = date    
##    rowDict['location'] = location    
##    rowDict['bathLines'] = bathLines
##    rowDict['bathInterv'] = bathInterv    
##    rowDict['instCallNo'] = instCallNo    
##    rowDict['digHold'] = digHold
##    rowDict['thumbUrl'] = thumbUrl
##    rowDict['iiifUrl'] = iiifUrl
##    rowDict['downloadUrl'] = downloadUrl
##    rowDict['websiteUrl'] = websiteUrl    

    return rowDict

# create a new geojson for the OIM Data
almaGeo = pygeoj.new()

for row in almaData:
    rowDict = processRow(row)
    outputWriter.writerow(rowDict)
    # skip any rows that do not have coordinates
    if rowDict['west'] is not None or rowDict['east'] is not None or rowDict['north'] is not None or rowDict['south'] is not None:        
        # Add the values from the dictionary into the geojson feature properties and coordinates
        almaGeo.add_feature(properties={"label": rowDict['label'], "west": rowDict['west'], "east": rowDict['east'], "north": rowDict['north'],
                                        "south": rowDict['south'], "scale": rowDict['scale'], "title": rowDict['title'],
                                        "edition": rowDict['edition'], "available": rowDict['available'], "physHold": rowDict['physHold'],
                                        "primeMer": rowDict['primeMer'], "projection": rowDict['projection'], "publisher": rowDict['publisher'],
                                        "datePub": rowDict['datePub'], "color": rowDict['color'], "recId": rowDict['recId'], "note": rowDict['note']},
                       geometry={"type":"Polygon", "coordinates":[[(rowDict['west'],rowDict['north']),(rowDict['west'],rowDict['south']),(rowDict['east'],
                                                                    rowDict['south']), (rowDict['east'], rowDict['north']), (rowDict['west'], rowDict['north'])]]} )
outputCSV.close()
# Output a geojson with the values of the dictionary 
almaGeo.save("alma2geo.geojson")




