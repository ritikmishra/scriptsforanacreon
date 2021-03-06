import csv

import anacreonlib
from anacreonlib import Anacreon
import json
import creds


def find_thing(unid):
    # find ID of warphant
    for type_id, type_obj in api.scenario_info.items():
        if type_obj["unid"] == unid:
            return type_id
    else:
        raise Exception("Thing not found ???")


if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    # set era to era 4
    api.gameID = creds.ERA_4_ALPHA

    api.sovID = creds.CURRENT_SOV

    scninfo = api.get_game_info()

    sf_calc = {}
    gf_calc = {}

    ground_id_to_name = {}

    space_unit_types = ("fixedUnit", "orbitalUnit", "maneuveringUnit")
    space_id_to_name = {"fixedUnit": {}, "orbitalUnit": {}, "maneuveringUnit": {}}

    aetherium_deposit_levels = {
        find_thing("core.aetheriumAbundant"): "1 abundant",
        find_thing("core.aetheriumCommon"): "2 major",
        find_thing("core.aetheriumUncommon"): "3 minor",
        find_thing("core.aetheriumRare"): "4 trace"
    }

    chronimium_deposit_levels = {
        find_thing("core.chronimiumAbundant"): "1 abundant",
        find_thing("core.chronimiumCommon"): "2 major",
        find_thing("core.chronimiumUncommon"): "3 minor",
        find_thing("core.chronimiumRare"): "4 trace"
    }

    ctholon_deposit_levels = {
        find_thing("core.chtholonAbundant"): "1 abundant",
        find_thing("core.chtholonCommon"): "2 major",
        find_thing("core.chtholonUncommon"): "3 minor",
        find_thing("core.chtholonRare"): "4 trace"
    }

    hexacarbide_deposit_levels = {
        find_thing("core.hexacarbideAbundant"): "1 abundant",
        find_thing("core.hexacarbideCommon"): "2 major",
        find_thing("core.hexacarbideUncommon"): "3 minor",
        find_thing("core.hexacarbideRare"): "4 trace"
    }

    trillum_deposit_levels = {
        find_thing("core.trillumAbundant"): "1 abundant",
        find_thing("core.trillumCommon"): "2 major",
        find_thing("core.trillumUncommon"): "3 minor",
        find_thing("core.trillumRare"): "4 trace"
    }

    deposit_levels = {"aetherium deposits": aetherium_deposit_levels, "chronimium deposits": chronimium_deposit_levels,
                      "ctholon deposits": ctholon_deposit_levels, "hexacarbide deposits": hexacarbide_deposit_levels,
                      "trillum deposits": trillum_deposit_levels}
    id_to_name = {}
    defense_ids = []

    deposit_level_ids = []

    for deposit_data_dict in deposit_levels.values():
        deposit_level_ids.extend(deposit_data_dict.keys())

    for item in scninfo['scenarioInfo']:
        try:
            if item[u'category'] in space_unit_types:
                defense_ids.append(int(item['id']))
                sf_calc[int(item['id'])] = float(item['attackValue'])
                space_id_to_name[item[u'category']][int(item['id'])] = str(item['nameDesc'])
            elif item['category'] == 'groundUnit':
                defense_ids.append(int(item['id']))
                gf_calc[int(item['id'])] = float(item['attackValue'])
                ground_id_to_name[int(item['id'])] = str(item['nameDesc'])
            id_to_name[int(item['id'])] = str(item['nameDesc'])
        except KeyError:
            continue

    print(id_to_name)

    data_file = open("state_of_my_empire.csv", "w", newline="")
    fieldnames = ["id", "name", "nearestCap", "dist", "techLvl", "current designation", "future designation",
                  "aetherium deposits", "chronimium deposits", "ctholon deposits", "hexacarbide deposits",
                  "trillum deposits", "sf", "gf"]

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

    api.get_objects()

    important_worlds = []
    for world_id, world in api.objects_dict.items():
        if world[u'class'] == "world":
            if world["sovereignID"] == api.sovID:
                try:
                    if api.scenario_info[int(world[u'designation'])]["role"] in ("imperialCapital", "sectorCapital"):
                        important_worlds.append(world)
                except KeyError:
                    pass

    # center = anacreon.getObjByID(objects, 55)

    for world_id, world in api.objects_dict.items():
        if world[u'class'] == "world":
            if int(world[u'sovereignID']) == api.sovID:
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
                    space_forces, ground_forces = api.get_forces(world[u'resources'])
                    tech_level = world[u'techLevel']
                    row = {"id": id, "name": name, "sf": space_forces, "gf": ground_forces, "techLvl": tech_level,
                           "dist": min_dist, "nearestCap": associated_cap_name, "future designation": ""}

                    currentID = None

                    # track how many existing defenses there are
                    for i, x in enumerate(world[u'resources']):
                        if i % 2 == 0:
                            currentID = x  # x is the id of the resource
                        else:
                            try:
                                if currentID in defense_ids:
                                    row[id_to_name[currentID]] = x
                            except KeyError:
                                continue

                    # track current designation
                    row["current designation"] = id_to_name[world[u'designation']]

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
