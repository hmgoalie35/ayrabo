from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string


def send_mail(subject, recipient_list, message, html_message=None, context=None):
    """
    Wrapper around django's send_mail function that treats the plain text message and html message as a django template
    and renders them with the given context.

    :param str subject: Email subject
    :param list recipient_list: Email address or addresses to send the email to
    :param str message: Template name for a plain text email message that will be rendered with the given context.
    Regular django template resolving and syntax rules apply
    :param str html_message: Template name for an html text email message that will be rendered with the given context.
    Regular django template resolving and syntax rules apply
    :param dict context: Context used to render the given templates
    :return: Number of successful emails sent
    """
    context = context or {}
    return django_send_mail(
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        message=render_to_string(message, context),
        html_message=render_to_string(html_message, context) if html_message else None,
    )
