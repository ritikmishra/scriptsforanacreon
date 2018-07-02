import json
import sys

from anacreonlib import Anacreon
import creds
import time

api = Anacreon(creds.USERNAME, creds.PASSWORD)
api.gameID = creds.ERA_4_ALPHA
api.sovID = creds.CURRENT_SOV

api.get_game_info()
api.get_objects()

PLANET_NAME = "Amon Uilroth"
TARGET_TYPE_ID = 32
OUR_UNITS_TYPE_IDS = (157,)

orbit_at_height = 25

if __name__ == '__main__':

    input("Press enter when ready:")
    planet_obj = api.get_obj_by_name(PLANET_NAME)
    planet_id = planet_obj["id"]
    tactical = api.get_tactical(planet_id)
    print(tactical)

    api.attack(planet_id, "spaceSupremacy", )
    target_tactical_id = None
    our_tactical_ids = []

    for batallion in tactical:
        try:
            if batallion["unitTypeID"] in OUR_UNITS_TYPE_IDS:
                our_tactical_ids.append(batallion["id"])
            elif batallion["unitTypeID"] == TARGET_TYPE_ID:
                target_tactical_id = batallion["id"]
        except KeyError:
            pass

    for tactical_id in our_tactical_ids:
        api.tactical_order("target", planet_id, tactical_id, targetID=target_tactical_id)
        api.tactical_order("orbit", planet_id, tactical_id, orbit=orbit_at_height)

    # while True:
    #     api.tactical_order("orbit", planet_id)

