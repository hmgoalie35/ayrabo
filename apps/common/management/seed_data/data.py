# Sports
ICE_HOCKEY = 'Ice Hockey'
BASEBALL = 'Baseball'
SPORTS = [ICE_HOCKEY, BASEBALL]

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

GENERIC_CHOICES = {
    ICE_HOCKEY: [
        # Game types
        {'short_value': 'exhibition', 'long_value': 'Exhibition', 'type': 'game_type'},
        {'short_value': 'league', 'long_value': 'League', 'type': 'game_type'},
        # Game point values
        {'short_value': '0', 'long_value': '0', 'type': 'game_point_value'},
        {'short_value': '1', 'long_value': '1', 'type': 'game_point_value'},
        {'short_value': '2', 'long_value': '2', 'type': 'game_point_value'},
    ]
}

GENERIC_PENALTY_CHOICES = {
    ICE_HOCKEY: [
        {'name': 'Abuse of officials', 'description': ''},
        {'name': 'Aggressor penalty', 'description': ''},
        {'name': 'Attempt to injure', 'description': ''},
        {'name': 'Biting', 'description': ''},
        {'name': 'Boarding', 'description': ''},
        {'name': 'Butt ending', 'description': ''},
        {'name': 'Broken stick', 'description': ''},
        {'name': 'Charging', 'description': ''},
        {'name': 'Checking from behind', 'description': ''},
        {'name': 'Clipping', 'description': ''},
        {'name': 'Cross checking', 'description': ''},
        {'name': 'Delay of game', 'description': ''},
        {'name': 'Diving', 'description': ''},
        {'name': 'Elbowing', 'description': ''},
        {'name': 'Eye gouging', 'description': ''},
        {'name': 'Fighting', 'description': ''},
        {'name': 'Goaltender interference', 'description': ''},
        {'name': 'Goaltender leaving the crease', 'description': ''},
        {'name': 'Head butting', 'description': ''},
        {'name': 'High sticking', 'description': ''},
        {'name': 'Holding', 'description': ''},
        {'name': 'Holding the stick', 'description': ''},
        {'name': 'Hooking', 'description': ''},
        {'name': 'Illegal check to the head', 'description': ''},
        {'name': 'Illegal equipment', 'description': ''},
        {'name': 'Instigator', 'description': ''},
        {'name': 'Interference', 'description': ''},
        {'name': 'Third man in', 'description': ''},
        {'name': 'Kicking', 'description': ''},
        {'name': 'Kneeing', 'description': ''},
        {'name': 'Roughing', 'description': ''},
        {'name': 'Slashing', 'description': ''},
        {'name': 'Slew footing', 'description': ''},
        {'name': 'Spearing', 'description': ''},
        {'name': 'Starting the wrong lineup', 'description': ''},
        {'name': 'Substitution infraction', 'description': ''},
        {'name': 'Throwing the stick', 'description': ''},
        {'name': 'Too many men', 'description': ''},
        {'name': 'Tripping', 'description': ''},
        {'name': 'Unsportsmanlike conduct', 'description': ''},
    ]
}
