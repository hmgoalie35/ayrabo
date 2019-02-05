from ayrabo.utils.exceptions import SportNotConfiguredException
from seasons.forms import HockeySeasonRosterCreateUpdateForm
from seasons.models import HockeySeasonRoster


SPORT_SEASON_ROSTER_MODEL_MAPPINGS = {
    'Ice Hockey': HockeySeasonRoster
}

SPORT_SEASON_ROSTER_CREATE_UPDATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeySeasonRosterCreateUpdateForm
}


def get_season_roster_model_cls(sport):
    """
    Gets the appropriate season roster model for the given sport.

    :param sport: Sport that will be used to fetch the correct model class.
    :raises SportNotConfiguredException: If a season roster model class can't be found for the given sport.
    :return: Season roster model class for the specified sport.
    """
    model_cls = SPORT_SEASON_ROSTER_MODEL_MAPPINGS.get(sport.name)
    if model_cls is None:
        raise SportNotConfiguredException(sport)
    return model_cls


def get_season_roster_create_update_form_cls(sport):
    """
    Get the appropriate season roster create/update form for the given sport.

    :param sport: Sport that will be used to fetch the correct form class.
    :raises SportNotConfiguredException: If a season roster form class can't be found for the given sport.
    :return: Season roster create/update form class for the specified sport.
    """
    form_cls = SPORT_SEASON_ROSTER_CREATE_UPDATE_FORM_MAPPINGS.get(sport.name)
    if form_cls is None:
        raise SportNotConfiguredException(sport)
    return form_cls
