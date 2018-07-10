"""
Sends a fleet to every independent world around a world
"""
import collections
import json
import multiprocessing
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

EXPLORER_ID = find_thing("core.explorerHelion", api)
SOURCE_OBJ_ID = 3023
ENEMY_SOV_ID = 172512

World = collections.namedtuple("World", ["name", "id"])

api_call_semaphore = multiprocessing.BoundedSemaphore(10)

def send_a_fleet(fleet_id, dest_id):
    api_call_semaphore.acquire()
    try:
        api.set_fleet_destination(fleet_id, thing.id)
    finally:
        api_call_semaphore.release()


if __name__ == '__main__':

    candidate_worlds = []
    for thing_id, thing in api.objects_dict.items():
        if thing["class"] == "world":
            if thing["sovereignID"] == ENEMY_SOV_ID:
                candidate_worlds.append(World(thing["name"], thing_id))

    for thing in candidate_worlds:
        api.deploy_fleet([EXPLORER_ID, 3], SOURCE_OBJ_ID)
        fleet_id = api.most_recent_fleet()
        print("Sending an envoy to", thing.name)
        # api.set_fleet_destination(fleet_id, thing.id)
        multiprocessing.Process(target=send_a_fleet, args=(fleet_id, thing.id)).start()
