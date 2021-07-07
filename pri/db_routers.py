from backoffice.models import Vehicle


class BackOfficeDBRouter(object):

    def db_for_read(self, model, **hints):
        """ reading Vehicle from backoffice """
        if model == Vehicle:
            return 'backoffice'
        return None

    def db_for_write(self, model, **hints):
        """ writing Vehicle to backoffice """
        if model == Vehicle:
            return 'backoffice'
        return None

    # def allow_relation(self, obj1, obj2, **hints):
    #     return True
