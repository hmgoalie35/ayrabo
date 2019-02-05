Feature: View a team's schedule for current season and past seasons
  As a user,
  I want to be able to view a team's schedule for past and current seasons

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@ayrabo.com  | myweakpassword |
      | Jane       | Doe       | user1@ayrabo.com | myweakpassword |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 3  | Aviator Gulls         | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager, Player, Coach"
    And "user1@ayrabo.com" is completely registered for "Ice Hockey" with role "Player"
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
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Informative text displayed to user
    Given I am on the "teams:schedule" page with kwargs "team_pk=1"
    Then I should see "Green Machine IceCats - Midget Minor AA"
    And I should see "Long Island Amateur Hockey League"
    And I should see season "today" "1y"

  Scenario: No games
    Given I am on the "teams:schedule" page with kwargs "team_pk=1"
    Then I should see "There are no games for Green Machine IceCats at this time."

  Scenario: Games exist
    Given The following game objects exist
      | id | home_team             | away_team             | type   | point_value | location | start               | end                 | timezone   | season |
      | 1  | Green Machine IceCats | Long Island Edge      | league | 2           | Iceland  | 10/23/2017 07:00 PM | 10/23/2017 09:00 PM | US/Eastern | 1      |
      | 2  | Long Island Edge      | Green Machine IceCats | league | 2           | Iceland  | 10/30/2017 07:00 PM | 10/30/2017 09:00 PM | US/Eastern | 1      |
      | 3  | Long Island Edge      | Aviator Gulls         | league | 2           | Iceland  | 10/31/2017 07:00 PM | 10/31/2017 09:00 PM | US/Eastern | 1      |

    And I am on the "teams:schedule" page with kwargs "team_pk=1"
    Then "create-game-btn" should be visible
    And I should see "1"
    And I should see "Green Machine IceCats"
    And I should see "League"
    And I should see "Scheduled"
    And I should see "Iceland"
    And I should see "10/23/2017 07:00 PM EDT"
    And I should see "10/23/2017 09:00 PM EDT"
    And I should not see "Aviator Gulls"

  Scenario: Not team manager
    Given The following game objects exist
      | home_team             | away_team             | type   | point_value | location | start               | end                 | timezone   | season |
      | Green Machine IceCats | Long Island Edge      | league | 2           | Iceland  | 10/23/2017 07:00 PM | 10/23/2017 09:00 PM | US/Eastern | 1      |
      | Long Island Edge      | Green Machine IceCats | league | 2           | Iceland  | 10/30/2017 07:00 PM | 10/30/2017 09:00 PM | US/Eastern | 1      |
      | Long Island Edge      | Aviator Gulls         | league | 2           | Iceland  | 10/31/2017 07:00 PM | 10/31/2017 09:00 PM | US/Eastern | 1      |
    And I login with "user1@ayrabo.com" and "myweakpassword"
    And I am on the "teams:schedule" page with kwargs "team_pk=1"
    Then "create-game-btn" should not exist on the page
    And "create-game-btn-empty-state" should not exist on the page
    And "i.fa.fa-pencil" should not exist on the page

  Scenario: Navigate to team detail schedule page for a past season
    Given The following season object exists
      | id | league                            | start_date | end_date | teams                 |
      | 2  | Long Island Amateur Hockey League | -1y        | -5d      | Green Machine IceCats |
    And I am on the "teams:schedule" page with kwargs "team_pk=1"
    And I press "tab-item-past-seasons"
    And I press "past-season-2"
    Then I should be on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=2"

  Scenario: View team detail schedule page for a past season
    Given The following season object exists
      | id | league                            | start_date | end_date | teams                 |
      | 2  | Long Island Amateur Hockey League | -1y        | -5d      | Green Machine IceCats |
    And I am on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=2"
    Then I should see "This season has been archived."
    And I should see "The current season's schedule is available"
