import json
import sys
from copy import copy

from anacreonlib import Anacreon
import creds
import time

AUTONOMOUS_DESIG = 33
CGAF_DESIG = 71


def should_designate_to_cgaf(world_obj):
    try:
        if world_obj["techLevel"] < 5:
            if world_obj["designation"] == AUTONOMOUS_DESIG:
                return True
    except KeyError:
        return False
    return False


if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    for world_id, world_obj in api.objects_dict.items():
        if world_obj["sovereignID"] == api.sovID:
            if should_designate_to_cgaf(world_obj):
                print("Designated planet", world_obj["name"], "(ID", world_id, ") to CGAF")
                api.designate_world(world_id, CGAF_DESIG)
