class SportNotConfiguredException(Exception):
    def __init__(self, sport):
        """
        Allow error message customization based on the sport that caused the error.

        :param sport: The sport that isn't configured properly.
        """
        self.sport = sport
        self.message = "{} hasn't been configured correctly in our system. " \
                       "If you believe this is an error please contact us.".format(self.sport)
