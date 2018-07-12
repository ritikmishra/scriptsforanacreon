"""
Get data about an admin region about
"""
import csv

import creds
from anacreonlib import Anacreon
from fraktur_b.utils import find_thing, find_many_things, world_has_trait, find_things_world_exports

if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    games = api.get_game_list()
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    potential_capital_trait_ids = [find_thing("core.sectorCapitalAdministration", api), find_thing("core.capitalDesignationAttribute", api)]

    data_dict = {}
    sector_capitals = {}


    # step 1: find sector capitals
    for world_id, world in api.objects_dict.items():
        if world["sovereignID"] == api.sovID:
            if world["class"] == "world":
                for trait_id in potential_capital_trait_ids:
                    if world_has_trait(trait_id, world, api.scenario_info, True):
                        data_dict[world_id] = {}
                        sector_capitals[world_id] = world

    # Sector capital ID's accessible from data_dict.keys()

    # step 2: group worlds

    for world_id, world in api.objects_dict.items():
        if world["sovereignID"] == api.sovID:
            if world["class"] == "world":
                distances = {cap_id: api.dist(world["pos"], cap["pos"]) for cap_id, cap in sector_capitals.items()}
                nearest_cap_id, nearest_cap = min(distances.items(), key=lambda x: x[1])

                world_exports = find_things_world_exports(world, api.scenario_info, True)

                world_production = api.generate_production_info(world_id)

                for item_id in world_exports:
                    if item_id in world_production.keys():
                        if item_id in data_dict[nearest_cap_id].keys():
                            data_dict[nearest_cap_id][item_id] += world_production[item_id]["produced"]
                        else:
                            data_dict[nearest_cap_id][item_id] = world_production[item_id]["produced"]


    # step 3: write csv
    with open("imperial_production.csv", "w") as data_file:
        data_file_writer = csv.DictWriter(data_file, delimiter=',', fieldnames=["sector_cap_name", "unit_name", "watch_prod", "hourly_prod", "daily_prod", "weekly_prod"])
        data_file_writer.writeheader()

        for sector_cap_id, production_data in data_dict.items():
            sector_cap_name = sector_capitals[sector_cap_id]["name"]
            for item_id, qty_produced in production_data.items():
                qty_produced = round(qty_produced, 2)
                data_file_writer.writerow({
                    "sector_cap_name": sector_cap_name,
                    "unit_name": api.scenario_info[item_id]["nameDesc"],
                    "watch_prod": qty_produced,
                    "hourly_prod": qty_produced * 60,
                    "daily_prod": qty_produced * 1440,
                    "weekly_prod": qty_produced * 7 * 1440
                })
        data_file.flush()
        data_file.close()

