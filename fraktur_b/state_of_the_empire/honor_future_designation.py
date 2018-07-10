import csv

import anacreonlib
from anacreonlib import Anacreon
import json
import creds
from anacreonlib.exceptions import HexArcException


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

    with open("state_of_my_empire.csv", "r") as data_file:
        csv_data = csv.DictReader(data_file)
        for row in csv_data:
            try:
                if row["future designation"] != "":
                    try:
                        if api.objects_dict[str(row["id"])]["designation"] != int(row["future designation"]):
                            api.designate_world(row["id"], row["future designation"])
                    except KeyError:
                        pass
            except HexArcException as e:
                print(e)
