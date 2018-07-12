import json
from typing import Dict, Any

try:
    from gi.repository import Notify  # Specific to gnome, a Linux Desktop Environment
except ImportError:
    def make_notification(title, action, planet_obj):
        # pass
        body = "Our forces " + str(action) + " the planet " + str(planet_obj["name"]) + " (ID " + str(
            planet_obj["id"]) + ")"

        make_notification_base(title, body)


    def make_notification_base(title, body):
        print(title + "\n" + body + "\n\n\n")

else:
    def make_notification(title, action, planet_obj):
        # pass
        body = "Our forces " + str(action) + " the planet " + str(planet_obj["name"]) + " (ID " + str(
            planet_obj["id"]) + ")"

        make_notification_base(title, body)


    def make_notification_base(title, body):
        Notify.init(title)
        notification = Notify.Notification.new(title,
                                               body,
                                               "dialog-information")
        notification.show()


def find_thing(unid, api):
    # find ID of warphant
    for type_id, type_obj in api.scenario_info.items():
        if type_obj["unid"] == unid:
            return type_id
    else:
        raise Exception("Thing not found ???")


def find_many_things(api, *args):
    ret = [None for _ in args]
    # find ID of warphant
    for type_id, type_obj in api.scenario_info.items():
        if type_obj["unid"] in args:
            ret[args.index(type_obj["unid"])] = type_id
    if None not in ret:
        return ret
    raise Exception("Thing not found ???")


def squashed_trait_dict(world):
    trait_dict = {}
    for trait in world["traits"]:
        if type(trait) is int:
            trait_dict[trait] = trait
        elif type(trait) is dict:
            trait_dict[trait["traitID"]] = trait

    return trait_dict


def trait_inherits_from_trait(trait_a, trait_b, scninfo):
    """
    Checks if trait_a inherits from trait_b i.e
    trait_a extends trait_b
    trait_a inheritsFrom trait_b
    :param trait_a:
    :param trait_b:
    :return:
    """
    try:
        return trait_b in scninfo[trait_a]["inheritFrom"] or any(
            [trait_inherits_from_trait(trait, trait_b, scninfo) for trait in scninfo[trait_a]["inheritFrom"]])
    except KeyError:
        return False


def world_has_trait(target_trait_id, world_dict, scninfo, include_world_characteristics = False):
    """
    Returns true if a world has the trait or a trait inheriting from it
    :param target_trait_id: The ID of the trait
    :param world_dict: The dictionary representing the world
    :return: bool
    """
    trait_dict = squashed_trait_dict(world_dict)
    for trait_id, trait in trait_dict.items():
        if target_trait_id == trait_id:
            return True
        elif trait_inherits_from_trait(trait_id, target_trait_id, scninfo):
            return True
    if include_world_characteristics:
        world_class = world_dict["worldClass"]
        world_designation = world_dict["designation"]
        world_culture = world_dict["culture"]
        if target_trait_id == world_class or target_trait_id == world_designation or target_trait_id == world_culture:
            return True
        if trait_inherits_from_trait(world_class, target_trait_id, scninfo) \
                or trait_inherits_from_trait(world_designation, target_trait_id, scninfo) \
                or trait_inherits_from_trait(world_culture, target_trait_id, scninfo):
            return True

    return False


def type_supercedes_type(trait_a, trait_b, scninfo):
    try:
        return trait_b in scninfo[trait_a]["buildUpgrade"] or any([type_supercedes_type(trait, trait_b, scninfo) for trait in scninfo[trait_a]["buildUpgrade"]])
    except KeyError:
        return False

def trait_under_construction(trait_dict, trait_id):
    if trait_id not in trait_dict.keys():
        return False
    if type(trait_dict[trait_id]) is int:
        return False
    if "buildComplete" in trait_dict[trait_id].keys():
        return True

def get_valid_improvement_list(world, scninfo: Dict[int, Dict[str, Any]]):
    valid_improvement_ids = []
    trait_dict = squashed_trait_dict(world)

    for thing_id, thing in scninfo.items():
        if thing is not None and "category" in thing.keys() \
                and thing["category"] == "improvement" \
                and "npeOnly" not in thing.keys() \
                and "designationOnly" not in thing.keys() \
                and "buildTime" in thing.keys() \
                and thing_id not in trait_dict.keys() \
                and world["techLevel"] >= thing["minTechLevel"]:
            if "buildUpgrade" in thing.keys():
                # Check if we have the predecessor structure
                for potential_predecessor in thing["buildUpgrade"]:
                    if world_has_trait(potential_predecessor, world, scninfo, True):
                        if "buildComplete" not in trait_dict[potential_predecessor]:
                            break
                else:
                    continue
            if "buildRequirements" in thing.keys():
                # Check we have requirements
                all_requirements_found = True
                for requirement_id in thing["buildRequirements"]:
                    if not world_has_trait(requirement_id, world, scninfo, True):
                        all_requirements_found = False
                        break
                    elif world_has_trait(requirement_id, world, scninfo, True) and trait_under_construction(trait_dict, trait_id):
                        all_requirements_found = False
                        break
                if not all_requirements_found:
                    continue

            if "buildExclusions" in thing.keys():
                # Check if we are banned from doing so
                exclusion_found = False
                for exclusion_id in thing["buildExclusions"]:
                    if world_has_trait(exclusion_id, world, scninfo, True):
                        exclusion_found = True
                        break
                if exclusion_found:
                    continue

            # Check if we are superceded by something
            superceded_by_another_structure = False
            for trait_id in trait_dict.keys():
                if type_supercedes_type(trait_id, thing_id, scninfo):
                    superceded_by_another_structure = True
                    break
            if superceded_by_another_structure:
                continue

            if thing["role"] == "techAdvance":
                if thing["techLevelAdvance"] <= world["techLevel"]:
                    # if this is a tech advancement structure, check if we can build it
                    continue

            # we have not continue'd so it'd ok
            valid_improvement_ids.append(thing_id)

    return valid_improvement_ids


def find_things_world_exports(world, scninfo, include_units=False):
    things_world_exports = []
    try:
        primary_industry_id = scninfo[world[u'designation']]["primaryIndustry"]
        for thing in world["traits"]:
            if type(thing) is dict and thing["traitID"] == primary_industry_id:
                try:
                    for i, item_id in enumerate(thing["buildData"][::3]):
                        alloc = thing["buildData"][i * 3 + 1]
                        cannotBuild = thing["buildData"][i * 3 + 2]

                        if cannotBuild is None and (include_units or "Unit" not in scninfo[item_id]["category"]):
                            things_world_exports.append(item_id)
                except KeyError as e:
                    raise e

    except KeyError:
        pass

    return things_world_exports


