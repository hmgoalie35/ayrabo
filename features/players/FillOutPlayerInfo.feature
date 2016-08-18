Feature: Create player in the system
  As a player,
  So that I can register for multiple sports and choose a team for each sport
  I want to be able to register for multiple sports and teams

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA" in league "Long Island Amateur Hockey League" in sport "Ice Hockey"
    And "user@example.com" is registered for "Ice Hockey" with role "Player"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Submit valid player form
    Given I am on the "sport:finish_sport_registration" page
    When I select "Green Machine IceCats - Midget Minor AA" from "id_hockeyplayer-team"
    And I fill in "id_hockeyplayer-jersey_number" with "35"
    And I select "G" from "id_hockeyplayer-position"
    And I select "Left" from "id_hockeyplayer-handedness"
    And I press "next_sport_registration_btn"
    Then I should see "Your profile is now complete, you may now access the site"
    And I should see "You have successfully registered for Ice Hockey."
    And I should be on the "home" page

  Scenario: Submit invalid player form
    Given I am on the "sport:finish_sport_registration" page
    When I press "next_sport_registration_btn"
    Then I should be on the "sport:finish_sport_registration" page
    And "This field is required." should show up 4 times
