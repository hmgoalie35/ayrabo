from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from sports.models import SportRegistration


class SportRegistrationCompleteMiddleware(object):
    """
    This middleware makes sure a user registered for at least one sport. It also checks to see if a user has registered
    for a sport but has not finished the sport registration (i.e. filling out Player, Coach, Referee, Manager specific)
    information
    """

    def process_request(self, request):
        create_sport_registration_url = reverse('sport:create_sport_registration')
        finish_sport_registration_url = reverse('sport:finish_sport_registration')

        whitelisted_urls = [reverse('account_logout'), create_sport_registration_url, finish_sport_registration_url]

        # debug_toolbar wasn't working properly because of my custom middleware so let all debug_toolbar
        # requests through
        if '__debug__' in request.path:
            return None

        # Do not apply this middleware to anonymous users, or for any request to a whitelisted url. An infinite redirect
        # loop would occur if sport_registration_url wasn't whitelisted
        if request.user.is_authenticated() and request.path not in whitelisted_urls:
            sport_registrations = SportRegistration.objects.filter(user=request.user)
            incomplete_sport_registrations = SportRegistration.objects.filter(user=request.user, is_complete=False)
            if not sport_registrations.exists():
                return redirect(create_sport_registration_url)
            elif incomplete_sport_registrations.exists():
                return redirect(finish_sport_registration_url)
            else:
                # The user's account is "complete"
                return None
        return None
