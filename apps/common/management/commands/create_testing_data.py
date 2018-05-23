import datetime
import random
from itertools import permutations, cycle

import pytz
from allauth.account.models import EmailAddress
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils.timezone import activate
from faker import Faker

from common.management.testing_data import liahl_divisions
from common.models import GenericChoice
from divisions.models import Division
from games.tests import HockeyGameFactory
from leagues.models import League
from locations.models import Location
from managers.models import Manager
from organizations.models import Organization
from players.tests import HockeyPlayerFactory
from seasons.models import Season
from sports.models import SportRegistration
from teams.models import Team
from userprofiles.tests import UserProfileFactory
from users.models import User
from users.tests import UserFactory

faker = Faker()


def get_object(cls, **kwargs):
    try:
        return cls.objects.get(**kwargs)
    except cls.DoesNotExist:
        return None


def create_object(cls, exclude=None, **kwargs):
    exclude = exclude or []
    instance = cls(**kwargs)
    instance.full_clean(exclude=exclude)
    instance.save()
    return instance


def get_user_input(prompt):
    string = None
    while string is None or string.strip() == '':
        string = input('{}: '.format(prompt))
    return string


def get_league(self):
    league_name = get_user_input('What league (case insensitive)').lower()
    try:
        league = League.objects.get(Q(full_name__iexact=league_name) | Q(abbreviated_name__iexact=league_name))
    except League.DoesNotExist:
        league = None

    if league is None:
        self.stdout.write('{} DNE'.format(league_name))
        exit(1)
    return league


def create_season(league, start_date, end_date):
    qs = Season.objects.filter(league=league, start_date__year=start_date.year, end_date__year=end_date.year)
    if qs.exists():
        return qs.first()
    return create_object(Season, league=league, start_date=start_date, end_date=end_date)


def create_division(name, league):
    return create_object(Division, exclude=['slug'], name=name, league=league)


def create_team(name, division):
    organization, _ = Organization.objects.get_or_create(name=name)
    return create_object(Team, exclude=['slug'], name=name, division=division, organization=organization)


def generate_birthday(year):
    bday = None
    while bday is None:
        try:
            month, day = faker.month(), faker.day_of_month()
            datetime.date(year=year, month=int(month), day=int(day))
            bday = '{}-{}-{}'.format(year, month, day)
        except ValueError:
            bday = None
    return bday


def create_user(birth_year):
    user = UserFactory(userprofile=None, password='myweakpassword')
    EmailAddress.objects.get_or_create(user=user, email=user.email, verified=True, primary=True)
    birthday = generate_birthday(birth_year)
    user_profile = UserProfileFactory(user=user, gender='male', birthday=birthday, timezone='US/Eastern')
    return user, user_profile


def create_users(count, birth_year):
    users = []
    for i in range(count):
        user, user_profile = create_user(birth_year)
        users.append(user)
    return users


def create_sport_registrations(users, sport, roles):
    sport_registrations = []
    for user in users:
        sr = create_object(SportRegistration, user=user, sport=sport, is_complete=True)
        sr.set_roles(roles)
        sport_registrations.append(sr)
    return sport_registrations


def get_position(i):
    if i in range(0, 4):
        return 'C'
    if i in range(4, 8):
        return 'LW'
    if i in range(8, 12):
        return 'RW'
    if i in range(12, 16):
        return 'LD'
    if i in range(16, 20):
        return 'RD'
    return 'G'


def create_players(users, sport, team):
    players = []
    i = 0
    num_users = len(users)
    for user in users:
        position = get_position(i)
        player = HockeyPlayerFactory(user=user, sport=sport, team=team, jersey_number=(i % num_users) + 1,
                                     position=position)
        player.full_clean()
        players.append(player)
        i += 1
    return players


def create_game(**kwargs):
    game = HockeyGameFactory(**kwargs)
    game.full_clean()
    game.save()
    return game


def get_friday(date):
    return date + datetime.timedelta((4 - date.weekday()) % 7)


def create_games(matchups, point_value, game_type, timezone, season, locations):
    games = []
    i = 0
    tz = pytz.timezone(timezone)
    activate(tz)
    iterator = cycle(range(2))
    weeks = 0
    for home_team, away_team in matchups:
        dt = datetime.datetime.combine(season.start_date, datetime.time(hour=random.choice([17, 18, 19, 20]),
                                                                        minute=random.choice([0, 30])))
        # Will create Friday/Saturday games for each week
        friday = get_friday(dt)
        value = next(iterator)
        start = friday + datetime.timedelta(weeks=weeks, days=value)
        if value == 1:
            weeks += 1
        weeks = weeks % 52

        managers = Manager.objects.active().filter(team=home_team)
        created_by = managers.first() or User.objects.filter(is_superuser=True).first()
        start = tz.localize(start)
        end = start + datetime.timedelta(hours=3)
        game = create_game(home_team=home_team, away_team=away_team, point_value=point_value, type=game_type,
                           timezone=timezone, season=season, start=start, end=end, location=random.choice(locations),
                           team=home_team, created_by=created_by)

        game_start = game.start.date()
        game_end = game.end.date()
        if (season.start_date <= game_start <= season.end_date) or (season.start_date <= game_end <= season.end_date):
            pass
        else:
            print('[WARNING] ID: {} {} does not occur during the {}-{} Season.'.format(
                game.id,
                game.start,
                season.start_date.year,
                season.end_date.year)
            )

        games.append(game)
        i += 1
    return games


class Command(BaseCommand):
    help = 'Creates useful testing data'

    def handle(self, *args, **options):
        self.stdout.write('This script assumes a sport and league exist.')

        one_year = datetime.timedelta(days=365)
        league = get_league(self)
        locations = Location.objects.all()
        if not locations.exists():
            self.stdout.write('Please create some locations')
            exit(1)

        script_start = datetime.datetime.now()

        sport = league.sport
        num_users = 22
        season_start_base = datetime.date(year=2015, month=8, day=15)
        season_end_base = season_start_base + one_year

        self.stdout.write('Creating 2015-2016, 2016-2017, 2017-2018 Seasons\n')
        season_2015_2016 = create_season(league, season_start_base, season_end_base)
        season_2016_2017 = create_season(league, season_2015_2016.start_date + one_year,
                                         season_2015_2016.end_date + one_year)
        season_2017_2018 = create_season(league, season_2016_2017.start_date + one_year,
                                         season_2016_2017.end_date + one_year)
        # NOTE: For every new year, the gap b/w 2017-2018 and the current season's years will grow. Need to write
        # a loop that will create all seasons from 2015-2016 season (or some arbitrary date)
        # to the currentyear-currentyear+1 season

        seasons = [season_2015_2016, season_2016_2017, season_2017_2018]

        for division_name, config in liahl_divisions.items():
            self.stdout.write('Creating {} division\n'.format(division_name))
            division = create_division(division_name, league)
            for team_name in config.get('teams'):
                self.stdout.write('Creating {} team for {} division\n'.format(team_name, division_name))
                team = create_team(team_name, division)
                if team.hockeyplayer_set.exists():
                    self.stdout.write('Players already exist, skipping user/player creation')
                else:
                    self.stdout.write('Creating {} users'.format(num_users))
                    bday_year = random.choice(config.get('bday_year'))
                    users = create_users(num_users, bday_year)
                    self.stdout.write('Creating sport registrations for {} users'.format(num_users))
                    create_sport_registrations(users, sport, ['Player'])
                    self.stdout.write('Creating players for {} users\n\n'.format(num_users))
                    create_players(users, sport, team)

        choices = GenericChoice.objects.get_choices(instance=sport)
        point_value = choices.filter(short_value=2, type='game_point_value').first()
        game_type = choices.filter(type='game_type').get(short_value='league')

        for division_name, config in liahl_divisions.items():
            division = get_object(Division, name=division_name, league=league)
            teams = division.team_set.all()
            self.stdout.write('\nGenerating matchups for {} teams'.format(len(teams)))
            matchups = list(permutations(teams, 2))
            tz = 'US/Eastern'
            for season in seasons:
                self.stdout.write('Adding teams to {}'.format(season))
                for team in teams:
                    season.teams.add(team)
                self.stdout.write('Creating games for {}'.format(season))
                games = create_games(matchups, point_value, game_type, tz, season, locations)
                self.stdout.write('Created {} games\n\n'.format(len(games)))

        script_end = datetime.datetime.now()
        self.stdout.write('\n\nTook: {}'.format(script_end - script_start))
        self.stdout.write('Done')
