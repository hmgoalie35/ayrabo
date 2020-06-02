class SportNotConfiguredException(Exception):
    def __init__(self, sport):
        """
        Allow error message customization based on the sport that caused the error.

        :param sport: The sport that isn't configured properly.
        """
        self.sport = sport
        self.message = f'Site configuration for {self.sport.name} is still in progress.'
