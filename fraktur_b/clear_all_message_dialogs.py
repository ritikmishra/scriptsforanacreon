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

    for hist_id, hist_obj in api.history_dict.items():
        print(hist_obj)
        api.set_history_read(hist_id)
