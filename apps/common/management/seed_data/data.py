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
