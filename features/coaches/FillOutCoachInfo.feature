Feature: Create coach in the system
  As a coach,
  So that I can manage my team
  I want to be able to register as a coach for the team I am coaching

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       | create_userprofile |
      | John       | Doe       | user@example.com | myweakpassword | false              |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA"
    And I login with "user@example.com" and "myweakpassword"
    And I am on the "create_userprofile" page
    # id_roles_2 is the Coach checkbox
    And I press "id_roles_2"
    And I select "male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"

  Scenario: Submit valid coach form
    Given I am on the "finish_userprofile" page
    When I select "Head Coach" from "id_position"
    And I select "1" from "id_team"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

   Scenario: Submit invalid coach form
     Given I am on the "finish_userprofile" page
     When I select "Head Coach" from "id_position"
     And I press "finish_profile_btn"
     Then I should be on the "finish_userprofile" page
     And "This field is required." should show up 1 time
