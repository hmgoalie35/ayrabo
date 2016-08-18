Feature: Create manager in the system
  As a manager,
  So that I can manage my team
  I want to be able to register as a manager for the team I am managing

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA" in league "Long Island Amateur Hockey League" in sport "Ice Hockey"
    And "user@example.com" is registered for "Ice Hockey" with role "Manager"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Submit valid manager form
    Given I am on the "sport:finish_sport_registration" page
    When I select "Green Machine IceCats - Midget Minor AA" from "id_manager-team"
    And I press "next_sport_registration_btn"
    Then I should see "Your profile is now complete, you may now access the site"
    And I should see "You have finished registering for Ice Hockey."
    And I should be on the "home" page

  Scenario: Submit invalid manager form
    Given I am on the "sport:finish_sport_registration" page
    When I press "next_sport_registration_btn"
    Then I should be on the "sport:finish_sport_registration" page
    And "This field is required." should show up 1 time
