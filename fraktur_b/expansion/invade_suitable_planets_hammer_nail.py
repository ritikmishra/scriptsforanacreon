"""
This script automates the hammer-nail method of invading worlds. This method is where the hammer fleet wipes the world of defenses,
then the nail fleet comes in to clean up and invade.
"""
import json
import queue
from copy import copy
from typing import Any, Dict

from anacreonlib import Anacreon
import creds
import time

import sys

from fraktur_b.utils import make_notification_base
import threading

HAMMER_FLEET_NAME = "Hammer"
NAIL_FLEET_NAME = "Nail"

api = Anacreon(creds.USERNAME, creds.PASSWORD)
api.gameID = creds.ERA_4_ALPHA
api.sovID = creds.CURRENT_SOV
api.get_game_info()

api.get_objects()


def sort_by_distance(world_id, fleet_obj):
    return api.dist(api.get_obj_by_id(world_id)["pos"], fleet_obj["pos"])


def sort_by_space_force(world_id):
    return api.get_forces(api.get_obj_by_id(world_id)["resources"])[0]


def send_fleet_to_world_and_attack(fleet_obj: Dict[str, Any], world_id: int, mode: str, name: str) -> None:
    """
    Send a fleet to a world and attack it
    :param fleet_obj: The object representing the fleet's info
    :param world_id: The ID of the world
    :param mode: 'spaceSupremacy' or 'invasion'
    :param name: 'Hammer' or 'nail'
    :return: None
    """
    api.set_fleet_destination(fleet_obj["id"], world_id)

    eta = api.get_fleet_eta(api.get_obj_by_id(fleet_obj["id"]))

    current_planet = api.get_obj_by_id(world_id)

    make_notification_base("[" + name + "]" + "Forces travelling to" + str(current_planet["name"]),
                           "Planet ID" + str(current_planet["id"]))

    print("[", name, "]", "Waiting", eta, "seconds while fleet goes to planet ID", world_id)
    time.sleep(eta + 1)

    current_planet = api.get_obj_by_id(world_id, refresh=True)
    print("[", name, "]", "Arrived at planet ID", world_id)

    api.attack(world_id, mode)
    make_notification_base("[" + name + "]" + "Forces launch attack on" + str(current_planet["name"]),
                           "Planet ID" + str(current_planet["id"]))

    print("[", name, "]", "Attacking planet ID", world_id)

    # wait for attack to be over
    tactical = api.get_tactical(world_id)

    while len([x for x in tactical if x["class"] == "battlePlan"]) > 0:
        print("[", name, "]", "Waiting 5 secs")
        time.sleep(5)
        tactical = api.get_tactical(world_id)

    print("[", name, "]", "Conquered planet ID", world_id)
    # print("[", name, "]", str(len(planet_ids_to_invade)) + " planets left to invade")
    make_notification_base("[" + name + "]" + "Forces conquered" + str(current_planet["name"]),
                           "Planet ID" + str(current_planet["id"]))


def hammer_thread_func():
    # 1. find a new place
    # 2. attack it
    # 3. add it to the queue
    hammer_semaphore.acquire()
    try:
        while len(planet_ids_to_invade) > 0:
            hammer_target_id = min(planet_ids_to_invade, key=sort_by_space_force)
            # check for 0 space forces
            if api.get_forces(api.get_obj_by_id(hammer_target_id)["resources"])[0] > 0:
                send_fleet_to_world_and_attack(hammer_fleet_obj, hammer_target_id, "spaceSupremacy", "Hammer")
            planet_ids_to_invade.remove(hammer_target_id)
            print("[ Hammer ]", len(planet_ids_to_invade), "planets left to invade")
            nail_queue.put(hammer_target_id)
    finally:
        hammer_semaphore.release()


def nail_thread_func():
    nail_semaphore.acquire()
    try:
        while len(planet_ids_to_invade) > 0 or not nail_queue.empty(): # hammer will finish first by design
            nail_target_id = nail_queue.get()
            send_fleet_to_world_and_attack(nail_fleet_obj, nail_target_id, "invasion", "nail")
    finally:
        nail_semaphore.release()


if __name__ == '__main__':

    with open("planet_ids_to_invade.json", "r") as f:
        planet_ids_to_invade = copy(json.load(f))
        f.close()
        del f

    planet_ids_to_invade = [planet_id for planet_id in planet_ids_to_invade if
                            api.get_obj_by_id(planet_id)["sovereignID"] == 1]

    print(planet_ids_to_invade)
    hammer_fleet_obj = api.get_obj_by_name(HAMMER_FLEET_NAME)
    nail_fleet_obj = api.get_obj_by_name(NAIL_FLEET_NAME)

    hammer_semaphore = threading.Semaphore()
    nail_semaphore = threading.Semaphore()

    # hammer_target_id = None
    # nail_target_id = None
    hammer_target_id = 2214
    nail_target_id = 2060

    nail_queue = queue.Queue()
    hammer_thread = threading.Thread(target=hammer_thread_func)
    nail_thread = threading.Thread(target=nail_thread_func)

    hammer_thread.start()
    nail_thread.start()

    # while len(planet_ids_to_invade) > 0:
    #     hammer_target_id = min(planet_ids_to_invade, key=sort_by_distance)
    #     # that world gets attacked
    #     print("Sending hammer to ID", hammer_target_id)
    #     hammer_thread = threading.Thread(target=send_fleet_to_world_and_attack,
    #                                      args=(hammer_fleet_obj, hammer_target_id, "spaceSupremacy", "Hammer"))
    #
    #     hammer_thread.start()
    #     if nail_target_id is not None:
    #         print("Sending nail to ID", nail_target_id)
    #         # nail's world gets attacked
    #         nail_thread = threading.Thread(target=send_fleet_to_world_and_attack,
    #                                          args=(nail_fleet_obj, nail_target_id, "invasion", "nail"))
    #
    #         nail_thread.start()
    #     else:
    #         nail_thread = None
    #
    #     print("Waiting for hammer to return . . .")
    #     # wait until hammer is done
    #     hammer_thread.join()
    #
    #     print("Waiting for nail to return . . .")
    #     if nail_thread is not None:
    #         nail_thread.join()
    #
    #     print("[ Main ]", len(planet_ids_to_invade), "planets left to invade")
    #     nail_target_id = hammer_target_id

    with open('planet_ids_to_invade.json', 'w') as fp:
        json.dump(planet_ids_to_invade, fp, indent=4, separators=(',', ': '))
