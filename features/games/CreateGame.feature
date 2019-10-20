Feature: Create game
  As a manager,
  I want to be able to create a game for my team,
  so the system can keep track of my team's games, display games to users, etc.

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 3  | Long Island Rebels    | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 4  | Nassau County Lions   | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 5  | Aviator Gulls         | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
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
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to game create page from dashboard
    Given I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "manager-tab"
    And I press "actions-dropdown-manager-green-machine-icecats"
    And I press "create_game_btn_green-machine-icecats"
    Then I should be on the "teams:games:create" page with kwargs "team_pk=1"

  Scenario: Navigate to game create page from team detail schedule page
    Given I am on the "teams:schedule" page with kwargs "team_pk=1"
    When I press "create-game-btn"
    Then I should be on the "teams:games:create" page with kwargs "team_pk=1"

  Scenario: Informative text displayed to user
    Given I am on the "teams:games:create" page with kwargs "team_pk=1"
    Then I should see "Green Machine IceCats - Midget Minor AA"
    And I should see "Long Island Amateur Hockey League"
    And I should see "Create Game"
    And I should see "Make sure the date and time entered for Game Start and Game End are for the timezone you choose."
    And I should see "All dates and times will be automatically displayed in common timezones throughout ayrabo.com."

  Scenario: Valid form
    Given I am on the "teams:games:create" page with kwargs "team_pk=1"
    And I select "Aviator Gulls - Midget Minor AA" from "id_home_team"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_away_team"
    And I select "Exhibition" from "id_type"
    And I select "2" from "id_point_value"
    And I select "Iceland" from "id_location"
    And I fill in "id_start" with date "today" and time "07:00 PM"
    And I fill in "id_end" with date "today" and time "09:00 PM"
    And I select "1" from "id_season"
    And I press "create_game_btn"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=1"
    And I should see "Your game has been created."

  Scenario: Invalid form
    Given I am on the "teams:games:create" page with kwargs "team_pk=1"
    And I select "Aviator Gulls - Midget Minor AA" from "id_home_team"
    And I select "Aviator Gulls - Midget Minor AA" from "id_away_team"
    And I select "Exhibition" from "id_type"
    And I select "2" from "id_point_value"
    And I select "Iceland" from "id_location"
    And I fill in "id_start" with date "today" and time "07:00 PM"
    And I fill in "id_end" with date "today" and time "09:00 PM"
    And I select "1" from "id_season"
    And I press "create_game_btn"
    Then I should see "This team must be different than the home team."
