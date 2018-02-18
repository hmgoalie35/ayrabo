Feature: Update a game
  As a manager,
  I want to be able to update a game
  So that I can fix incorrect information

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email             | password       |
      | John       | Doe       | user@example.com  | myweakpassword |
      | Jane       | Doe       | user1@example.com | myweakpassword |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 3  | Aviator Gulls         | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And "user1@example.com" is completely registered for "Ice Hockey" with role "Player"
    And The following manager objects exist
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And The following generic choice objects exist
      | content_type | short_value | long_value | type             |
      | sports.Sport | exhibition  | Exhibition | game_type        |
      | sports.Sport | league      | League     | game_type        |
      | sports.Sport | 2           | 2          | game_point_value |
    And The following location object exists
      | name     |
      | Iceland  |
      | IceWorks |
    And The following season object exists
      | id | league                            | start_date | end_date   | teams                 |
      | 1  | Long Island Amateur Hockey League | 2017-09-14 | 2018-09-14 | Green Machine IceCats |
    And The following game objects exist
      | id | home_team             | away_team             | type   | point_value | location | start               | end                 | timezone   | season |
      | 1  | Green Machine IceCats | Long Island Edge      | league | 2           | Iceland  | today               | today               | US/Eastern | 1      |
      | 2  | Long Island Edge      | Green Machine IceCats | league | 2           | Iceland  | 10/30/2017 07:00 PM | 10/30/2017 09:00 PM | US/Eastern | 1      |
      | 3  | Long Island Edge      | Aviator Gulls         | league | 2           | Iceland  | 10/31/2017 07:00 PM | 10/31/2017 09:00 PM | US/Eastern | 1      |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Navigate to game update page
    Given I am on the "teams:games:list" page with kwargs "team_pk=1"
    When I press "actions-dropdown-1"
    And I press "update-game-1"
    Then I should be on the "teams:games:update" page with kwargs "team_pk=1, pk=1"

  Scenario: Informative text shown to user
    Given I am on the "teams:games:update" page with kwargs "team_pk=1, pk=1"
    Then I should see "Update Game #1"
    And I should see "Green Machine IceCats Midget Minor AA vs. Long Island Edge Midget Minor AA"

  Scenario: Submit valid form
    Given I am on the "teams:games:update" page with kwargs "team_pk=1, pk=1"
    And I select "IceWorks" from "id_location"
    And I press "update_game_btn"
    Then I should be on the "teams:games:list" page with kwargs "team_pk=1"
    And I should see "Your game has been updated."

  Scenario: Submit invalid form
    Given I am on the "teams:games:update" page with kwargs "team_pk=1, pk=1"
    And I fill in "id_end" with "10/23/2017 03:00 PM"
    And I press "update_game_btn"
    Then I should see "Game end must be after game start."

  Scenario: Form disabled
    Given The following game object exists
      | id | home_team             | away_team     | type   | point_value | location | start               | end                 | timezone   | season | status    |
      | 4  | Green Machine IceCats | Aviator Gulls | league | 2           | Iceland  | 11/23/2017 07:00 PM | 11/23/2017 10:00 PM | US/Eastern | 1      | completed |
    And I am on the "teams:games:update" page with kwargs "team_pk=1, pk=4"
    Then I should see "Updates to this game are no longer permitted."
    And I should see "Back"
    And "update_game_btn" should not exist on the page

  Scenario: Changing away team launches modal
    Given The following player object exists
      | id | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | 1  | john@tavares.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And "1" is added to "away_players" for the game with kwargs "pk=1"
    And I am on the "teams:games:update" page with kwargs "team_pk=1, pk=1"
    And I select "Aviator Gulls - Midget Minor AA" from "id_away_team"
    And I press "update_game_btn" which opens "roster-warning-modal"
    And I should see "Changing the home team for this game will clear the home team roster if one was set."
    And I should see "Changing the away team for this game will clear the away team roster if one was set."
    And I should see "You will need to set new home team rosters or away team rosters."
    And I press "js-modal-continue"
    Then I should be on the "teams:games:list" page with kwargs "team_pk=1"
    And I should see "Your game has been updated."
