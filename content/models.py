from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.blocks import CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.admin.panels import FieldPanel

from marketing.views import NavMenuMixin


# TODO: change "url" to "slugurl" references to CMS pages once all are created

class CMSPage(NavMenuMixin, Page):
    template = 'front_site/cms_page.html'

    body = StreamField([
        ('heading', CharBlock(classname="full title", icon='title')),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('table', TableBlock()),
        ('html', RawHTMLBlock()),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['content'] = site_content.content
        return context