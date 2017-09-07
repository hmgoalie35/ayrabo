Feature: List what sports I am currently registered for
  As a user of the site,
  So that I can remember what sports I am registered for
  I want to be able to see what sports I have registered for.

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player, Coach, Referee, Manager"
    And "user@example.com" is completely registered for "Baseball" with roles "Player, Coach, Referee, Manager"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: View my sport registrations
    Given I am on the "account_home" page
    When I press "my-sports-tab"
    Then "my_sport_registrations" should be visible
    And I should see "Ice Hockey"
    And I should see "Baseball"

  Scenario: Navigate to new sport registration page when more sports to register for exist
    Given I am on the "account_home" page
    And The following sport exists "Basketball"
    When I press "my-sports-tab"
    And I press "register_for_sport_btn"
    Then I should be on the "sportregistrations:create" page

  Scenario: Navigate to new sport registration page when no more sports to register for exist
    Given I am on the "account_home" page
    When I press "my-sports-tab"
    And I press "register_for_sport_btn"
    Then I should see "You have already registered for all available sports. Check back later to see if any new sports have been added."
    And I should be on the "account_home" page

  Scenario: Expand sport list item
    Given I am on the "account_home" page
    When I press "my-sports-tab"
    And I press "list-item-ice-hockey"
    Then "ice-hockey" should be visible
    Then I should see "Player"
    And I should see "Coach"
    And I should see "Referee"
    And I should see "Manager"

  Scenario: Navigate to update sport registration page
    Given I am on the "account_home" page
    When I press "my-sports-tab"
    And I press "edit-" with kwargs "Ice Hockey"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user@example.com Ice Hockey"
