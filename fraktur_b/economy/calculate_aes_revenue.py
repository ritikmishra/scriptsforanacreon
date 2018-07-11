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

    trading_hub_desigs = (
        find_thing("core.tradingHubDesignation", api),
        find_thing("core.sectorCapitalTradeDesignation", api),
        find_thing("core.capitalTradeDesignation", api)
    )

    total_revenue = 0

    planet_ids_to_look_at = []
    for world_id, world in api.objects_dict.items():
        if world["sovereignID"] == api.sovID:
            if world["class"] == "world":
                if world["designation"] in trading_hub_desigs:
                    for trade_route in world["tradeRoutes"]:
                        if api.objects_dict[trade_route["partnerObjID"]]["sovereignID"] != api.sovID:
                            planet_ids_to_look_at.append(trade_route["partnerObjID"])

    for world_id in planet_ids_to_look_at:
        world = api.objects_dict[world_id]

        for trade_route in world["tradeRoutes"]:
            if "purchases" in trade_route.keys():
                for i, item_id in enumerate(trade_route["purchases"][::4]):
                    actually_sold = trade_route["purchases"][4 * i + 3]
                    goal = trade_route["purchases"][4 * i + 1]
                    money_earned = trade_route["purchases"][4 * i + 2]
                    print("Selling", goal if actually_sold is None else actually_sold, "units of",
                          api.scenario_info[item_id]["nameDesc"], "for {:,.2f}".format(money_earned), "aes")
                    total_revenue += money_earned

    print("Earned {:,.2f} last watch".format(total_revenue))
    # print("Current amount of cash: {:,.2f}".format(total_revenue))
    daily_earnings = total_revenue * 1440
    print("Projected earnings of {:,.2f} per day".format(daily_earnings))
    print("That is approximately {:,.2f} Undines per day".format(daily_earnings / 190))
    print("That is approximately {:,.2f} Minotaurs per day".format(daily_earnings / 85))
