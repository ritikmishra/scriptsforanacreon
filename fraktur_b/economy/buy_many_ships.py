import creds
from anacreonlib import Anacreon
from fraktur_b.utils import find_thing


VENDOR_NAME = "UX 6582"
SHIP_UNID = "core.explorerVanguard"
QUANTITY = 100000


def buy_many_ships(api, vendor_name, ship_unid, quantity):
    vendor_planet = api.get_obj_by_name(vendor_name)
    ship_id = find_thing(ship_unid, api)
    api.buy_item(vendor_planet["id"], ship_id, quantity)


if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    games = api.get_game_list()
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    buy_many_ships(api, VENDOR_NAME, SHIP_UNID, QUANTITY)

