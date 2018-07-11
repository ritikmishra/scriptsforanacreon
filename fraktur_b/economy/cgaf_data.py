"""
Get data about an admin region about
"""
import creds
from anacreonlib import Anacreon
from fraktur_b.utils import find_thing, find_many_things

SECCAP_NAME = "whales"

if __name__ == '__main__':
    api = Anacreon(creds.USERNAME, creds.PASSWORD)
    games = api.get_game_list()
    api.gameID = creds.ERA_4_ALPHA
    api.sovID = creds.CURRENT_SOV

    api.get_game_info()
    api.get_objects()

    # organic_food = find_thing("core.organicFood", api)
    # durable_goods = find_thing("core.durableGoods", api)
    # luxuries = find_thing("core.luxuries", api)

    organic_food, durable_goods, luxuries = find_many_things(api, "core.organicFood", "core.durableGoods",
                                                             "core.luxuries")

    id_to_name = {organic_food: "organic food", durable_goods: "durable goods", luxuries: "luxuries"}
    consumer_goods_ids = [organic_food, durable_goods, luxuries]
    cgaf_desig_id = find_thing("core.consumerGoodsDesignation", api)
    autonomous_desig_id = find_thing("core.autonomousDesignation", api)

    produced_tally = {good_id: 0 for good_id in consumer_goods_ids}
    consumed_tally = {good_id: 0 for good_id in consumer_goods_ids}
    exported_tally = {good_id: 0 for good_id in consumer_goods_ids}

    for world_id, world in api.objects_dict.items():
        if world["class"] == "world":
            if world["sovereignID"] == api.sovID:
                if world["designation"] != autonomous_desig_id:
                    if world_id == 349:
                        print("woo!")
                    prod_info = api.generate_production_info(world_id)

                    world_is_cgaf = world["designation"] == cgaf_desig_id

                    # calculcate consumed
                    for good_id in consumer_goods_ids:
                        try:
                            consumed_tally[good_id] += prod_info[good_id]["consumed"]
                        except KeyError:
                            pass

                        if world_is_cgaf:
                            # calculate exported
                            # calculate produced
                            try:
                                produced_tally[good_id] += prod_info[good_id]["produced"]
                                exported_tally[good_id] += prod_info[good_id]["exported"]

                            except KeyError:
                                pass

    produced_consumed_disparity = {}
    produced_exported_disparity = {}

    print("A total of:")
    for good_id, qty_produced in produced_tally.items():
        produced_consumed_disparity[good_id] = qty_produced - consumed_tally[good_id]
        produced_exported_disparity[good_id] = qty_produced - exported_tally[good_id]
        print("\t", int(qty_produced), id_to_name[good_id])

    print("was produced")
    print()
    print("A total of:")
    for good_id, qty_consumed in consumed_tally.items():
        print("\t", int(qty_consumed), id_to_name[good_id])

    print("was consumed")
    print()
    print("Surplus production:")
    for good_id, qty in produced_consumed_disparity.items():
        print("\t", int(qty), id_to_name[good_id])
    print()
    print()
    print("Non-exported content:")
    for good_id, qty in produced_exported_disparity.items():
        print("\t", int(qty), id_to_name[good_id])
