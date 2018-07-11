import collections
import json
import queue
import threading

from anacreonlib import Anacreon
import creds
from fraktur_b.utils import find_thing, get_valid_improvement_list


if __name__ == '__main__':
    done_iterating = False
    ConstructionOrder = collections.namedtuple("ConstructionOrder", ["planet_id", "planet_name", "improvement_id", "improvement_name"])

    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    construction_orders = queue.Queue()
    limiting_semaphore = threading.BoundedSemaphore(6)

    def fill_construction_orders():
        while not done_iterating or not construction_orders.empty():  # If there are more to be added or it is not empty
            limiting_semaphore.acquire()

            try:
                construction_order = construction_orders.get()
                print("Building a", construction_order.improvement_name, "on planet", construction_order.planet_name, "(planet ID", construction_order.planet_id, ")")
                api.build_improvement(construction_order.planet_id, construction_order.improvement_id)
            finally:
                limiting_semaphore.release()

    print("Beginning to iterate through planets")
    for planet_id, planet in api.objects_dict.items():
        print("Grabbed new planet")
        if planet["sovereignID"] == api.sovID:
            if planet["class"] == "world":
                valid_improvements = get_valid_improvement_list(planet, api.scenario_info)
                for trait_id in valid_improvements:
                    trait_dict = api.scenario_info[trait_id]
                    try:
                        if trait_dict["role"] == "lifeSupport":
                            planet_name = planet["name"]
                            structure_name = trait_dict["nameDesc"]
                            construction_orders.put(ConstructionOrder(planet_id, planet_name, trait_id, structure_name))
                            print("Added an order for", planet_name, "to get a", structure_name)
                    except KeyError:
                        pass

    print("Done iterating")

    print("Making threads")
    for _ in range(6):
        threading.Thread(target=fill_construction_orders).start()

    print("Created threads")

    done_iterating = True