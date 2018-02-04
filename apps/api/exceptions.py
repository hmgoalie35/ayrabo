from rest_framework import exceptions, status


class SportNotConfiguredException(exceptions.APIException):
    def __init__(self, sport, *args, **kwargs):
        self.default_detail = '{} is not currently configured'.format(sport.name)
        super().__init__(*args, **kwargs)

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'sport_not_configured'
