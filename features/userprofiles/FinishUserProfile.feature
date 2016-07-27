Feature: Finish userprofile, filling in any coach/manager/player/referee specific info
  As a site user with multiple roles,
  So that I can be any combinations of player, manager, coach, referee
  I want to be able to register as any combination of player, manager, coach, referee

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following league exists "Long Island Amateur Hockey League"
    And The following division exists "Midget Minor AA" in league "Long Island Amateur Hockey League"
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Forms rendered correctly for Coach and Manager roles
    Given "user@example.com" has a userprofile with roles "Coach, Manager"
    And I am on the "profile:finish" page
    Then I should see "Coach"
    And I should see "Manager"
    And I should not see "Player"
    And I should not see "Referee"

  Scenario: Submit valid form for Coach and Manager roles
    Given "user@example.com" has a userprofile with roles "Coach, Manager"
    And I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_coach-team"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_manager-team"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

  Scenario: Submit invalid form for Coach and Manager roles
    Given "user@example.com" has a userprofile with roles "Coach, Manager"
    Given I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 2 times

  Scenario: Submit valid form for Coach, Manager, Referee roles
    Given "user@example.com" has a userprofile with roles "Coach, Manager, Referee"
    And I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_coach-team"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_manager-team"
    And I select "Long Island Amateur Hockey League" from "id_referee-league"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

  Scenario: Submit invalid form for Coach, Manager, Referee roles
    Given "user@example.com" has a userprofile with roles "Coach, Manager, Referee"
    Given I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_coach-team"
    And I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 2 times

  Scenario: Submit valid form for Coach, Manager, Referee, Player roles
    Given "user@example.com" has a userprofile with roles "Coach, Manager, Referee, Player"
    And I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_hockeyplayer-team"
    And I fill in "id_hockeyplayer-jersey_number" with "35"
    And I select "G" from "id_hockeyplayer-position"
    And I select "Left" from "id_hockeyplayer-handedness"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_coach-team"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_manager-team"
    And I select "Long Island Amateur Hockey League" from "id_referee-league"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

  Scenario: Submit invalid form for Coach, Manager, Referee, Player roles
    Given "user@example.com" has a userprofile with roles "Coach, Manager, Referee, Player"
    Given I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_coach-team"
    And I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 6 times
