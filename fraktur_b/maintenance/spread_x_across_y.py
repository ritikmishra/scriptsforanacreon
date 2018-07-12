"""
This script moves Warphants from their jumpship yard to their infantry autofac
Cron approved
"""
import collections
import multiprocessing
import time

from anacreonlib import Anacreon
import json
import creds
import argparse

from fraktur_b.utils import world_has_trait

parser = argparse.ArgumentParser()
parser.add_argument("--warphants", help="Spread warphants across infantry academies", action="store_true")
parser.add_argument("--minotaurs", help="Spread minotaurs across clearspace worlds", action="store_true")
parser.add_argument("--cerberuses", help="Spread cerberuses across nebular worlds", action="store_true")
parser.add_argument("--same_sector", help="Force fleets to only go to worlds within the same sector",
                    action="store_true")
parser.add_argument("--percent_to_use", help="What percent of all ships in the category we should use",
                    action="store_const", const=0.94, default=0.94)
arguments = parser.parse_args()

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

ResourceDistribution = collections.namedtuple("ResourceDistribution", ["units_per_consumer", "producers", "consumers", "item_id"])


# plan resource distribution
def _plan_resource_disribution(worlds, is_world_producer, is_world_consumer, thing_id):
    where_are_things = {}
    """Key is worldID, value is quantity"""

    where_do_they_need_to_go = []

    # step 1: find the warphants
    # step 2: who is making infantry
    for world_id, world in worlds.items():
        if is_world_producer(world):
            for i, resource_id in enumerate(world["resources"][::2]):
                if resource_id == thing_id:
                    qty = world["resources"][2 * i + 1]
                    where_are_things[world["id"]] = qty
                    print(world["name"], qty)
                    break
        elif is_world_consumer(world):
            where_do_they_need_to_go.append(world_id)

    total_things_available = sum(where_are_things.values())

    things_per_planet = int((total_things_available / len(where_do_they_need_to_go)) * arguments.percent_to_use)

    return ResourceDistribution(units_per_consumer=things_per_planet, producers=where_are_things,
                                consumers=where_do_they_need_to_go, item_id=thing_id)


# enforce resource distribution
def _apply_resource_distribution(resource_dist: ResourceDistribution):
    print("Distributing", resource_dist.units_per_consumer, "things per planet")
    print("There are", len(resource_dist.consumers), "planets")

    for consumer_id in resource_dist.consumers:
        thing_required = resource_dist.units_per_consumer

        for producer_id, quantity in resource_dist.producers.items():
            if thing_required <= quantity:
                multiprocessing.Process(target=send_a_fleet,
                                        args=(producer_id, consumer_id, [resource_dist.item_id, thing_required])).start()
                resource_dist.producers[producer_id] -= thing_required
                break
            elif quantity > 0:
                multiprocessing.Process(target=send_a_fleet,
                                        args=(producer_id, consumer_id, [resource_dist.item_id, quantity])).start()
                thing_required -= quantity
                resource_dist.producers[producer_id] -= quantity


def spread_resources(is_world_producer, is_world_consumer, thing_id, segregate_sector_capitals=False):
    if segregate_sector_capitals:
        # group worlds by sector cap
        categorized_worlds = categorize_worlds()
        for sector_cap_id, worlds_near_sector_cap in categorized_worlds.items():
            print("Spreading resources around the sector capital with ID", sector_cap_id)
            _apply_resource_distribution(
                _plan_resource_disribution(worlds_near_sector_cap, is_world_producer, is_world_consumer, thing_id))

    else:
        _apply_resource_distribution(_plan_resource_disribution(api.objects_dict, is_world_producer, is_world_consumer, thing_id))

def categorize_worlds():
    worlds = {}  # Key: sector cap ID, Value: List of planet IDs near it
    sector_capitals = {}

    potential_capital_trait_ids = [find_thing("core.sectorCapitalAdministration"), find_thing("core.capitalDesignationAttribute")]


    # step 1: find sector capitals
    for world_id, world in api.objects_dict.items():
        if world["sovereignID"] == api.sovID:
            if world["class"] == "world":
                for trait_id in potential_capital_trait_ids:
                    if world_has_trait(trait_id, world, api.scenario_info, True):
                        worlds[world_id] = {}
                        sector_capitals[world_id] = world

    # step 2: sort worlds
    for world_id, world in api.objects_dict.items():
        if world["sovereignID"] == api.sovID:
            if world["class"] == "world":
                distances = {cap_id: api.dist(world["pos"], cap["pos"]) for cap_id, cap in sector_capitals.items()}
                nearest_cap_id, nearest_cap = min(distances.items(), key=lambda x: x[1])

                worlds[nearest_cap_id][world_id]  = world

    return worlds

if __name__ == '__main__':
    if arguments.warphants:
        print("Spreading warphants!")
        spread_resources(is_world_jumpship_yard, is_world_infantry_academy, warphant_id, segregate_sector_capitals=arguments.same_sector)

    if arguments.cerberuses:
        print("Spreading Cerberus's")
        spread_resources(is_world_ramship_yard, is_world_in_nebula, cerberus_id, segregate_sector_capitals=arguments.same_sector)

    if arguments.minotaurs:
        print("Spreading Minotaurs")
        spread_resources(is_world_starship_yard, is_world_not_in_nebula, minotaur_id, segregate_sector_capitals=arguments.same_sector)
