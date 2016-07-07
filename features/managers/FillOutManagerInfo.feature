Feature: Create manager in the system
  As a manager,
  So that I can manage my team
  I want to be able to register as a manager for the team I am managing

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       | create_userprofile |
      | John       | Doe       | user@example.com | myweakpassword | false              |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA"
    And I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:create" page
    # id_roles_4 is the Manager checkbox
    And I press "id_roles_4"
    And I select "male" from "id_gender"
    # 4 stands for April
    And I select "4" from "id_birthday_month"
    And I select "4" from "id_birthday_day"
    And I select "1994" from "id_birthday_year"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"

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
