Feature: Create referee in the system
  As a referee,
  So that I can signup to officiate games
  I want to be able to register as a referee for a bunch of divisions

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following league object exists
      | full_name                         | sport      |
      | Long Island Amateur Hockey League | Ice Hockey |
    And "user@example.com" is registered for "Ice Hockey" with role "Referee"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Submit valid referee form
    Given I am on the "sport:finish_sport_registration" page
    When I select "Long Island Amateur Hockey League" from "id_referee-league"
    And I press "next_sport_registration_btn"
    Then I should see "Your profile is now complete, you may now access the site"
    And I should see "You have finished registering for Ice Hockey."
    And I should be on the "home" page

  Scenario: Submit invalid referee form
    Given I am on the "sport:finish_sport_registration" page
    When I press "next_sport_registration_btn"
    Then I should be on the "sport:finish_sport_registration" page
    And "This field is required." should show up 1 time
