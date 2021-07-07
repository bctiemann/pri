from fleet.models import VehicleMarketing


class BackOfficeDBRouter(object):

    def db_for_read(self, model, **hints):
        """ reading VehicleMarketing from front """
        if model == VehicleMarketing:
            return 'front'
        return None

    def db_for_write(self, model, **hints):
        """ writing VehicleMarketing to front """
        if model == VehicleMarketing:
            return 'front'
        return None

    # def allow_relation(self, obj1, obj2, **hints):
    #     return True
