Feature: Role specific functionality
  As a user of the site (potentially with multiple roles)
  I want to be able to see possible actions I can take for a specific role
  So that I can perform one of said actions

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA" in league "Long Island Amateur Hockey League" in sport "Ice Hockey"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Players menu is displayed in navbar when user has player role
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player"
    And I go to the "home" page
    Then I should see "Players"
    And "player_menu" should be visible

  Scenario: Coaches menu is displayed in navbar when user has coach role
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Coach"
    And I go to the "home" page
    Then I should see "Coaches"
    And "coach_menu" should be visible

  Scenario: Referees menu is displayed in navbar when user has referee role
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Referee"
    And I go to the "home" page
    Then I should see "Referees"
    And "referee_menu" should be visible

  Scenario: Managers menu is displayed in navbar when user has manager role
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And I go to the "home" page
    Then I should see "Managers"
    And "manager_menu" should be visible

  Scenario: Multiple roles, multiple menus should be visible
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player, Manager"
    And I go to the "home" page
    Then I should see "Players"
    And "player_menu" should be visible
    And I should see "Managers"
    And "manager_menu" should be visible
