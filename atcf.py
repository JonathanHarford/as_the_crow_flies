"""A web app that calculates the distance (in nautical miles) between two
airports. The app autocompletes the airports and features all airports in the
US. The trip is also plotted on Google Maps."""

import csv
from cgi import parse_qs, escape
from sys import argv
from math import atan2, cos, sin, sqrt

EARTH_RADIUS = 3440.06  # 6371 km

HEADER1_HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>As The Crow Flies</title>
<meta charset="utf-8">
'''

AUTOCOMPLETE_HTML = '''
<link rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
<link rel="stylesheet" href="http://jonathanharford.pythonanywhere.com/static/main.css" />
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
<script src="http://jonathanharford.pythonanywhere.com/static/airports.js"></script>
'''

MAP_HTML = '''
<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
<script src="https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false">
</script>
<script>
var map;
function initialize() {
  var bounds = new google.maps.LatLngBounds();
  var latLng1 = new google.maps.LatLng( %(lat1)f, %(lng1)f );
  bounds.extend(latLng1);
  var latLng2 = new google.maps.LatLng( %(lat2)f, %(lng2)f );
  bounds.extend(latLng2);
  var mapOptions = {
    mapTypeId: google.maps.MapTypeId.TERRAIN
  };
  map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
  map.fitBounds(bounds);

  var polyOptions = {
    geodesic:true,
    path: [latLng1, latLng2],
    strokeColor: '#ff0000',
    strokeOpacity: 1.0,
    strokeWeight: 2    
  };

  var polyline = new google.maps.Polyline(polyOptions);

  polyline.setMap(map)

}

google.maps.event.addDomListener(window, 'load', initialize);
</script>'''


HEADER2_HTML = '''
</head>
<body>
<h1>As The Crow Flies</h1>'''

FORM_HTML = '''
<form action="." method="GET">
<p>Enter two US airports:</p>
<label for="ap1">From: </label><input class="autocomplete" name="ap1" />
<label for="ap2">To: </label><input class="autocomplete" name="ap2" />
<input type="submit" value="Calculate Distance">
</form>'''

ANSWER_HTML = '''
<p id="answer">Distance from {} to {}: {:,.1f} nautical miles.</p>'''

MAP_CANVAS_HTML = '''
<div id="map-canvas"></div>'''

FOOTER_HTML = '''</body></html>'''


def load_airports(csvfile):
    """Make a dict from the given CSV file of airports."""
    return {code: {'airport': airport,
                   'city':   city,
                   'coords_rad': (float(lat_rad), float(lng_rad)),
                   'coords_deg': (float(lat_deg), float(lng_deg))
                   }
            # We dont need altitude
            for (airport, city, code, lat_deg, lng_deg, lat_rad, lng_rad, _)
            in csv.reader(open(csvfile))}


def asthecrowflies(airport_dict, ap1, ap2):
    """Calculate the distance between any two points on the globe using the
    Vincenty formula (thanks, Wikipedia)."""

    lat_1, lng_1 = ap1['coords_rad']  # Airport 1 coords (radians)
    lat_2, lng_2 = ap2['coords_rad']  # Airport 2 coords (radians)

    # We could calculate all the sins and cosines, but this is more readable.
    lng_d = abs(lng_1 - lng_2)  # Longitudinal delta
    top = sqrt((cos(lat_2) * sin(lng_d)) ** 2 +
               (cos(lat_1) * sin(lat_2) -
                sin(lat_1) * cos(lat_2) * cos(lng_d)) ** 2)
    bottom = sin(lat_1) * sin(lat_2) + cos(lat_1) * cos(lat_2) * cos(lng_d)
    arc_length = atan2(top, bottom)
    return EARTH_RADIUS * arc_length


def application(environ, start_response):
    """The main WSGI application. Return a list of strings to be concatenated 
    into the final HTML page."""
    airports = load_airports('./data/us_airports.csv')  # openflights.org
    parameters = parse_qs(environ.get('QUERY_STRING', ''))
    start_response('200 OK', [('Content-Type', 'text/html')])
    if parameters:
        code1 = parameters['ap1'][0][:3].upper()
        code2 = parameters['ap2'][0][:3].upper()
        ap1 = airports[code1]
        ap2 = airports[code2]
        dist = asthecrowflies(airports, ap1, ap2)
        print ap1['coords_deg']
        print ap2['coords_deg']
        return [HEADER1_HTML,
                AUTOCOMPLETE_HTML,
                MAP_HTML % {'lat1': ap1['coords_deg'][0],
                            'lng1': ap1['coords_deg'][1],
                            'lat2': ap2['coords_deg'][0],
                            'lng2': ap2['coords_deg'][1]
                            },
                HEADER2_HTML,
                FORM_HTML,
                ANSWER_HTML.format(code1, code2, dist),
                MAP_CANVAS_HTML,
                FOOTER_HTML
                ]
    else:
        return [HEADER1_HTML,
                AUTOCOMPLETE_HTML,
                HEADER2_HTML,
                FORM_HTML,
                FOOTER_HTML
                ]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
