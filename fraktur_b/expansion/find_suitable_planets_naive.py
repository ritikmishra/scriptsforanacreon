"""
Sends 1 fleet to every planet in range sequentially
"Naive" because it is not omniscient
"""
import json
import sys

from anacreonlib import Anacreon
import creds
import time

FLEET_NAME = "Exploration Fleet Uno"
ALLOWED_RESOURCES = [1, 3, 26, 148, 99, 141, 100, 101]
CIRCLE_CENTER_ID = 90

if __name__ == '__main__':
    # Autenticate
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    # find the center of the circle
    circle_center_planet = api.get_obj_by_id(CIRCLE_CENTER_ID)
    suitable_planet_ids = []

    planet_ids_in_range = []

    # Find planets who are in range of us
    for id, thing in api.objects_dict.items():
        if thing["sovereignID"] == 1:
            if api.dist(thing["pos"], circle_center_planet["pos"]) <= 250:
                planet_ids_in_range.append(id)

    # find our fleet that is exploring
    exploration_fleet_obj = api.get_obj_by_name(FLEET_NAME)

    # as long as we have a world to go to
    while len(planet_ids_in_range) > 0:
        # find the nearest world to go to
        closest_planet_id = min(planet_ids_in_range,
                                key=lambda id: api.dist(api.get_obj_by_id(id)["pos"], exploration_fleet_obj["pos"]))

        # go to that world
        api.set_fleet_destination(exploration_fleet_obj["id"], closest_planet_id)

        # wait for arrival
        eta = api.get_fleet_eta(api.get_obj_by_id(exploration_fleet_obj["id"]))
        print("Waiting", eta, "seconds while fleet goes to planet ID", closest_planet_id)
        time.sleep(eta + 1)

        # get world's information
        current_planet = api.get_obj_by_id(closest_planet_id, refresh=True)
        print("Arrived at planet ID", closest_planet_id)

        # check if the world's defenses are allowed
        for resource_id in current_planet["resources"][::2]:
            if (
                    resource_id in api.sf_calc.keys() or resource_id in api.gf_calc.keys()) and resource_id not in ALLOWED_RESOURCES:
                print("Planet had banned resource")
                break
        else:
            print("Planet is good to go")
            suitable_planet_ids.append(current_planet["id"])

        planet_ids_in_range.remove(closest_planet_id)

    # save our findings
    with open('planet_ids_to_invade.json', 'w') as fp:
        json.dump(suitable_planet_ids, fp, indent=4, separators=(',', ': '))
