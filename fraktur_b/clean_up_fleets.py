import json
import threading
import queue
import sys
import time
from anacreonlib import Anacreon
import creds
from anacreonlib.exceptions import HexArcException
from fraktur_b import utils
from fraktur_b.utils import find_thing, get_valid_improvement_list

if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    print(api.authtoken)

    gameinfo = api.get_game_info()
    api.get_objects()

    fleets_to_disband = queue.Queue()

    for thing_id, thing in api.objects_dict.items():
        if thing["class"] == "fleet":
            if thing["sovereignID"] == api.sovID:
                if "anchorObjID" in thing.keys():
                    if api.objects_dict[thing["anchorObjID"]]["sovereignID"] == api.sovID:
                        fleets_to_disband.put((thing_id, thing["anchorObjID"]))

    def process_disband_orders():
        while not fleets_to_disband.empty():
            print("Disbanding a fleet")
            api.disband_fleet(*fleets_to_disband.get())

    for _ in range(5):
        threading.Thread(target=process_disband_orders).start()