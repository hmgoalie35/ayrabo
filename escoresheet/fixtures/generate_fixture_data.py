import datetime

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.text import slugify
from faker import Faker

from divisions.models import Division
from leagues.models import League
from players.models import HockeyPlayer
from seasons.models import Season, HockeySeasonRoster
from sports.models import Sport, SportRegistration
from teams.models import Team
from userprofiles.models import UserProfile
from userprofiles.tests.factories.UserProfileFactory import generate_height

site = Site.objects.first()
site.domain = 'escoresheet.com'
site.name = site.domain
site.save()

fake = Faker()

# Sports
ICE_HOCKEY = 'Ice Hockey'
BASEBALL = 'Baseball'

# Leagues
LIAHL = 'Long Island Amateur Hockey League'
NHL = 'National Hockey League'
MLB = 'Major League Baseball'

# Divisions
PACIFIC = 'Pacific Division'
CENTRAL = 'Central Division'
METROPOLITAN = 'Metropolitan Division'
ATLANTIC = 'Atlantic Division'

MM_AA = 'Midget Minor AA'

AMERICAN_LEAGUE_EAST = 'American League East'
AMERICAN_LEAGUE_WEST = 'American League West'
AMERICAN_LEAGUE_CENTRAL = 'American League Central'
NATIONAL_LEAGUE_EAST = 'National League East'
NATIONAL_LEAGUE_WEST = 'National League West'
NATIONAL_LEAGUE_CENTRAL = 'National League Central'

DATA = {
    ICE_HOCKEY: {
        LIAHL: {
            MM_AA: ['Aviator Gulls', 'Brewster Bulldogs', 'Freeport Arrows', 'Great Neck Bruins',
                    'Green Machine IceCats', 'Long Island Edge', 'Long Island Rebels', 'Long Island Royals',
                    'Mamaroneck Tigers', 'NYC Cyclones', 'Nassau County Lions'],
        },
        NHL: {
            PACIFIC: ['Anaheim Ducks', 'Arizona Coyotes', 'Calgary Flames', 'Edmonton Oilers', 'Los Angeles Kings',
                      'San Jose Sharks', 'Vancouver Canucks'],
            CENTRAL: ['Chicago Blackhawks', 'Colorado Avalanche', 'Dallas Stars', 'Minnesota Wild',
                      'Nashville Predators', 'St. Louis Blues', 'Winnipeg Jets'],
            METROPOLITAN: ['Carolina Hurricanes', 'Columbus Blue Jackets', 'New Jersey Devils', 'New York Islanders',
                           'New York Rangers', 'Philadelphia Flyers', 'Pittsburgh Penguins', 'Washington Capitals'],
            ATLANTIC: ['Boston Bruins', 'Buffalo Sabres', 'Detroit Red Wings', 'Florida Panthers', 'Ottawa Senators',
                       'Tampa Bay Lightning', 'Toronto Maple Leafs', 'Montr\u00e9al Canadiens']
        },
    },
    BASEBALL: {
        MLB: {
            AMERICAN_LEAGUE_CENTRAL: ['Cleveland Indians', 'Detroit Tigers', 'Chicago White Sox', 'Kansas City Royals',
                                      'Minnesota Twins'],
            AMERICAN_LEAGUE_EAST: ['Toronto Blue Jays', 'Baltimore Orioles', 'Boston Red Sox', 'New York Yankees',
                                   'Tampa Bay Rays'],
            AMERICAN_LEAGUE_WEST: ['Texas Rangers', 'Seattle Mariners', 'Houston Astros', 'Oakland Athletics',
                                   'Los Angeles Angels'],
            NATIONAL_LEAGUE_CENTRAL: ['Chicago Cubs', 'St. Louis Cardinals', 'Pittsburgh Pirates', 'Milwaukee Brewers',
                                      'Cincinnati Reds'],
            NATIONAL_LEAGUE_EAST: ['Washington Nationals', 'Miami Marlins', 'New York Mets', 'Philadelphia Phillies',
                                   'Atlanta Braves'],
            NATIONAL_LEAGUE_WEST: ['San Francisco Giants', 'Los Angeles Dodgers', 'Colorado Rockies',
                                   'San Diego Padres', 'Arizona Diamondbacks'
                                   ]
        }
    }
}

names = []
while len(names) < 242:
    name = fake.first_name_male() + ' ' + fake.last_name_male()
    if name not in names:
        names.append(name)


def create_hierarchy():
    """
    Create objects for sports, leagues, divisions, teams
    Setup seasons
    """
    for sport_name, leagues in DATA.items():
        sport, s_created = Sport.objects.get_or_create(name=sport_name, slug=slugify(sport_name))
        print(sport, s_created)
        for league_name, divisions in leagues.items():
            abbreviated_name = ''.join([word[:1].strip().upper() for word in league_name.split(' ')])
            league, l_created = League.objects.get_or_create(sport=sport, full_name=league_name,
                                                             abbreviated_name=abbreviated_name,
                                                             slug=slugify(abbreviated_name))
            print(' ' * 2, league, l_created)

            start_date = datetime.date(year=2016, month=9, day=19)
            end_date = start_date + datetime.timedelta(days=365)
            season, season_created = Season.objects.get_or_create(league=league, start_date=start_date,
                                                                  end_date=end_date)
            print(' ' * 4, season, season_created)

            for division_name, teams in divisions.items():
                division, d_created = Division.objects.get_or_create(league=league, name=division_name,
                                                                     slug=slugify(division_name))
                print(' ' * 6, division, d_created)

                for team_name in teams:
                    team, t_created = Team.objects.get_or_create(name=team_name, division=division,
                                                                 slug=slugify(team_name), website='')
                    season.teams.add(team)
                    if 'Hockey' in sport_name:
                        hsr, hsr_created = HockeySeasonRoster.objects.get_or_create(season=season, team=team)
                        print(' ' * 8, hsr, hsr_created)
                        print(' ' * 10, team, t_created)
        print('\n')


def create_users():
    """
    Only handles creating users/hockey players for all times in midget minor AA
    """
    i = 0
    team_index = 0
    position_index = 1
    ice_hockey = Sport.objects.get(name='Ice Hockey')
    teams = Team.objects.filter(division__name=MM_AA)
    print('Working...')
    for name in names:
        name_split = name.strip().split(' ')
        first_name = name_split[0].strip()
        last_name = name_split[1].strip()
        email = '{first_name}@{last_name}.com'.format(first_name=first_name.lower(), last_name=last_name.lower())

        user, u_created = User.objects.get_or_create(first_name=first_name, last_name=last_name,
                                                     email=email, username=email)
        user.set_password('jjjjjjjj')
        user.save()

        email_obj, e_created = EmailAddress.objects.get_or_create(user=user, email=email, verified=True, primary=True)

        qs = UserProfile.objects.filter(user=user)
        up = None
        if qs.exists():
            up = qs.first()
        else:
            up = UserProfile.objects.create(user=user, gender='Male',
                                            birthday=datetime.datetime.now(), height=generate_height(),
                                            weight=130)

        sr, sr_created = SportRegistration.objects.get_or_create(user=user, sport=ice_hockey, is_complete=True)
        sr.set_roles(['Player'])

        if position_index <= 4:
            position = 'C'
        elif 4 < position_index <= 8:
            position = 'LW'
        elif 8 < position_index <= 12:
            position = 'RW'
        elif 12 < position_index <= 16:
            position = 'LD'
        elif 16 < position_index <= 20:
            position = 'RD'
        elif 20 < position_index <= 22:
            position = 'G'
        else:
            position_index = 1
            position = 'C'

        hp, hp_created = HockeyPlayer.objects.get_or_create(user=user, sport=ice_hockey, team=teams[team_index],
                                                            jersey_number=(i % 22) + 1,
                                                            position=position,
                                                            handedness='Right')
        hsr = HockeySeasonRoster.objects.get(season=Season.objects.get(league__full_name=LIAHL), team=teams[team_index])

        hsr.players.add(hp)

        if i != 0 and i % 22 == 0:
            team_index += 1

        i += 1
        position_index += 1
        print('{}%'.format(round((i / 242.0) * 100, 2)))


if __name__ == '__main__':
    create_hierarchy()
    create_users()
