Feature: Create referee in the system
  As a referee,
  So that I can signup to officiate games
  I want to be able to register as a referee for a bunch of divisions

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following division exists "Midget Minor AA" in league "Long Island Amateur Hockey League"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Submit valid referee form
    Given "user@example.com" has a userprofile with role "Referee"
    And I am on the "profile:finish" page
    When I select "Midget Minor AA - LIAHL" from "id_referee-division"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

  Scenario: Submit invalid referee form
    Given "user@example.com" has a userprofile with role "Referee"
    And I am on the "profile:finish" page
    When I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 1 time
