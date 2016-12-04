import pytz
from django.conf import settings
from django.utils import timezone, translation
from django.utils.deprecation import MiddlewareMixin


class TranslationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated() and hasattr(request.user, 'userprofile'):
            language_code = request.user.userprofile.language
        else:
            language_code = translation.get_language_from_request(request)
        request.session[translation.LANGUAGE_SESSION_KEY] = language_code
        translation.activate(language_code)
        return None


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated() and hasattr(request.user, 'userprofile'):
            tz = request.user.userprofile.timezone
        else:
            tz = settings.TIME_ZONE
        timezone.activate(pytz.timezone(tz))
        return None
