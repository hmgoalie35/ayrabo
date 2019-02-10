Feature: League detail
  As an authenticated user,
  I want to be able to view details, standings and other info about a league
  So that I can have all of this info in a central place

  Background:
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following league objects exist
      | name                              | sport      |
      | Long Island Amateur Hockey League | Ice Hockey |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 3  | Aviator Gulls         | PeeWee          | Long Island Amateur Hockey League | Ice Hockey |
      | 4  | Long Island Rebels    | PeeWee          | Long Island Amateur Hockey League | Ice Hockey |
    And The following manager objects exist
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And The following generic choice objects exist
      | content_type | short_value | long_value | type             |
      | sports.Sport | exhibition  | Exhibition | game_type        |
      | sports.Sport | league      | League     | game_type        |
      | sports.Sport | 2           | 2          | game_point_value |
    And The following location object exists
      | name    |
      | Iceland |
    And The following season object exists
      | id | league                            | start_date | end_date | teams                 |
      | 1  | Long Island Amateur Hockey League | today      | 1y       | Green Machine IceCats |
      | 2  | Long Island Amateur Hockey League | -1y        | -5d      | Green Machine IceCats |
    And The following game objects exist
      | home_team             | away_team        | type   | point_value | location | start | end   | timezone   | season |
      | Green Machine IceCats | Long Island Edge | league | 2           | Iceland  | today | today | US/Eastern | 1      |
      | Long Island Rebels    | Aviator Gulls    | league | 2           | Iceland  | today | today | US/Eastern | 1      |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Basic info displayed to user
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    Then I should see "Long Island Amateur Hockey League"
    And I should see season "today" "1y"

  Scenario: Games exist
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    Then I should see "Green Machine IceCats"
    And I should see "Long Island Edge"
    And I should see "League"
    And I should see "Scheduled"
    And I should see "Edit"
    And I should see "Rosters"
    And I should see "Iceland"
    And I should see "Long Island Rebels"
    And I should see "Aviator Gulls"
    And I should see season "today" "1y"

  Scenario: Navigate to league detail schedule page for a past season
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    And I press "tab-item-past-seasons"
    And I press "past-season-2"
    Then I should be on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=2"

  Scenario: View past season
    Given I am on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=2"
    Then I should see "This season has been archived."
    And I should see "The current season's schedule is available"
    And I should see season "-1y" "-5d"
    And I should see "There are no games for Long Island Amateur Hockey League at this time."
