from fleet.models import VehicleMarketing, VehiclePicture, VehicleVideo
from marketing.models import NewsItem, NewsletterSubscription, Tweet

FRONT_MODELS = [
    VehicleMarketing,
    VehiclePicture,
    VehicleVideo,
    NewsItem,
    NewsletterSubscription,
    Tweet,
]


class FrontDBRouter(object):

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        front_model_names = [m._meta.model_name for m in FRONT_MODELS]
        if db != 'default' and model_name not in front_model_names:
            return False
        if db == 'default' and model_name in front_model_names:
            return False
        return None

    def db_for_read(self, model, **hints):
        """ reading model from front """
        if model in FRONT_MODELS:
            return 'front'
        return None

    def db_for_write(self, model, **hints):
        """ writing model to front """
        if model in FRONT_MODELS:
            return 'front'
        return None

    # def allow_relation(self, obj1, obj2, **hints):
    #     return True
