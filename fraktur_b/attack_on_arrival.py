import json
import sys
from copy import copy

from anacreonlib import Anacreon
import creds
import time

FLEET_ID = 123
FLEET_NAME = "315th Fleet"
FIND_FLEET_BY_NAME = True
MODE = "spaceSupremacy"

if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    input("Please send your fleet to its destination, and press [ENTER] when ready")

    if FIND_FLEET_BY_NAME:
        fleet_obj = api.get_obj_by_name(FLEET_NAME)
    else:
        fleet_obj = api.get_obj_by_id(FLEET_ID)
    eta = api.get_fleet_eta(fleet_obj) + 5
    print("Waiting", eta, "seconds . . .")
    time.sleep(eta)
    fleet_obj = api.get_obj_by_id(fleet_obj["id"], True)

    with open('fleetobj.json', 'w') as fp:
        json.dump(fleet_obj, fp, indent=4, separators=(',', ': '))

    api.attack(fleet_obj["anchorObjID"], MODE)
