Feature: Create player in the system
  As a player,
  So that I can register for multiple sports and choose a team for each sport
  I want to be able to register for multiple sports and teams

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       | create_userprofile |
      | John       | Doe       | user@example.com | myweakpassword | false              |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA"
    And I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:create" page
    And I press "id_roles_1"
    And I select "male" from "id_gender"
    And I select "4" from "id_birthday_month"
    And I select "4" from "id_birthday_day"
    And I select "1994" from "id_birthday_year"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"

  Scenario: Submit valid player form
    Given I am on the "profile:finish" page
    When I select "1" from "id_hockeyplayer-team"
    And I fill in "id_hockeyplayer-jersey_number" with "35"
    And I select "G" from "id_hockeyplayer-position"
    And I select "Left" from "id_hockeyplayer-handedness"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

  Scenario: Submit invalid player form
    Given I am on the "profile:finish" page
    When I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 4 times
