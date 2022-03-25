from django.contrib.sitemaps import Sitemap


class FleetSitemap(Sitemap):
    def items(self):
        return [
            {'name': 'blog:index', 'kwargs': {}},
            {'name': 'gridsolver:index', 'kwargs': {}},
            {'name': 'blog:page', 'kwargs': {'slug': 'site-notice'}},
            {'name': 'blog:page', 'kwargs': {'slug': 'privacy-police'}},
        ]

    def location(self, location_map):
        return reverse(location_map['name'], kwargs=location_map['kwargs'])