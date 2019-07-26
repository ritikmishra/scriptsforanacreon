import json
import multiprocessing
import sys
from copy import copy

# import daemon

from anacreonlib import Anacreon
import creds
import time

from fraktur_b.utils import make_notification_base

FLEET_ID = 123
FLEET_NAME = "lawn treaders"
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
    world_id = fleet_obj["anchorObjID"]
    api.attack(world_id, MODE)
    # api.disband_fleet(fleet_obj["id"], fleet_obj["anchorObjID"])

    # wait for attack to be over
    tactical = api.get_tactical(world_id)

    while len([x for x in tactical if x["class"] == "battlePlan"]) > 0:
        print("[", world_id, "]", "Waiting 5 secs")
        time.sleep(5)
        tactical = api.get_tactical(world_id)

    daleras_world_id = 3739
    api.set_fleet_destination(fleet_obj["id"], daleras_world_id)

    print("Waiting for arrival at Daleras")
    time.sleep(api.get_fleet_eta(fleet_obj) + 10)

    fleet_obj = api.get_obj_by_id(fleet_obj["id"], True)

    print("Selling")
    api.sell_fleet(fleet_obj["id"], daleras_world_id, fleet_obj["resources"])
if __name__ == '__main__':
    # with daemon.DaemonContext():
    main()
