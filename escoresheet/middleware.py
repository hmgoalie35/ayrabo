import pytz
from django.conf import settings
from django.utils import timezone
from django.utils import translation


class TranslationMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and hasattr(request.user, 'userprofile'):
            language_code = request.user.userprofile.language
        else:
            language_code = translation.get_language_from_request(request)
        request.session[translation.LANGUAGE_SESSION_KEY] = language_code
        translation.activate(language_code)
        return None


class TimezoneMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and hasattr(request.user, 'userprofile'):
            tz = request.user.userprofile.timezone
        else:
            tz = settings.TIME_ZONE
        timezone.activate(pytz.timezone(tz))
        return None
