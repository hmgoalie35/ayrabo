Feature: Game scoresheet
  As an authenticated user,
  I want to be able to view a game's scoresheet

  Background: User exists
    Given The following users exist
      | first_name | last_name | email             | password       |
      | Michael    | Scott     | mscott@ayrabo.com | myweakpassword |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following generic choice objects exist
      | content_type | short_value | long_value | type             |
      | sports.Sport | exhibition  | Exhibition | game_type        |
      | sports.Sport | league      | League     | game_type        |
      | sports.Sport | 2           | 2          | game_point_value |
    And The following location object exists
      | name    |
      | Iceland |
    And The following seasons exist
      | id | league                            | start_date | end_date   | teams                 |
      | 1  | Long Island Amateur Hockey League | 2017-09-01 | 2018-09-02 | Green Machine IceCats |
    And The following game objects exist
      | id | home_team             | away_team        | type   | point_value | location | start               | end                 | timezone   | season |
      | 1  | Green Machine IceCats | Long Island Edge | league | 2           | Iceland  | 10/23/2017 07:00 PM | 10/23/2017 09:00 PM | US/Eastern | 1      |
    And I login with "mscott@ayrabo.com" and "myweakpassword"

  Scenario: View basic game details
    Given I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=1"
    Then I should see "Home Team"
    And I should see "Green Machine IceCats"
    And I should see "Long Island Amateur Hockey League"
    And I should see "10/23/2017 07:00 PM"
    And I should see "Iceland"
    And I should see "League"
    And I should see "Scheduled"
    And I should see "2017-2018"
    And I should see "Away Team"
    And I should see "Long Island Edge"
    And I should see "Long Island Amateur Hockey League"

  Scenario: User can't take score, view game before started
    Given I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=1"
    Then "Scheduled" should show up 2 times
    And I should see "Countdown to Game Start"
    And I should see "minutes"
