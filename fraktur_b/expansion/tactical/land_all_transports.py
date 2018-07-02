import json
import sys

from anacreonlib import Anacreon
import creds
import time

# ALLOWED_RESOURCES = [1, 26, 148, 99, 141, 100, 101]
CIRCLE_CENTER_ID = 90

api = Anacreon(creds.USERNAME, creds.PASSWORD)
api.gameID = creds.ERA_4_ALPHA
api.sovID = creds.CURRENT_SOV

api.get_game_info()
api.get_objects()

PLANET_NAME = "UX 3382"
if __name__ == '__main__':
    tactical = api.get_tactical(api.get_obj_by_name(PLANET_NAME)["id"])
    raise NotImplementedError()
