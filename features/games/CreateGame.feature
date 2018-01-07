Feature: Create hockey game
  As a manager,
  I want to be able to create a hockey game for my team,
  so the system can keep track of my team's games, display games to users, etc.

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 3  | Long Island Rebels    | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 4  | Nassau County Lions   | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 5  | Aviator Gulls         | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager objects exist
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And The following generic choice objects exist
      | content_type | short_value | long_value | type             |
      | sports.Sport | exhibition  | Exhibition | game_type        |
      | sports.Sport | league      | League     | game_type        |
      | sports.Sport | 2           | 2          | game_point_value |
    And The following location object exists
      | name    |
      | Iceland |
    And The following season object exists
      | league                            | start_date | end_date   | teams                 |
      | Long Island Amateur Hockey League | 2017-09-14 | 2018-09-14 | Green Machine IceCats |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Navigate to hockey game create page
    Given I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I press "manager_tab"
    And I press "actions-dropdown-manager-green-machine-icecats"
    And I press "create_game_btn_green-machine-icecats"
    Then I should be on the "/teams/1/games/create/" page

  Scenario: Informative text displayed to user
    Given I am on the "/teams/1/games/create/" page
    Then I should see "Create Hockey Game for Green Machine IceCats"
    And I should see "Midget Minor AA - LIAHL"
    And I should see "Make sure the date and time entered for Game Start and Game End are for the timezone you choose."
    And I should see "All dates and times will be automatically displayed in common timezones throughout example.com."

  Scenario: Valid form
    Given I am on the "/teams/1/games/create/" page
    And I select "Aviator Gulls - Midget Minor AA" from "id_home_team"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_away_team"
    And I select "Exhibition" from "id_type"
    And I select "2" from "id_point_value"
    And I select "Iceland" from "id_location"
    And I fill in "id_start" with "12/26/2017 07:00 PM"
    And I fill in "id_end" with "12/26/2017 09:00 PM"
    And I select "LIAHL: 2017-2018 Season" from "id_season"
    And I press "create_game_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Your game has been created."

  Scenario: Invalid form
    Given I am on the "/teams/1/games/create/" page
    And I press "create_game_btn"
    Then "This field is required." should show up 8 times
