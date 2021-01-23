import datetime

import pytz
from django.core.exceptions import ValidationError

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from games.form_fields import GamePlayerField, GamePlayerWidget
from games.models import HockeyGamePlayer
from games.tests import HockeyGameFactory, HockeyGamePlayerFactory
from players.models import HockeyPlayer
from players.tests import HockeyPlayerFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


class FixtureMixin(object):
    def setUp(self):
        super().setUp()
        self.sport = SportFactory()
        self.point_value = GenericChoiceFactory(
            content_object=self.sport,
            short_value='1',
            long_value='1',
            type=GenericChoice.GAME_POINT_VALUE
        )
        self.game_type = GenericChoiceFactory(
            content_object=self.sport,
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE
        )
        self.tz_name = 'US/Eastern'
        self.home_team = TeamFactory(name='New York Islanders')
        self.away_team = TeamFactory(name='New York Rangers', division=self.home_team.division)
        # 12/16/2017 @ 07:00PM
        self.start = pytz.utc.localize(datetime.datetime(year=2017, month=12, day=16, hour=19))
        self.game = HockeyGameFactory(
            type=self.game_type,
            point_value=self.point_value,
            start=self.start,
            timezone=self.tz_name,
            home_team=self.home_team,
            away_team=self.away_team
        )
        self.home_player1 = HockeyPlayerFactory(
            sport=self.sport,
            team=self.home_team,
            jersey_number='1',
            position=HockeyPlayer.GOALTENDER,
            user__first_name='Jon',
            user__last_name='Doe'
        )
        self.home_player2 = HockeyPlayerFactory(
            sport=self.sport,
            team=self.home_team,
            jersey_number='99',
            position=HockeyPlayer.CENTER,
            user__first_name='Wayne',
            user__last_name='Gretzky'
        )

        self.home_hockey_game_player1 = HockeyGamePlayerFactory(
            team=self.home_team,
            game=self.game,
            player=self.home_player1,
            is_starting=True
        )
        self.home_hockey_game_player2 = HockeyGamePlayerFactory(
            team=self.home_team,
            game=self.game,
            player=self.home_player2
        )
        self.queryset = self.game.home_team_game_players


class GamePlayerWidgetTests(FixtureMixin, BaseTestCase):

    def test_get_context(self):
        widget = GamePlayerWidget(queryset=self.queryset)

        context = widget.get_context('my_name', self.queryset, None)
        self.assertIs(context.get('queryset'), self.queryset)

    def test_render(self):
        qs = self.queryset
        widget = GamePlayerWidget(queryset=qs)
        html = widget.render('my_name', qs)

        self.assertInHTML(
            """
            <ul class="list-group game-player-widget">
                <li class="list-group-item list-group-item-slim text-left">
                    #1 Jon Doe G
                    <span class="badge badge-info">Starter</span>
                </li>
                <li class="list-group-item list-group-item-slim text-left">
                    #99 Wayne Gretzky C
                </li>
            </ul>
            """,
            html
        )

        qs = None
        widget = GamePlayerWidget(queryset=qs)
        html = widget.render('my_name', qs)
        self.assertInHTML(
            """
            <p class="mt5">There are no players on this roster.</p>
            """,
            html
        )

        qs = HockeyGamePlayer.objects.none()
        widget = GamePlayerWidget(queryset=qs)
        html = widget.render('my_name', qs)
        self.assertInHTML(
            """
            <p class="mt5">There are no players on this roster.</p>
            """,
            html
        )


class GamePlayerFieldTests(FixtureMixin, BaseTestCase):
    def test_init(self):
        field = GamePlayerField(self.queryset)

        self.assertTrue(field.disabled)
        self.assertTrue(field.required)
        self.assertEqual(field.initial, self.queryset)
        self.assertIsInstance(field.widget, GamePlayerWidget)

    def test_validate(self):
        # The field constructor sets coerces falsy values to `None`. By default it looks like django passes the value
        # of `initial` to the clean function
        with self.assertRaisesMessage(ValidationError, 'This field is required.'):
            field = GamePlayerField(None)
            field.clean(field.initial)

        with self.assertRaisesMessage(ValidationError, 'This field is required.'):
            field = GamePlayerField(HockeyGamePlayer.objects.none())
            field.clean(field.initial)

        self.home_hockey_game_player1.is_starting = False
        self.home_hockey_game_player1.save()
        with self.assertRaisesMessage(ValidationError, 'Please select a starting goaltender.'):
            field = GamePlayerField(self.queryset)
            field.clean(field.initial)
