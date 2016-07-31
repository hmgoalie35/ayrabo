Feature: Create player in the system
  As a player,
  So that I can register for multiple sports and choose a team for each sport
  I want to be able to register for multiple sports and teams

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA"
    And A rolesmask exists for "user@example.com" for "Ice Hockey" with role "Player"
    And I login with "user@example.com" and "myweakpassword"

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
