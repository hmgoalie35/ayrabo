divisions = [
    '18U Tier II',
    '16U Tier I',
    '16U Tier II',
    '16U Tier III',
    '15U Tier I',
    '14U Tier I Major',
    '14U Tier I Minor',
    '14U Tier II',
    '14U Tier III',
    '14U Milner',
    '12U Tier I Major',
    '12U Tier I Minor',
    '12U Tier II',
    '12U Tier III',
    '12U Milner',
    '10U Tier I Major',
    '10U Tier I Minor',
    '10U Tier II',
    '10U Tier III East',
    '10U Tier III West',
    '10U Milner',
]

nyc_cyclones = 'New York City Cyclones'
ny_skyliners = 'New York Skyliners'
li_rebels = 'Long Island Rebels'
lb_lightning = 'Long Beach Lightning'
li_edge = 'Long Island Edge'
greater_ny = 'Greater New York'
hv_polar_bears = 'Hudson Valley Polar Bears'
arrows = 'Freeport Arrows'
mamaroneck = 'Mamaroneck Tigers'
icecats = 'Green Machine IceCats'
li_gulls = 'Long Island Gulls'
pal_ih_jr_isles = 'P.A.L. IH Jr. Islanders'
pal_ih = 'P.A.L. IH'
pal_ih_sound_tigers = 'P.A.L. IH Sound Tigers'
westchester_express = 'Westchester Express'
westchester_vipers = 'Westchester Vipers'
li_royals = 'Long Island Royals'
aviator = 'Aviator Hockey Club'
gn_bruins = 'Great Neck Bruins'
dix_hills_hawks = 'Dix Hills Hawks'
brewster = 'Brewster Hockey'
richmond_thunder = 'Richmond Thunder'
lady_isles = 'Lady Islanders'


def append_east(team):
    return team + ' East'


def append_west(team):
    return team + ' West'


liahl_divisions = {
    '18U Tier II': {
        'bday_year': [1999, 2000],
        'teams': [nyc_cyclones, li_rebels, lb_lightning, li_edge, greater_ny, hv_polar_bears, arrows, mamaroneck,
                  icecats]
    },
    '16U Tier I': {
        'bday_year': [2001, 2000],
        'teams': [li_gulls, pal_ih_jr_isles, westchester_express, li_royals]
    },
    # ********** This is a good division to test with **********
    '16U Tier II': {
        'bday_year': [2001, 2000],
        'teams': [li_edge, greater_ny, icecats, pal_ih, arrows, aviator, li_rebels, lb_lightning, westchester_vipers,
                  nyc_cyclones, hv_polar_bears]
    },
    '16U Tier III': {
        'bday_year': [2001, 2000],
        'teams': [li_edge, gn_bruins, icecats, li_rebels, dix_hills_hawks, ny_skyliners, aviator, greater_ny]
    },
    '15U Tier I': {
        'bday_year': [2002],
        'teams': [li_royals, li_gulls, pal_ih_jr_isles, westchester_express]
    },
    '14U Tier I Major': {
        'bday_year': [2003, 2004],
        'teams': [li_gulls, pal_ih_jr_isles, li_royals]
    },
    '14U Tier I Minor': {
        'bday_year': [2003, 2004],
        'teams': [pal_ih_jr_isles, li_royals, li_gulls, westchester_express]
    },
    # ********** This is a good division to test with **********
    '14U Tier II': {
        'bday_year': [2003, 2004],
        'teams': [greater_ny, brewster, li_rebels, lb_lightning, nyc_cyclones, li_edge, hv_polar_bears,
                  westchester_vipers, pal_ih, mamaroneck, arrows]
    },
    '14U Tier III': {
        'bday_year': [2003, 2004],
        'teams': [lb_lightning, dix_hills_hawks, aviator, richmond_thunder, arrows, nyc_cyclones, greater_ny, li_edge,
                  gn_bruins, ny_skyliners]
    },
    '14U Milner': {
        'bday_year': [2003, 2004],
        'teams': [ny_skyliners, icecats, westchester_vipers, dix_hills_hawks, li_rebels, li_royals, li_gulls, brewster,
                  pal_ih_sound_tigers, aviator, ]
    },
    '12U Tier I Major': {
        'bday_year': [2005, 2006],
        'teams': [li_royals, li_gulls, westchester_express, pal_ih_jr_isles, aviator]
    },
    '12U Tier I Minor': {
        'bday_year': [2005, 2006],
        'teams': [li_royals, pal_ih_jr_isles, li_gulls, westchester_express]
    },
    '12U Tier II': {
        'bday_year': [2005, 2006],
        'teams': [pal_ih, westchester_vipers, li_rebels, nyc_cyclones, arrows, lb_lightning, icecats, brewster,
                  greater_ny, li_edge]
    },
    # ********** This is a good division to test with **********
    '12U Tier III': {
        'bday_year': [2005, 2006],
        'teams': [aviator, gn_bruins, li_edge, dix_hills_hawks, pal_ih_sound_tigers, lady_isles, greater_ny,
                  lb_lightning, icecats, arrows, ny_skyliners, brewster, richmond_thunder, mamaroneck]
    },
    '12U Milner': {
        'bday_year': [2005, 2006],
        'teams': [pal_ih, li_gulls, li_royals, pal_ih_sound_tigers, li_rebels, ny_skyliners, nyc_cyclones,
                  westchester_vipers, lb_lightning, arrows]
    },
    '10U Tier I Major': {
        'bday_year': [2007, 2008],
        'teams': [pal_ih_jr_isles, li_gulls, li_royals, westchester_express]
    },
    '10U Tier I Minor': {
        'bday_year': [2007, 2008],
        'teams': [li_gulls, westchester_express, li_royals, pal_ih_jr_isles]
    },
    '10U Tier II': {
        'bday_year': [2007, 2008],
        'teams': [arrows, li_rebels, nyc_cyclones, westchester_vipers, pal_ih, lb_lightning, brewster, greater_ny,
                  li_edge, mamaroneck, icecats]
    },
    '10U Tier III East': {
        'bday_year': [2007, 2008],
        'teams': [append_east(pal_ih_sound_tigers), append_east(li_rebels), append_east(gn_bruins),
                  append_east(li_edge), append_east(li_gulls), append_east(icecats), append_east(arrows),
                  append_east(lb_lightning), append_east(ny_skyliners)]
    },
    '10U Tier III West': {
        'bday_year': [2007, 2008],
        'teams': [append_west(greater_ny), append_west(nyc_cyclones), append_west(aviator), append_west(ny_skyliners),
                  append_west(brewster), append_west(richmond_thunder), append_west(li_gulls)]
    },
    '10U Milner': {
        'bday_year': [2007, 2008],
        'teams': [westchester_vipers, li_gulls, ny_skyliners, pal_ih_sound_tigers, arrows, li_royals, aviator,
                  li_rebels, pal_ih]
    }
}
