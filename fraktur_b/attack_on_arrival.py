import json
import sys
from copy import copy

from anacreonlib import Anacreon
import creds
import time

FLEET_ID = 123
FLEET_NAME = "125th Fleet"
MODE = "spaceSupremacy"

if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    print("Waiting . . .")
    time.sleep(api.get_fleet_eta(api.get_obj_by_name(FLEET_NAME)) + 5)
    fleet_obj = api.get_obj_by_id(FLEET_ID, True)
    api.attack(fleet_obj["anchorObjID"], MODE)
