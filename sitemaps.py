from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from django.utils import timezone
from fleet.models import VehicleMarketing, VehicleStatus


class FleetSitemap(Sitemap):
    DEFAULT_CHANGEFREQ = 'never'
    DEFAULT_PRIORITY = 0.5

    def items(self):
        item_objs = [
            {'name': 'fleet', 'kwargs': {}, 'lastmod': ''},
            # {'name': 'gridsolver:index', 'kwargs': {}},
            # {'name': 'blog:page', 'kwargs': {'slug': 'site-notice'}},
            # {'name': 'blog:page', 'kwargs': {'slug': 'privacy-police'}},
        ]
        ready_vehicles = VehicleMarketing.objects.filter(status=VehicleStatus.READY).order_by('-weighting')
        for vehicle in ready_vehicles:
            item_objs.append({'name': 'vehicle', 'kwargs': {'slug': vehicle.slug}, 'priority': 0.75})
        return item_objs

    def location(self, location_map):
        return reverse(location_map['name'], kwargs=location_map['kwargs'])

    def lastmod(self, obj):
        return obj.get('lastmod') or timezone.now()

    def changefreq(self, obj):
        return obj.get('changefreq') or self.DEFAULT_CHANGEFREQ

    def priority(self, obj):
        return obj.get('priority') or self.DEFAULT_PRIORITY


sitemaps = {'fleet': FleetSitemap}
