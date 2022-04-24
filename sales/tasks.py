import os
import importlib
from zipfile import ZipFile
from pwd import getpwnam
from PIL import Image
from uuid import uuid4

from django.conf import settings
from django.core import mail
from django.template import Context
from django.template.loader import get_template

# from celery import shared_task
# from celery.utils.log import get_task_logger

import logging
logger = logging.getLogger(__name__)

TEXT_TEMPLATE = 'email/notification.txt'
HTML_TEMPLATE = 'email/notification.html'
FROM_ADDRESS = settings.SITE_EMAIL


# @shared_task
def send_email(
        recipients,
        subject,
        context,
        text_template=TEXT_TEMPLATE,
        html_template=HTML_TEMPLATE,
        attachments=None,
        bcc=None,
        from_address=FROM_ADDRESS,
):
    if settings.DEBUG:
        recipients = [settings.DEBUG_EMAIL]

    plaintext = get_template(text_template)
    htmly = get_template(html_template)
    connection = mail.get_connection()
    connection.open()
    for recipient in recipients:
        text_content = plaintext.render(context)
        html_content = htmly.render(context)
        msg = mail.EmailMultiAlternatives(subject, text_content, from_address, [recipient], bcc=bcc)
        msg.attach_alternative(html_content, "text/html")
        if attachments:
            for attachment in attachments:
                msg.attach(**attachment)

        msg.send()
        logger.info('Sending email "{0}" to {1}...'.format(subject, recipient))

    connection.close()
