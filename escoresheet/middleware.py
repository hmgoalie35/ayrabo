import pytz
from django.conf import settings
from django.utils import timezone, translation
from django.utils.deprecation import MiddlewareMixin


class TimezoneAndTranslationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            userprofile = request.user.userprofile
            language_code = userprofile.language
            tz = userprofile.timezone
        else:
            language_code = translation.get_language_from_request(request)
            tz = settings.TIME_ZONE
        request.session[translation.LANGUAGE_SESSION_KEY] = language_code
        translation.activate(language_code)

        timezone.activate(pytz.timezone(tz))
        return None
