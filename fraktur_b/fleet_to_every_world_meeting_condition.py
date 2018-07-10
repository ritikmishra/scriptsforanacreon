"""
Sends a fleet to every independent world around a world
"""
import json
import sys
from copy import copy

from anacreonlib import Anacreon
import creds
import time

from fraktur_b.utils import find_thing

api = Anacreon(creds.USERNAME, creds.PASSWORD)
api.gameID = creds.ERA_4_ALPHA
api.sovID = creds.CURRENT_SOV

api.get_game_info()
api.get_objects()

CAPITAL = api.get_obj_by_id(90)




def fleet_to_world(condition, api: Anacreon, source):
    explorer_id = find_thing("core.explorerHelion", api)
    candidate_worlds = []
    for thing_id, thing in api.objects_dict.items():
        if condition(thing):
            print("World", thing["name"], "is a candidate")
            candidate_worlds.append(thing_id)

    for thing_id in candidate_worlds:
        api.deploy_fleet([explorer_id, 3], source)
        fleet_id = api.most_recent_fleet()
        api.set_fleet_destination(fleet_id, thing_id)


def is_in_range(world):
    if world["class"] == "world":
        if world["sovereignID"] != api.sovID:
            if 250 <= api.dist(world["pos"], CAPITAL["pos"]) <= 350:
                return True
    return False
if __name__ == '__main__':

    fleet_to_world(is_in_range, api, 3023)
