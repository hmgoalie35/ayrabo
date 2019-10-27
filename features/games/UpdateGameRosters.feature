Feature: Update game rosters
  As a scorekeeper or manager,
  I want to be able to update the game rosters
  So that it is known what players are partaking in the game

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email              | password       |
      | John       | Doe       | user@ayrabo.com    | myweakpassword |
      | Jane       | Doe       | user1@ayrabo.com   | myweakpassword |
      | Michael    | Scott     | michael@scott.com  | myweakpassword |
      | Dwight     | Schrute   | dwight@schrute.com | myweakpassword |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And "user1@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And "michael@scott.com" is completely registered for "Ice Hockey" with role "Scorekeeper"
    And "dwight@schrute.com" is completely registered for "Ice Hockey" with role "Player"
    And The following manager objects exist
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
      | user1@ayrabo.com  | Long Island Edge      |
    And The following scorekeeper object exists
      | username_or_email | sport      |
      | michael@scott.com | Ice Hockey |
    And The following player object exists
      | username_or_email  | sport      | team                  |
      | dwight@schrute.com | Ice Hockey | Green Machine IceCats |
    And The following generic choice objects exist
      | content_type | short_value | long_value | type             |
      | sports.Sport | league      | League     | game_type        |
      | sports.Sport | 2           | 2          | game_point_value |
    And The following location object exists
      | name    |
      | Iceland |
    And The following seasons exist
      | id | league                            | start_date | end_date   | teams                 |
      | 1  | Long Island Amateur Hockey League | 2017-09-14 | 2018-09-14 | Green Machine IceCats |
    And The following game objects exist
      | id | home_team             | away_team        | type   | point_value | location | start               | end                 | timezone   | season |
      | 1  | Green Machine IceCats | Long Island Edge | league | 2           | Iceland  | 10/25/2017 07:00 PM | 10/25/2017 09:00 PM | US/Eastern | 1      |

  Scenario: Navigate to game roster update page as home team manager
    Given I login with "user@ayrabo.com" and "myweakpassword"
    And I am on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=1"
    When I press "actions-dropdown-1"
    And I press "update-game-rosters-1"
    Then I should be on the "sports:games:rosters:update" page with kwargs "slug=ice-hockey, game_pk=1"
    And I should see "Update Game Rosters"
    And I should see "Game #1"
    And I should see "10/25/2017 07:00 PM EDT at Iceland"

  Scenario: Navigate to game roster update page as away team manager
    Given I login with "user1@ayrabo.com" and "myweakpassword"
    And I am on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=1"
    When I press "actions-dropdown-1"
    And I press "update-game-rosters-1"
    Then I should be on the "sports:games:rosters:update" page with kwargs "slug=ice-hockey, game_pk=1"

  Scenario: Navigate to game roster update page as scorekeeper for the team's sport
    Given I login with "michael@scott.com" and "myweakpassword"
    And I am on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=1"
    When I press "actions-dropdown-1"
    And I press "update-game-rosters-1"
    Then I should be on the "sports:games:rosters:update" page with kwargs "slug=ice-hockey, game_pk=1"

  Scenario: Update game roster link not shown to regular users
    Given I login with "dwight@schrute.com" and "myweakpassword"
    And I am on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=1"
    When I press "actions-dropdown-1"
    Then "update-game-rosters-1" should not exist on the page
