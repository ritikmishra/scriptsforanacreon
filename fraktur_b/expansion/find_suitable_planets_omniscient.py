"""
Sends 1 fleet to every planet in range
"Naive" because it is not omniscient
"""
import json
import sys

from anacreonlib import Anacreon
import creds
import time

ALLOWED_RESOURCES = [1, 3, 26, 148, 99, 141, 100, 101]
CIRCLE_CENTER_ID = 38

api = Anacreon(creds.USERNAME, creds.PASSWORD)
api.gameID = creds.ERA_4_ALPHA
api.sovID = creds.CURRENT_SOV

api.get_game_info()
api.get_objects()


def can_conquer_planet(planet_obj):
    if planet_obj["sovereignID"] == 1:
        if api.dist(planet_obj["pos"], circle_center_planet["pos"]) <= 250:
            if api.get_forces(planet_obj["resources"])[0] < 10000:
                # for resource_id in planet_obj["resources"][::2]:
                #     if (resource_id in api.sf_calc.keys() or resource_id in api.gf_calc.keys()) and resource_id not in ALLOWED_RESOURCES:
                #         return False
                return True

    return False


if __name__ == '__main__':
    circle_center_planet = api.get_obj_by_id(CIRCLE_CENTER_ID)
    suitable_planet_ids = [planet_id for planet_id, planet in api.objects_dict.items() if can_conquer_planet(planet)]

    with open('planet_ids_to_invade.json', 'w') as fp:
        json.dump(suitable_planet_ids, fp, indent=4, separators=(',', ': '))
