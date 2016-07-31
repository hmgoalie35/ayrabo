Feature: Create manager in the system
  As a manager,
  So that I can manage my team
  I want to be able to register as a manager for the team I am managing

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA"
    And A rolesmask exists for "user@example.com" for "Ice Hockey" with role "Manager"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Submit valid manager form
    Given I am on the "profile:finish" page
    When I select "1" from "id_manager-team"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

  Scenario: Submit invalid manager form
    Given I am on the "profile:finish" page
    When I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 1 time
