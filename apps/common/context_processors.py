from django.conf import settings


def support_contact(request):
    return {'support_contact': settings.SUPPORT_CONTACT}


def sports_for_user(request):
    user = request.user
    sports = []
    if user.is_authenticated:
        for sr in user.get_sport_registrations():
            sport = sr.sport
            if sport not in sports:
                sports.append(sport)
    return {'sports_for_user': sports}
