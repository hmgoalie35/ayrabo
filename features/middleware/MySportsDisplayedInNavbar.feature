Feature: Quick access to registered sports
  As a user,
  I want to be able to quickly access all sports I have registered or,
  So that I can access role specific functionality for said sports.

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following sport objects exist
      | name       |
      | Ice Hockey |
      | Baseball   |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Registered for one sport
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player"
    And I go to the "home" page
    Then I should see "Ice Hockey"
    And I should not see "Baseball"
    And I should see "Register for a sport"

  Scenario: Registered for 2 sports
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player"
    And "user@example.com" is completely registered for "Baseball" with role "Coach"
    And I go to the "home" page
    And I should see "Ice Hockey"
    And I should see "Baseball"
    And I should see "Register for a sport"
