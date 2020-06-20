Feature: League schedule

  Background:
    Given The following users exist
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
    And The following seasons exist
      | id | league                            | start_date | end_date | teams                 |
      | 1  | Long Island Amateur Hockey League | today      | 1y       | Green Machine IceCats |
      | 2  | Long Island Amateur Hockey League | -1y        | -5d      | Green Machine IceCats |
      | 3  | Long Island Amateur Hockey League | 1y         | 2y       | Green Machine IceCats |
    And The following game objects exist
      | id | home_team             | away_team        | type   | point_value | location | start | end   | timezone   | season |
      | 1  | Green Machine IceCats | Long Island Edge | league | 2           | Iceland  | today | today | US/Eastern | 1      |
      | 2  | Long Island Rebels    | Aviator Gulls    | league | 2           | Iceland  | today | today | US/Eastern | 1      |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: View current season
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    Then I should see "Long Island Amateur Hockey League"
    And I should see season "today" "1y"
    Then I should see "Green Machine IceCats"
    And I should see "Long Island Edge"
    And I should see "League"
    And I should see "Scheduled"
    And I should see "Edit"
    And I should see "Rosters"
    And I should see "Iceland"
    And I should see "Long Island Rebels"
    And I should see "Aviator Gulls"
    And I should see "Start"

  Scenario: View current season, press schedule nav tab again
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    And I press "tab-item-schedule"
    Then I should be on the "leagues:schedule" page with kwargs "slug=liahl"

  Scenario: Navigate to league schedule page for past season
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    And I press "tab-item-seasons"
    And I press "season-2"
    Then I should be on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=2"

  Scenario: View past season
    Given I am on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=2"
    Then I should see "This season has been archived."
    And I should see "The current season's schedule is available"
    And I should see season "-1y" "-5d"
    And I should see "There are no games for Long Island Amateur Hockey League at this time."

  Scenario: View past season, press schedule nav tab again
    Given I am on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=2"
    And I press "tab-item-schedule"
    Then I should be on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=2"

  Scenario: Navigate to league schedule page for future season
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    And I press "tab-item-seasons"
    And I press "season-3"
    Then I should be on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=3"

  Scenario: View future season
    Given I am on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=3"
    Then I should see "This season has not started yet."
    And I should see "The current season's schedule is available"
    And I should see season "1y" "2y"
    And I should see "There are no games for Long Island Amateur Hockey League at this time."

  Scenario: View future season, press schedule nav tab again
    Given I am on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=3"
    And I press "tab-item-schedule"
    Then I should be on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=3"

  Scenario: Navigate to game scoresheet page
    Given I am on the "teams:schedule" page with kwargs "team_pk=1"
    When I press "actions-dropdown-1"
    And I press "game-scoresheet-1"
    Then I should be on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=1"
