"""
Sends a fleet to every independent world around a world
"""
import json
import sys
from copy import copy

from anacreonlib import Anacreon
import creds
import time

EXPLORER_ID = 100
CENTER_WORLD_ID = 38
SOURCE_OBJ_ID = 3023
RANGE = 250

if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    center = api.get_obj_by_id(CENTER_WORLD_ID)

    candidate_worlds = []
    for thing_id, thing in api.objects_dict.items():
        if thing["class"] == "world":
            if thing["sovereignID"] == 1:
                if api.dist(thing["pos"], center["pos"]) <= 250:
                    candidate_worlds.append(thing_id)

    for thing_id in candidate_worlds:
        api.deploy_fleet([EXPLORER_ID, 3], SOURCE_OBJ_ID)
        fleet_id = api.most_recent_fleet()
        api.set_fleet_destination(fleet_id, thing_id)
