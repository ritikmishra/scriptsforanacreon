import time

import creds
from anacreonlib import Anacreon
from fraktur_b.utils import make_notification

FLEET_NAME = "Galactic Exploration Fleet"
TARGET_POINT = (1600, None)
DIST_REQUIREMENT = 200


def fulfills_dist_requirement(world_pos, fleet_pos):
    return DIST_REQUIREMENT is None or api.dist(world_pos, fleet_pos) <= DIST_REQUIREMENT


def send_fleet_to_point(api: Anacreon, fleet_name: str, x: float = None, y: float = None) -> None:
    previous_best_world_id = None

    fleet_obj = api.get_obj_by_name(fleet_name, refresh=True)
    while True:
        # Find the world closest to the target point
        distances = {}
        for world_id, world in api.objects_dict.items():
            if world["class"] == "world":  # cannot target moving objects
                if fulfills_dist_requirement(world["pos"], fleet_obj["pos"]):
                    dx = 0
                    dy = 0

                    if x is not None:
                        dx = (world["pos"][0] - x) ** 2

                    if y is not None:
                        dy = (world["pos"][1] - y) ** 2

                    distances[world_id] = dx + dy

        best_world_id, best_dist = min(distances.items(), key=(lambda x: x[1]))

        # Get information about that world
        best_world_obj = api.get_obj_by_id(best_world_id)

        # Go there
        api.set_fleet_destination(fleet_obj["id"], best_world_id)

        # If we're at the same spot then we are as close as we can
        try:
            if previous_best_world_id == best_world_id and fleet_obj["anchorObjID"] == previous_best_world_id:
                break
        except KeyError:
            pass
        finally:
            previous_best_world_id = best_world_id

        print("Going to planet", best_world_obj["name"], "(ID", best_world_id, ")")
        make_notification("Explorers going to " + best_world_obj["name"], "of exploration are travelling to",
                          best_world_obj)

        # Wait until the watch updates i.e our fleet moves
        fleet_obj = api.get_obj_by_name(fleet_name)

        time.sleep(api.get_fleet_eta(fleet_obj) % 60)

        fleet_obj = api.get_obj_by_name(fleet_name, refresh=True)


if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()

    send_fleet_to_point(api, FLEET_NAME, TARGET_POINT[0], TARGET_POINT[1])
