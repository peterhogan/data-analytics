import random
import MySQLdb as mdb
import sys
from time import time
import argparse
import json
import logging

timestart = time()

##### COMMAND LINE ARGUMENTS #####
parser = argparse.ArgumentParser(description="query gazzeteer for geo data")
#parser.add_argument("query", help="string input to query DB with")
parser.add_argument("-q", "--quiet", help="only output on error",action="store_true")
parser.add_argument("-v", "--verbose", help="log level DEBUG",action="store_true")
parser.add_argument("-n", "--number", help="only process n entries",
        action="store", required=False)
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

# cache queries for speed up
locations = {}

# init the counter (n)
counter = 0

# init jitter for dups
#jitter = random.choice([1,-1])*random.random()/10000

# open the JSON file
log.debug("Opening file: %r", arg.input)
with open(arg.input, 'r') as inputfile:
    nodedata = json.load(inputfile)
    log.debug("File opened successfully")

# connect to the MySQL DB
connect = mdb.connect(arg.server, 'peter', 'peter1', 'geonames');
log.debug("Connected to MySQL successfully")

with connect:

    # initialise SQL cursor
    cursor  = connect.cursor()

    for ind in range(len(nodedata)):
        roottitle = nodedata[ind]['title']
        try:
            for element in [nodedata[ind]['LOCATIONS'][j] for j in [i for i in nodedata[ind]['LOCATIONS']]]:
                title = roottitle+" : "+element
                log.debug("Title is: %s", title)
                if element in locations:
                    log.debug("element %s found in locations dictionary", element)
                    coord_tuple = [title, locations[element][0],locations[element][1]]
                else:
                    log.debug("element %s not found in dictionary, querying MySQL and adding", element)
                    try:
                        cursor.execute('''SELECT population, geonameid, name, countrycode, latitude, longitude 
                                          FROM geoname 
                                          WHERE name = %s''', (element,))
                        return_value = cursor.fetchall()
                        log.debug("Return value from query: %r",return_value)

                        coord_pair = [float(max(return_value)[4]),float(max(return_value)[5])]

                        # add to dict to speed up queries
                        log.debug("adding %r to locations dict", coord_pair)
                        locations[element] = coord_pair

                        coord_tuple = [title,coord_pair[0],coord_pair[1]]
                        
                    except ValueError:
                        log.warn("Problem with database query - look at MySQL logs")
                        pass

                ## construct the coord tuple
                if coord_tuple in geo_points:
                    log.warn("duplicate point found: %r", coord_tuple)
                    log.debug("applying jitter")
                    coord_tuple = [coord_tuple[0],
                                   random.choice([1,-1])*random.random()/100+coord_tuple[1],
                                   random.choice([1,-1])*random.random()/100+coord_tuple[2]]
                geo_points.append(coord_tuple)
                log.debug("Tuple Value: %r", coord_tuple)


        except KeyError:
            pass

        log.debug("Counter value: %i",counter)
        counter += 1

        if arg.number and counter >= int(arg.number):
            break

finishtime = time() - timestart
log.debug("Time taken: %r", finishtime)
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
