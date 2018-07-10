import json
import multiprocessing
import sys
from copy import copy

import daemon

from anacreonlib import Anacreon
import creds
import time

from fraktur_b.utils import make_notification_base

FLEET_ID = 123
FLEET_NAME = "get off my lawn"
FIND_FLEET_BY_NAME = True
MODE = "spaceSupremacy"

def main():
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()

    input("Please send your fleet to its destination, and press [ENTER] when ready")


    api.get_objects()


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


    make_notification_base("Attacking that world!", "Fleet name " + FLEET_NAME + " is attacking the world")

    ### ACTION ###
    api.attack(fleet_obj["anchorObjID"], MODE)
    # api.disband_fleet(fleet_obj["id"], fleet_obj["anchorObjID"])

if __name__ == '__main__':
    # with daemon.DaemonContext():
    main()
