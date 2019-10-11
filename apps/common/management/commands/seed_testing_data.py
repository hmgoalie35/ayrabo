import datetime
import random
from itertools import cycle, permutations

import pytz
from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from faker import Faker

from common.management.commands._utils import get_or_create
from common.management.seed_data.testing_data import liahl_divisions
from common.models import GenericChoice
from divisions.models import Division
from games.models import AbstractGame, HockeyGame
from leagues.models import League
from locations.models import Location
from managers.models import Manager
from organizations.models import Organization
from players.models import HockeyPlayer
from seasons.models import Season
from sports.models import SportRegistration
from teams.models import Team
from userprofiles.models import UserProfile
from users.models import User


faker = Faker()
PLAYERS_PER_TEAM = 22


def generate_birthday(year):
    bday = None
    while bday is None:
        try:
            month, day = faker.month(), faker.day_of_month()
            datetime.date(year=year, month=int(month), day=int(day))
            bday = f'{year}-{month}-{day}'
        except ValueError:
            bday = None
    return bday


def get_position(i):
    if i in range(0, 4):
        return HockeyPlayer.CENTER
    if i in range(4, 8):
        return HockeyPlayer.LEFT_WING
    if i in range(8, 12):
        return HockeyPlayer.RIGHT_WING
    if i in range(12, 16):
        return HockeyPlayer.LEFT_DEFENSE
    if i in range(16, 20):
        return HockeyPlayer.RIGHT_DEFENSE
    return HockeyPlayer.GOALTENDER


def get_friday(date):
    return date + datetime.timedelta((4 - date.weekday()) % 7)


class Command(BaseCommand):
    help = 'Creates useful testing data'

    def __init__(self, *args, **kwargs):
        self.num_users = 0
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # Only support LIAHL for now since testing_data.py only contains that league
        leagues = list(League.objects.filter(abbreviated_name__iexact='liahl').values_list(
            'abbreviated_name', flat=True
        ))
        parser.add_argument('league', choices=leagues)
        parser.add_argument('--players-per-team', type=int, default=PLAYERS_PER_TEAM)

    def create_seasons(self, league):
        season_start_date = datetime.date(year=2015, month=8, day=15)
        season_end_date = season_start_date.replace(year=timezone.now().year)
        self.stdout.write(f'Creating seasons from {season_start_date.year} to {season_end_date.year}')
        seasons = []
        for i in range((season_end_date.year - season_start_date.year) + 1):
            start_date = season_start_date + datetime.timedelta(days=365 * i)
            end_date = start_date + datetime.timedelta(days=365)
            seasons.append(self.create_season(league=league, start_date=start_date, end_date=end_date))
        return seasons

    def create_season(self, league, start_date, end_date):
        obj, created = get_or_create(
            Season,
            get_kwargs={
                'league': league,
                'start_date__year': start_date.year,
                'end_date__year': end_date.year,
            },
            create_kwargs={
                'league': league,
                'start_date': start_date,
                'end_date': end_date
            }
        )
        return obj, created

    def create_division(self, name, league):
        kwargs = {'name': name, 'league': league}
        return get_or_create(Division, get_kwargs=kwargs, create_kwargs=kwargs, exclude=['slug'])

    def create_organization(self, name, division):
        kwargs = {'name': name, 'sport': division.league.sport}
        return get_or_create(Organization, get_kwargs=kwargs, create_kwargs=kwargs, exclude=['slug'])

    def create_team(self, name, division, organization):
        kwargs = {'name': name, 'division': division, 'organization': organization}
        return get_or_create(Team, get_kwargs=kwargs, create_kwargs=kwargs, exclude=['slug'])

    def create_users(self, players_per_team, birth_year):
        users = []
        for i in range(players_per_team):
            user, _ = self.create_user(birth_year)
            users.append(user)
        return users

    def create_user(self, birth_year):
        email = f'user{self.num_users}@ayrabo.com'
        user = User.objects.create_user(
            username=email,
            email=email,
            password='myweakpassword',
            first_name=faker.first_name_male(),
            last_name=faker.last_name_male(),
        )
        self.num_users += 1
        EmailAddress.objects.get_or_create(user=user, email=user.email, verified=True, primary=True)
        user_profile = UserProfile.objects.create(
            user=user,
            gender='male',
            birthday=generate_birthday(birth_year),
            height=f'{random.randint(1, 8)}\' {random.randint(0, 11)}\"',
            weight=faker.random_int(min=UserProfile.MIN_WEIGHT, max=UserProfile.MAX_WEIGHT),
            timezone='US/Eastern'
        )
        return user, user_profile

    def create_sport_registrations(self, user, sport, roles):
        return SportRegistration.objects.create_for_user_and_sport(user, sport, roles)

    def create_players(self, users, sport, team):
        players = []
        i = 0
        num_users = len(users)
        handedness_choices = [handedness[0] for handedness in HockeyPlayer.HANDEDNESS]
        for user in users:
            self.create_sport_registrations(user, sport, [SportRegistration.PLAYER])
            player, _ = get_or_create(
                HockeyPlayer,
                get_kwargs={'user': user, 'team': team},
                create_kwargs={
                    'user': user,
                    'team': team,
                    'sport': sport,
                    'jersey_number': (i % num_users) + 1,
                    'position': get_position(i),
                    'handedness': faker.random_element(handedness_choices),
                    'is_active': True,
                }
            )
            players.append(player)
            i += 1
        return players

    def create_games(self, matchups, point_value, game_type, tz, season, locations):
        games = []
        i = 0
        tz = pytz.timezone(tz)
        timezone.activate(tz)
        iterator = cycle(range(2))
        weeks = 0
        for home_team, away_team in matchups:
            dt = datetime.datetime.combine(
                season.start_date,
                datetime.time(hour=random.choice([17, 18, 19, 20]), minute=random.choice([0, 30]))
            )
            # Will create Friday/Saturday games for each week
            friday = get_friday(dt)
            value = next(iterator)
            start = friday + datetime.timedelta(weeks=weeks, days=value)
            if value == 1:
                weeks += 1
            weeks = weeks % 52

            manager = Manager.objects.active().filter(team=home_team).first()
            created_by = manager.user if manager else User.objects.filter(is_superuser=True).first()
            start = tz.localize(start)
            end = start + datetime.timedelta(hours=3)
            game = self.create_game(
                home_team=home_team,
                away_team=away_team,
                point_value=point_value,
                status=AbstractGame.SCHEDULED,
                type=game_type,
                timezone=tz,
                season=season,
                start=start,
                end=end,
                location=random.choice(locations),
                team=home_team,
                created_by=created_by
            )

            game_start = game.start.date()
            game_end = game.end.date()
            warning_msg = '{} {} does not occur during the {}.'
            if not (season.start_date <= game_start <= season.end_date):
                self.stdout.write(self.style.WARNING(warning_msg.format(game.id, game.start, season)))
            if not (season.start_date <= game_end <= season.end_date):
                self.stdout.write(self.style.WARNING(warning_msg.format(game.id, game.end, season)))

            games.append(game)
            i += 1
        return games

    def create_game(self, **kwargs):
        # Using get kwargs won't really work because start and end dates are randomly chosen
        game, _ = get_or_create(
            HockeyGame,
            get_kwargs={'home_team': None},  # Workaround to always create games since home team is never null
            create_kwargs=kwargs,
        )
        return game

    def handle(self, *args, **options):
        locations = Location.objects.all()
        if not locations.exists():
            raise CommandError('Please create some locations before running this command.')
        start = timezone.now()

        league = League.objects.select_related('sport').get(abbreviated_name__iexact=options.get('league'))
        sport = league.sport
        players_per_team = options.get('players_per_team')

        seasons = self.create_seasons(league=league)

        for division_name, config in liahl_divisions.items():
            self.stdout.write(f'Creating division {division_name}')
            division, _ = self.create_division(division_name, league)
            for team_name in config.get('teams'):
                self.stdout.write(f'  Creating organization {team_name}')
                organization, _ = self.create_organization(team_name, division)
                self.stdout.write(f'    Creating team {team_name}')
                team, _ = self.create_team(team_name, division, organization)
                if team.hockeyplayer_set.exists():
                    self.stdout.write(f'      Players already exist, skipping user/player creation')
                    continue
                self.stdout.write(f'        Creating {players_per_team} users')
                users = self.create_users(players_per_team, random.choice(config.get('bday_year')))
                self.stdout.write(f'          Creating {players_per_team} players for users')
                self.create_players(users, sport, team)

        choices = GenericChoice.objects.get_choices(instance=sport)
        point_value = choices.filter(short_value=2, type=GenericChoice.GAME_POINT_VALUE).first()
        game_type = choices.filter(type=GenericChoice.GAME_TYPE).get(short_value='league')

        for division_name, config in liahl_divisions.items():
            division = Division.objects.prefetch_related('teams').get(name=division_name, league=league)
            teams = division.teams.all()
            self.stdout.write(f'Generating {division_name} matchups for {len(teams)} teams')
            matchups = list(permutations(teams, 2))
            for season, _ in seasons:
                self.stdout.write(f'Creating data for {season}')
                self.stdout.write(f'  Adding teams to {season}')
                season.teams.add(*teams)
                self.stdout.write(f'    Creating games for {season}')
                # We could generate a new tz for each game but having one tz for all games in a season is fine also
                tz = faker.random_element(settings.TIMEZONES)
                # Creating of games is not idempotent, new games will be created on subsequent runs of this command
                games = self.create_games(matchups, point_value, game_type, tz, season, locations)
                self.stdout.write(f'      Created {len(games)} games')

        end = timezone.now()
        self.stdout.write(f'Duration: {end - start}')
        self.stdout.write('Done')
