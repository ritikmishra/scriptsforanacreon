
try:
    from gi.repository import Notify  # Specific to gnome, a Linux Desktop Environment
except ImportError:
    def make_notification(title, action, planet_obj):
        # pass
        body = "Our forces " + str(action) + " the planet " + str(planet_obj["name"]) + " (ID " + str(
            planet_obj["id"]) + ")"

        make_notification_base(title, body)


    def make_notification_base(title, body):
        print(title + "\n" + body + "\n\n\n")

else:
    def make_notification(title, action, planet_obj):
        # pass
        body = "Our forces " + str(action) + " the planet " + str(planet_obj["name"]) + " (ID " + str(
            planet_obj["id"]) + ")"

        make_notification_base(title, body)


    def make_notification_base(title, body):
        Notify.init(title)
        notification = Notify.Notification.new(title,
                                               body,
                                               "dialog-information")
        notification.show()


def find_thing(unid, api):
    # find ID of warphant
    for type_id, type_obj in api.scenario_info.items():
        if type_obj["unid"] == unid:
            return type_id
    else:
        raise Exception("Thing not found ???")

def find_many_things(api, *args):
    ret = [None for _ in args]
    # find ID of warphant
    for type_id, type_obj in api.scenario_info.items():
        if type_obj["unid"] in args:
            ret[args.index(type_obj["unid"])] = type_id
    if None not in ret:
        return ret
    raise Exception("Thing not found ???")

