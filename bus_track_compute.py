import json
import requests
import geojson
import auth_params

NAVITIA_TOKEN = auth_params.navitia_api_key
NAVITIA_URL = auth_params.navitia_base_url
NAVITIA_COVERAGE = auth_params.navitia_coverage


def call_navitia_between_to_stops(from_tuple, to_tuple, additionnal_params={}):
    origin = "{};{}".format(from_tuple[1], from_tuple[0])
    destination = "{};{}".format(to_tuple[1], to_tuple[0])
    url_params = {"from" : origin, "to": destination, "first_section_mode[]": "car", "last_section_mode[]" : "car"}
    url_params["max_duration"] = 0 #force non PT journey
    url_params["count"] = 1
    url_params["_override_scenario"] = "experimental"
    url_params = dict(url_params, **additionnal_params)

    url = NAVITIA_URL + "/coverage/{}/journeys".format(NAVITIA_COVERAGE)
    call = requests.get(url, params=url_params,  headers={'Authorization': NAVITIA_TOKEN})
    #print (call.url)
    if not call.status_code == 200 :
        print("Appel à navitia KO - status code : {}".format(call.status_code))
        return
    navitia_response = call.json()
    if not "journeys" in navitia_response :
        print("Pas d'itinéraire retourné : " + navitia_response["error"]["message"])
        return
    navitia_journey = navitia_response['journeys'][0]
    if not "non_pt" in navitia_journey['tags'] :
        print("L'itinéraire retourné n'est pas exploitable (contient du transport en commun)")
        return
    if not navitia_journey["sections"][0]["mode"] == "car" :
        print("L'itinéraire retourné n'est pas exploitable (il n'est pas en voiture)")
        return
    
    track =  geojson.LineString(navitia_journey["sections"][0]['geojson']['coordinates'])
    
    return navitia_journey["sections"][0]['geojson']['coordinates']


def call_navitia_for_this_route(route_id):
    url_schedule = NAVITIA_URL + "/coverage/{}/routes/{}/route_schedules?".format(NAVITIA_COVERAGE, route_id)

    call = requests.get(url_schedule, headers={'Authorization': NAVITIA_TOKEN})
    #print (call.url)
    if not call.status_code == 200 :
        print("Appel à navitia KO - status code : {}".format(call.status_code))
        return    
    navitia_response = call.json()
    if len(navitia_response['route_schedules']) < 1 :
        print("Pas de grille horaire retournée - impossible de récupérer la séquence des arrêts")
        return        
    schedule = navitia_response['route_schedules'][0]

    stops = []
    for a_row in schedule['table']['rows']:
        stops.append((float(a_row['stop_point']['coord']['lat']), float(a_row['stop_point']['coord']['lon']), a_row['stop_point']['name']))

    return stops   

def get_track_for_this_route(route_id):
        stops = call_navitia_for_this_route(route_id)
        if not stops :
           return geojson.Point(0,0)

        linestring_list = []

        for id_, stop in enumerate(stops[:-1]):
            line = call_navitia_between_to_stops(stop, stops[id_+1])
            linestring_list.append(line)

        return geojson.MultiLineString(linestring_list)

