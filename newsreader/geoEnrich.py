import MySQLdb as mdb
import sys
from time import time
import argparse
import json
import logging

timestart = time()

##### COMMAND LINE ARGUMENTS #####
parser = argparse.ArgumentParser(description="query gazzeteer for geo data")
parser.add_argument("query", help="string input to query DB with")
parser.add_argument("-q", "--quiet", help="only output on error",action="store_true")
parser.add_argument("-v", "--verbose", help="log level DEBUG",action="store_true")
parser.add_argument("-i", "--input", help="input file to query",
        action="store", required=True)
parser.add_argument("-s", "--server", help="server address for geo queries",
        action="store", required=False, default="localhost")
parser.add_argument("-o", "--output", help="output a file",
                                    action="store", required=False)

arg = parser.parse_args()

##### LOGGING #####
if arg.quiet:
    logging.basicConfig(level=logging.ERROR)
elif arg.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
log = logging.getLogger('relaLog')

##############################

# init the points list for html - for jscript list 
geo_points = []

# open the JSON file
with open(arg.input, 'r') as inputfile:
    nodedata = json.load(inputfile)

# connect to the MySQL DB
connect = mdb.connect(arg.server, 'peter', 'peter1', 'geonames');

### Don't know if I can keep the connect open for all queries or if I'll have to reopen it for each coord request

with connect:

    # This might need to move inside the second for (or the first)
    cursor  = connect.cursor()

    for ind in range(len(nodedata)):
        title = nodedata[ind]['title']
        try:
            for element in [nodedata[ind]['LOCATIONS'][j] for j in [i for i in nodedata[ind]['LOCATIONS']]]:
                try:
                    cursor.execute('''SELECT population, geonameid, name, countrycode, latitude, longitude 
                                      FROM geoname 
                                      WHERE name = %s''', (element,))
                    return_value = cursor.fetchall()

                    coord_tuple = [title,float(max(return_value)[4]),float(max(return_value)[5])]
                    geo_points.append(coord_tuple)
                    
                except KeyError: # NOT THE RIGHT ERROR - will have to test the error thrown when you don't get a hit (try searching for gibberish
                    pass


        except KeyError:
            pass


#print("Time taken:", time() - timestart)
print('''
<!DOCTYPE html>
<style>
#mapid { height: 480px; }
</style>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.3/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.0.3/dist/leaflet.js"></script>
<div id="mapid"></div>
<script>

var points = %(points)r

var mymap = L.map('mapid').setView([51,0], 2);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: 'peterhogan.2o06lcg4',
    accessToken: 'pk.eyJ1IjoicGV0ZXJob2dhbiIsImEiOiJjaXlibmc5OXcwMDUxMzJwMTFmNjR0YTVqIn0.wgGLXdLvInTPohqpwLIcWw'
}).addTo(mymap);

for (var i = 0; i < points.length; i++) {
    marker = new L.marker([points[i][1],points[i][2]])
        .bindPopup(points[i][0])
        .addTo(mymap);
}

var popup = L.popup();

function onMapClick(e){
    popup
        .setLatLng(e.latlng)
        .setContent(e.latlng.toString())
        .openOn(mymap)
}

mymap.on('click', onMapClick);

</script>
<html>
</html>
''' % {'points': geo_points})
