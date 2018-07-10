"""
This script moves Warphants from their jumpship yard to their infantry autofac
Cron approved
"""
import multiprocessing
import time

from anacreonlib import Anacreon
import json
import creds

api = Anacreon(creds.USERNAME, creds.PASSWORD)
api.gameID = creds.ERA_4_ALPHA
api.sovID = creds.CURRENT_SOV

api.get_game_info()
api.get_objects()

api_call_semaphore = multiprocessing.BoundedSemaphore(6)


def send_a_fleet(source_id, dest_id, resources):
    api_call_semaphore.acquire()
    try:
        api.deploy_fleet(resources, source_id)
        fleet_id = api.most_recent_fleet()
        api.set_fleet_destination(fleet_id, dest_id)
    except Exception as e:
        raise e
    else:
        print("Sending a fleet from source ID", source_id, "to dest ID", dest_id, ".")
    finally:
        api_call_semaphore.release()


def find_thing(unid):
    # find ID of warphant
    for type_id, type_obj in api.scenario_info.items():
        if type_obj["unid"] == unid:
            return type_id
    else:
        raise Exception("Thing not found ???")


def is_world_jumpship_yard(world):
    if world["class"] == "world":
        if world["sovereignID"] == api.sovID:
            if world["designation"] == jumpship_yard_desig_id:
                for i, resource_id in enumerate(world["resources"][::2]):
                    if resource_id == warphant_id:
                        return True
    return False


def is_world_ramship_yard(world):
    if world["class"] == "world":
        if world["sovereignID"] == api.sovID:
            if world["designation"] == ramship_yard_desig_id:
                for i, resource_id in enumerate(world["resources"][::2]):
                    if resource_id == cerberus_id:
                        return True
    return False


def is_world_infantry_academy(world):
    if world["class"] == "world":
        if world["sovereignID"] == api.sovID:
            if world["designation"] == infantry_academy_desig_id:
                return True
    return False


def is_world_in_nebula(world):
    if world["class"] == "world":
        if world["sovereignID"] == api.sovID:
            if in_bright_nebula_id in world["traits"] or in_dark_nebula_id in world["traits"]:
                return True
    return False


def is_world_not_in_nebula(world):
    if world["class"] == "world":
        if world["sovereignID"] == api.sovID:
            if not (in_bright_nebula_id in world["traits"] or in_dark_nebula_id in world["traits"]):
                return True
    return False

def is_world_starship_yard(world):
    if world["class"] == "world":
        if world["sovereignID"] == api.sovID:
            if world["designation"] == starship_yard_desig_id:
                for i, resource_id in enumerate(world["resources"][::2]):
                    if resource_id == minotaur_id:
                        return True
    return False

warphant_id = find_thing("core.jumptransportWarphant")
jumpship_yard_desig_id = find_thing("core.jumpshipYardsDesignation")
ramship_yard_desig_id = find_thing("core.ramshipYardsDesignation")
starship_yard_desig_id = find_thing("core.starshipYardsDesignation")

cerberus_id = find_thing("core.gunshipCerberus")
minotaur_id = find_thing("core.gunshipMinotaur")

infantry_academy_desig_id = find_thing("core.infantryAcademyDesignation")
in_bright_nebula_id = find_thing("core.inBrightNebula")
in_dark_nebula_id = find_thing("core.inDarkNebula")


def spread_resources(is_world_producer, is_world_consumer, thing_id):
    where_are_things = {}
    """Key is worldID, value is quantity"""

    where_do_they_need_to_go = []

    # step 1: find the warphants
    # step 2: who is making infantry
    for world_id, world in api.objects_dict.items():
        if is_world_producer(world):
            for i, resource_id in enumerate(world["resources"][::2]):
                if resource_id == thing_id:
                    qty = world["resources"][2 * i + 1]
                    where_are_things[world["id"]] = qty
                    print(world["name"], qty)
                    break
        elif is_world_consumer(world):
            where_do_they_need_to_go.append(world_id)

    # step 3: split up warphants
    total_things_available = sum(where_are_things.values())

    things_per_planet = int((total_things_available / len(where_do_they_need_to_go)) * 0.94)  # just in case

    print("Distributing", things_per_planet, "things per planet")
    print("There are", len(where_do_they_need_to_go), "planets")

    for consumer_id in where_do_they_need_to_go:
        thing_required = things_per_planet

        for producer_id, quantity in where_are_things.items():
            if thing_required <= quantity:
                multiprocessing.Process(target=send_a_fleet,
                                        args=(producer_id, consumer_id, [thing_id, thing_required])).start()
                where_are_things[producer_id] -= thing_required
                break
            elif quantity > 0:
                multiprocessing.Process(target=send_a_fleet,
                                        args=(producer_id, consumer_id, [thing_id, quantity])).start()
                thing_required -= quantity
                where_are_things[producer_id] -= quantity




if __name__ == '__main__':
    print("Spreading warphants!")
    spread_resources(is_world_jumpship_yard, is_world_infantry_academy, warphant_id)
    #
    # print("Spreading Cerberus's")
    # spread_resources(is_world_ramship_yard, is_world_in_nebula, cerberus_id)


    # print("Spreading Minotaurs")
    # spread_resources(is_world_starship_yard, is_world_not_in_nebula, minotaur_id)