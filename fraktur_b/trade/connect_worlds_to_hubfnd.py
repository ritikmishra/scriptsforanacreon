import collections

import anacreonlib
from anacreonlib import Anacreon
import creds

# TL_10_WORLD_CLASS_IDS = [203]
TL8_WORLD_CLASS_IDS = [268, 183, 259]
TL9_DESIGNATION_IDS = []
TL8_DESIGNATION_IDS = [71,]

TechLevelOrder = collections.namedtuple("TechLevelOrder", ["planet_id", "tech_level"])
ExportOrder = collections.namedtuple("ExportOrder", ["planet_id", "planetary_export"])
ImportOrder = collections.namedtuple("ImportOrder", ["planet_id"])


def who_is_trading_with_me(world_obj):
    partner_ids = []
    try:
        for trade_info in world_obj["tradeRoutes"]:
            partner_ids.append(int(trade_info["partnerObjID"]))
        return partner_ids
    except KeyError:
        return []


if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    games = api.get_game_list()
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    hubID = 90
    fndID = 1415

    hub = api.get_obj_by_id(hubID)
    fnd = api.get_obj_by_id(fndID)

    orders = []

    for world_id, world in api.objects_dict.items():
        if u"class" in world.keys():
            if world['sovereignID'] == api.sovID:
                if world['class'] == "world":
                    partner_ids = who_is_trading_with_me(world)

                    if 0 < api.dist(world['pos'], fnd['pos']) < 200 and fndID not in partner_ids:
                        tech_level = 7
                        if world["designation"] in TL9_DESIGNATION_IDS:
                            tech_level = 9
                        elif world[u'worldClass'] in TL8_WORLD_CLASS_IDS or world["designation"] in TL8_DESIGNATION_IDS:
                            tech_level = 8

                        print("Would have made", world["name"], "go to tech level", tech_level)
                        orders.append(TechLevelOrder(world_id, tech_level))
                        # api.set_trade_route(world_id, fndID, "tech", tech_level)

                    if 0 < api.dist(world['pos'], hub['pos']) < 200 and world_id != 90:
                        # World imports everything it needs from hub
                        orders.append(ImportOrder(world_id))
                        # api.set_trade_route(world_id, hubID, "addDefaultRoute")

                        # Find exports
                        try:
                            things_world_exports = []
                            primary_industry_id = api.scenario_info[world[u'designation']]["primaryIndustry"]
                            for thing in world["traits"]:
                                if type(thing) is dict:
                                    if thing["traitID"] == primary_industry_id:
                                        try:
                                            for i, item_id in enumerate(thing["buildData"][::3]):
                                                alloc = thing["buildData"][i * 3 + 1]
                                                cannotBuild = thing["buildData"][i * 3 + 2]

                                                if cannotBuild is None and "Unit" not in api.scenario_info[item_id][
                                                    "category"]:
                                                    things_world_exports.append(item_id)
                                        except KeyError as e:
                                            raise e

                        except KeyError:
                            pass
                            # world does not export anything
                        else:
                            for thing_id in things_world_exports:
                                print("Planet", world["name"], "exports", api.scenario_info[thing_id]["nameDesc"])
                                orders.append(ExportOrder(world_id, thing_id))
                                # api.set_trade_route(hubID, world_id, "consumption", 100, thing_id)

    for order in orders:
        if type(order) is ImportOrder:
            api.set_trade_route(order.planet_id, hubID, "addDefaultRoute")
            print("Order: Import from hub, ID: ", order.planet_id)
        elif type(order) is ExportOrder:
            api.set_trade_route(hubID, order.planet_id, "consumption", 100, order.planetary_export)
            print("Order: Export resource ID", order.planetary_export, "to hub, planet ID: ", order.planet_id)
        elif type(orders) is TechLevelOrder:
            print("Order: Import tech level", order.tech_level, "to planet ID: ", order.planet_id)
            api.set_trade_route(order.planet_id, fndID, "tech", order.tech_level)
