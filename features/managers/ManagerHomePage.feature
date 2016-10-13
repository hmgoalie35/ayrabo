Feature: Manager home page
  As a manager of a team
  So that I can manage teams I am a manager for
  I want to be able to see all teams I manage and create season rosters, game rosters, etc

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA" in league "Long Island Amateur Hockey League" in sport "Ice Hockey"
    And The following team exists "New York Yankees" in division "American League East" in league "Major League Baseball" in sport "Baseball"
    And I login with "user@example.com" and "myweakpassword"
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    Given "user@example.com" is completely registered for "Baseball" with role "Manager"
    And The following manager objects exist
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
      | user@example.com  | New York Yankees      |

  Scenario: Navigate to manager home page
    Given I am on the "home" page
    When I press "manager_menu"
    And I press "manager_home"
    Then I should be on the "manager:home" page

  Scenario: Informative text about the page exists
    Given I am on the "manager:home" page
    Then I should see "Team List"
    And I should see "Showing all teams you are a manager for"

  Scenario: All teams the manager manages are displayed
    Given I am on the "manager:home" page
    Then I should see "Green Machine IceCats"
    And I should see "Midget Minor AA"
    And I should see "Long Island Amateur Hockey League"
    And I should see "Ice Hockey"

  Scenario: Manager functions for a specific team become visible after clicking button
    Given I am on the "manager:home" page
    When I press "green-machine-icecats_manage_link"
    And I press "new-york-yankees_manage_link"
    Then "green-machine-icecats_create_season_roster_btn" should be visible
    And "green-machine-icecats_list_season_rosters_btn" should be visible
    And "new-york-yankees_create_season_roster_btn" should be visible
    And "new-york-yankees_list_season_rosters_btn" should be visible
