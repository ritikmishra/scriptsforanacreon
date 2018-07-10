import time

import creds
from anacreonlib import Anacreon
from fraktur_b.utils import find_thing


if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    games = api.get_game_list()
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    citadel_desig_id = find_thing("core.citadelDesignation", api)
    citadel_world_ids = []
    for world_id, world in api.objects_dict.items():
        if world["class"] == "world":
            if world["sovereignID"] == api.sovID:
                if world["designation"] == citadel_desig_id:
                    citadel_world_ids.append(world_id)
                    print("World name", world["name"], "is a citadel")

    while True:
        nearby_things = {}
        for thing_id, thing in api.objects_dict.items():
            if thing["class"] == "fleet":
                if thing["sovereignID"] != api.sovID:
                    for citadel_id in citadel_world_ids:
                        citadel = api.get_obj_by_id(citadel_id)
                        if api.dist(thing["pos"], citadel["pos"]) < 100:
                            nearby_things[thing_id] = citadel_id

        for fleet_id, citadel_id in nearby_things.items():
            print("Launching LAMs at ID", fleet_id, "from citadel ID", citadel_id)
            api.launch_lams(citadel_id, fleet_id)

        time.sleep(60)

        api.get_objects()

