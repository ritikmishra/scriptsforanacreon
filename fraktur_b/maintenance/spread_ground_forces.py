from anacreonlib import Anacreon
import json
import creds

SELECTED_CAPITAL = 90
api = None

def find_thing(unid):
    # find ID of warphant
    for type_id, type_obj in api.scenario_info.items():
        if type_obj["unid"] == unid:
            return type_id
    else:
        raise Exception("Thing not found ???")


def main():
    # Authenticate
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    warphant_id = find_thing("core.jumptransportWarphant")




if __name__ == '__main__':
    main()
