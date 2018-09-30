from django.conf import settings


def support_contact(request):
    return {'support_contact': settings.SUPPORT_CONTACT}
