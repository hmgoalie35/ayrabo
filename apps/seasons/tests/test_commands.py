import datetime
from unittest import mock

from django.core.management import call_command
from django.utils.six import StringIO

from divisions.tests import DivisionFactory
from escoresheet.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from seasons.models import Season
from seasons.tests import SeasonFactory
from teams.tests import TeamFactory

EXPIRATION_DAYS = 30


class CopyExpiringSeasonsTests(BaseTestCase):
    def setUp(self):
        self.today = datetime.date.today()
        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport__name='Ice Hockey')
        self.division = DivisionFactory(league=self.league)
        self.teams = TeamFactory.create_batch(5, division=self.division)

        # Expired

        # 2012-2013
        self.season_1 = SeasonFactory(start_date=datetime.date(2012, 8, 15),
                                      end_date=datetime.date(2013, 8, 15),
                                      league=self.league,
                                      teams=self.teams)
        # 2014-2015
        self.season_2 = SeasonFactory(start_date=datetime.date(2014, 8, 15),
                                      end_date=datetime.date(2015, 8, 15),
                                      league=self.league,
                                      teams=self.teams)
        # Expiring in 30 days
        self.season_3 = SeasonFactory(start_date=self.today,
                                      end_date=self.today + datetime.timedelta(days=EXPIRATION_DAYS),
                                      league=self.league,
                                      teams=self.teams)

        # Not expired

        # Expiring in 60 days
        self.season_4 = SeasonFactory(start_date=self.today,
                                      end_date=self.today + datetime.timedelta(days=EXPIRATION_DAYS * 2))

    def test_expired_no_copies_yet(self):
        out = StringIO()
        call_command('copy_expiring_seasons', stdout=out)
        result = out.getvalue()
        s1 = Season.objects.get(start_date__year=2013, end_date__year=2014)
        s2 = Season.objects.get(start_date__year=2015, end_date__year=2016)
        end_date = self.today + datetime.timedelta(days=EXPIRATION_DAYS)
        s3 = Season.objects.get(start_date=end_date,
                                end_date=end_date + datetime.timedelta(days=365))
        self.assertEqual(s1.league_id, self.season_1.league_id)
        self.assertListEqual(list(s1.teams.values_list('id', flat=True)),
                             list(self.season_1.teams.values_list('id', flat=True)))
        self.assertEqual(s2.league_id, self.season_2.league_id)
        self.assertListEqual(list(s2.teams.values_list('id', flat=True)),
                             list(self.season_2.teams.values_list('id', flat=True)))
        self.assertEqual(s3.league_id, self.season_3.league_id)
        self.assertListEqual(list(s3.teams.values_list('id', flat=True)),
                             list(self.season_3.teams.values_list('id', flat=True)))
        self.assertRegex(result, r'Total: 3 Copied: 3 Skipped: 0 SUCCESS\n$')

    @mock.patch('seasons.management.commands.copy_expiring_seasons.date')
    def test_expired_copies_exist(self, mock_date):
        today = datetime.date(2017, 9, 24)
        mock_date.today.return_value = today
        mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)

        self.season_3.start_date = today
        self.season_3.end_date = today + datetime.timedelta(days=EXPIRATION_DAYS)
        self.season_3.save()

        SeasonFactory(start_date=datetime.date(2013, 8, 15),
                      end_date=datetime.date(2014, 8, 15),
                      league=self.league,
                      teams=self.teams)
        SeasonFactory(start_date=datetime.date(2015, 8, 15),
                      end_date=datetime.date(2016, 8, 15),
                      league=self.league,
                      teams=self.teams)
        SeasonFactory(start_date=datetime.date(2016, 8, 15),
                      end_date=datetime.date(2017, 8, 15),
                      league=self.league,
                      teams=self.teams)
        out = StringIO()
        call_command('copy_expiring_seasons', stdout=out)
        result = out.getvalue()
        self.assertRegex(result, r'Total: 6 Copied: 1 Skipped: 5 SUCCESS\n$')
