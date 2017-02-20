Feature: Remove roles from sport registration
  As a user of the site,
  So that I can remove any roles I do not utilize
  I want to be able to remove roles I have for a sport.

  Background: User and sport registration exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Modal prompts user to confirm action
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player, Coach, Referee, Manager"
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "remove_player_icon"
    Then I should see "Are you sure?"
    And I should see "Remove player role from Ice Hockey"
    And I should see "You will no longer have access to player specific functionality for Ice Hockey."

  Scenario: Remove a role, user has all roles
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player, Coach, Referee, Manager"
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I press "remove_player_icon" which opens "remove_player_modal"
    And I press "remove_player_role_btn"
    And I wait for a page refresh
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should not see "Ice Hockey Player"

  Scenario: Remove a role when only one role left
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player"
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "remove_player_icon_disabled"
    Then I should not see "Remove player role from Ice Hockey"
    And I should see "Ice Hockey Player"
