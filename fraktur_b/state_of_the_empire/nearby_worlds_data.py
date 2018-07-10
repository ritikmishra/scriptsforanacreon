import csv

import anacreonlib
from anacreonlib import Anacreon
import json
import creds

if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    print(api.authtoken)
    games = api.get_game_list()
    # set era to era 4
    api.gameID = creds.ERA_4_ALPHA

    api.sovID = creds.CURRENT_SOV

    scninfo = api.get_game_info()

    sf_calc = {}
    gf_calc = {}

    ground_id_to_name = {}

    space_unit_types = ("fixedUnit", "orbitalUnit", "maneuveringUnit")
    space_id_to_name = {"fixedUnit": {}, "orbitalUnit": {}, "maneuveringUnit": {}}

    aetherium_deposit_levels = {13: "1 abundant", 14: "2 major", 19: "3 minor", 17: "4 trace"}
    chronimium_deposit_levels = {50: "1 abundant", 51: "2 major", 57: "3 minor", 55: "4 trace"}
    ctholon_deposit_levels = {59: "1 abundant", 60: "2 major", 65: "3 minor", 63: "4 trace"}
    hexacarbide_deposit_levels = {126: "1 abundant", 127: "2 major", 133: "3 minor", 131: "4 trace"}
    trillum_deposit_levels = {244: "1 abundant", 245: "2 major", 251: "3 minor", 250: "4 trace"}

    deposit_levels = {"aetherium deposits": aetherium_deposit_levels, "chronimium deposits": chronimium_deposit_levels,
                      "ctholon deposits": ctholon_deposit_levels, "hexacarbide deposits": hexacarbide_deposit_levels,
                      "trillum deposits": trillum_deposit_levels}
    id_to_name = {}

    deposit_level_ids = []

    for deposit_data_dict in deposit_levels.values():
        deposit_level_ids.extend(deposit_data_dict.keys())

    for item in scninfo['scenarioInfo']:
        try:
            if item[u'category'] in space_unit_types:
                sf_calc[int(item['id'])] = float(item['attackValue'])
                space_id_to_name[item[u'category']][int(item['id'])] = str(item['nameDesc'])
                id_to_name[int(item['id'])] = str(item['nameDesc'])
            elif item['category'] == 'groundUnit':
                gf_calc[int(item['id'])] = float(item['attackValue'])
                ground_id_to_name[int(item['id'])] = str(item['nameDesc'])
                id_to_name[int(item['id'])] = str(item['nameDesc'])
        except KeyError:
            continue

    print(id_to_name)

    data_file = open("autonomous_worlds_near_cap.csv", "w", newline="")
    fieldnames = ["id", "name", "nearestCap", "dist", "techLvl", "aetherium deposits", "chronimium deposits",
                  "ctholon deposits", "hexacarbide deposits", "trillum deposits", "sf", "gf"]

    for key, value in space_id_to_name["fixedUnit"].items():
        fieldnames.append(value)

    for key, value in space_id_to_name["orbitalUnit"].items():
        fieldnames.append(value)

    for key, value in ground_id_to_name.items():
        fieldnames.append(value)

    for key, value in space_id_to_name["maneuveringUnit"].items():
        fieldnames.append(value)

    data_file_writer = csv.DictWriter(data_file, delimiter=',', fieldnames=fieldnames)
    data_file_writer.writeheader()

    objects = api.get_objects()

    important_worlds = []
    for world_id, world in objects.items():
        if world[u'class'] == "world":
            if world[u'sovereignID'] == api.sovID:
                if int(world[u'designation']) in (45, 46, 47, 48, 210, 211, 212, 213):
                    important_worlds.append(world)

    # center = anacreon.getObjByID(objects, 55)

    for world_id, world in objects.items():
        if world[u'class'] == "world":
            if int(world[u'sovereignID']) == 28957:
                # dist = anacreon.dist(world[u'pos'], center[u'pos'])
                distances = {cap[u'name']: api.dist(world[u'pos'], cap[u'pos']) for cap in important_worlds}
                min_dist = min(distances.values())
                if min_dist <= 250:
                    associated_cap_name = None
                    for cap_name, dist_to_world in distances.items():
                        if dist_to_world == min_dist:
                            associated_cap_name = cap_name

                    id = world[u'id']
                    name = world[u'name']
                    try:
                        space_forces, ground_forces = api.get_forces(world[u'resources'])
                    except KeyError as e:
                        print("You need to station an explorer at every world in your admin zone!")
                        print(name, "(id", id, " dist", min_dist, associated_cap_name, ") is missing an explorer")
                        raise e
                    tech_level = world[u'techLevel']
                    row = {"id": id, "name": name, "sf": space_forces, "gf": ground_forces, "techLvl": tech_level,
                           "dist": min_dist, "nearestCap": associated_cap_name}

                    currentID = None

                    # track how many existing defenses there are
                    for i, x in enumerate(world[u'resources']):
                        if i % 2 == 0:
                            currentID = x  # x is the id of the resource
                        else:
                            try:
                                row[id_to_name[currentID]] = x
                            except KeyError:
                                continue

                    has_deposit_level = {"aetherium deposits": False,
                                         "chronimium deposits": False,
                                         "ctholon deposits": False,
                                         "hexacarbide deposits": False,
                                         "trillum deposits": False}
                    # track resource concentration
                    for trait in world[u'traits']:
                        if trait in deposit_level_ids:
                            for resource_type, deposit_level_data in deposit_levels.items():
                                if trait in deposit_level_data.keys():
                                    row[resource_type] = deposit_level_data[trait]
                                    has_deposit_level[resource_type] = True

                    for resource_type, has_deposits in has_deposit_level.items():
                        if not has_deposits:
                            row[resource_type] = "5 none"
                    data_file_writer.writerow(row)

                # break

    data_file.flush()
    data_file.close()
