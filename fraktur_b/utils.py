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
