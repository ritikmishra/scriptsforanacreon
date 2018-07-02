import json
from copy import copy

from anacreonlib import Anacreon
import creds
import time

from fraktur_b.utils import make_notification

FLEET_NAME = "Despongifier"

api = Anacreon(creds.USERNAME, creds.PASSWORD)
api.gameID = creds.ERA_4_ALPHA
api.sovID = creds.CURRENT_SOV
api.get_game_info()

api.get_objects()


def sort_by_distance(world_id):
    return api.dist(api.get_obj_by_id(world_id)["pos"], invasion_fleet_obj["pos"])


def sort_by_space_force(world_id):
    return api.get_forces(api.get_obj_by_id(world_id)["resources"])[0]


if __name__ == '__main__':

    with open("planet_ids_to_invade.json", "r") as f:
        planet_ids_to_invade = copy(json.load(f))
        f.close()
        del f

    planet_ids_to_invade = [planet_id for planet_id in planet_ids_to_invade if
                            api.get_obj_by_id(planet_id)["sovereignID"] == 1]

    print(planet_ids_to_invade)
    invasion_fleet_obj = api.get_obj_by_name(FLEET_NAME)

    while len(planet_ids_to_invade) > 0:
        closest_planet_id = min(planet_ids_to_invade,
                                key=sort_by_space_force)

        api.set_fleet_destination(invasion_fleet_obj["id"], closest_planet_id)
        eta = api.get_fleet_eta(api.get_obj_by_id(invasion_fleet_obj["id"]))

        current_planet = api.get_obj_by_id(closest_planet_id)
        make_notification("Forces on their way to " + str(current_planet["name"]), "are travelling to", current_planet)

        print("Waiting", eta, "seconds while fleet goes to planet ID", closest_planet_id)
        time.sleep(eta + 1)

        current_planet = api.get_obj_by_id(closest_planet_id, refresh=True)
        print("Arrived at planet ID", closest_planet_id)

        api.attack(closest_planet_id, "invasion")
        make_notification("Forces launch attack on" + str(current_planet["name"]), "have arrived and started invading",
                          current_planet)
        print("Attacking planet ID", closest_planet_id)

        # wait for attack to be over
        tactical = api.get_tactical(closest_planet_id)

        # transport_tactical_ids = []
        # for grouping in tactical:
        #     if "cargo" in grouping.keys():
        #         transport_tactical_ids.append(int(grouping["id"]))
        # time.sleep(8)
        #
        # print("Landing units")
        # for id in transport_tactical_ids:
        #     api.tactical_order("land", closest_planet_id, id)
        #

        while len([x for x in tactical if x["class"] == "battlePlan"]) > 0:
            print("Waiting 5 secs")
            time.sleep(5)
            tactical = api.get_tactical(closest_planet_id)

        planet_ids_to_invade.remove(closest_planet_id)
        print("Conquered planet ID", closest_planet_id)
        print(str(len(planet_ids_to_invade)) + " planets left to invade")
        make_notification("Forces have conquered" + str(current_planet["name"]), "have successfully conquered",
                          current_planet)

    with open('planet_ids_to_invade.json', 'w') as fp:
        json.dump(planet_ids_to_invade, fp, indent=4, separators=(',', ': '))
