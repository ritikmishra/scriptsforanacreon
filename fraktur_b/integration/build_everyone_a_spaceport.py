import json
import sys
from copy import copy

from anacreonlib import Anacreon
import creds
import time

from fraktur_b.utils import find_thing

def squash_traits(worldobj):
    ids = []
    for thing in world_obj["traits"]:
        if type(thing) is int:
            ids.append(thing)
        else:
            ids.append(thing["traitID"])
    return ids


if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    SPACEPORT_ID = find_thing("core.spaceport", api)
    STARPORT_ID = find_thing("core.starport", api)

    for world_id, world_obj in api.objects_dict.items():
        if world_obj["sovereignID"] == api.sovID:
            if world_obj["class"] == "world":
                if world_obj["techLevel"] >= 5:
                    squashed_traits = squash_traits(world_obj["traits"])
                    if SPACEPORT_ID not in squashed_traits and STARPORT_ID not in squashed_traits:
                        print("Building planet", world_obj["name"], "(ID", world_id, ") a spaceport")
                        api.build_improvement(world_id, SPACEPORT_ID)
