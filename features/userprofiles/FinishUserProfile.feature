Feature: Finish userprofile, filling in any coach/manager/player/referee specific info
  As a site user with multiple roles,
  So that I can be any combinations of player, manager, coach, referee
  I want to be able to register as any combination of player, manager, coach, referee

  Background: Go to user profile creation page
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA" in league "Long Island Amateur Hockey League" in sport "Ice Hockey"
    And The following team exists "Knicks" in division "Atlantic Division" in league "National Basketball Association" in sport "Basketball"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Try to navigate to profile create page
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager"
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager"
    When I go to the "profile:create" page
    Then I should be on the "profile:finish" page

  Scenario: Try to navigate to select_roles page
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager"
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager"
    When I go to the "profile:select_roles" page
    Then I should be on the "profile:finish" page

  Scenario: Forms rendered correctly for ice hockey Coach and Manager roles
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager"
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager"
    And I am on the "profile:finish" page
    Then I should see "Please fill out the required information for Ice Hockey"
    And I should see "Coach"
    And I should see "Manager"
    And I should not see "Ice Hockey Player"
    And I should not see "Referee"
    And I should see "2 sports remaining"

  Scenario: Submit valid form for ice hockey and Coach and Manager roles
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager"
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager"
    And I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_coach-team"
    And I select "Midget Minor AA - Green Machine IceCats" from "id_manager-team"
    And I press "finish_profile_btn"
    Then I should see "1 sport remaining"
    And I should be on the "profile:finish" page

  Scenario: Submit invalid form for Coach and Manager roles
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager"
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager"
    And I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 2 times
    And I should see "2 sports remaining"

  Scenario: Submit valid form for basketball Coach, Manager, Referee roles
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager, Referee"
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager, Referee"
    And I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Atlantic Division - Knicks" from "id_coach-team"
    And I select "Atlantic Division - Knicks" from "id_manager-team"
    And I select "National Basketball Association" from "id_referee-league"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

  Scenario: Submit invalid form for basketball Coach, Manager, Referee roles
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager, Referee"
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager, Referee"
    And I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Atlantic Division - Knicks" from "id_coach-team"
    And I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 2 times
    And I should see "1 sport remaining"

  Scenario: Submit valid form for basketball Coach, Manager, Referee, Player roles
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager, Referee, Player"
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager, Referee, Player"
    And I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Atlantic Division - Knicks" from "id_basketballplayer-team"
    And I fill in "id_basketballplayer-jersey_number" with "35"
    And I select "PG" from "id_basketballplayer-position"
    And I select "Left" from "id_basketballplayer-shoots"
    And I select "Atlantic Division - Knicks" from "id_coach-team"
    And I select "Atlantic Division - Knicks" from "id_manager-team"
    And I select "National Basketball Association" from "id_referee-league"
    And I press "finish_profile_btn"
    Then I should see "You have successfully completed your profile, you can now access the site"
    And I should be on the "home" page

  Scenario: Submit invalid form for basketball Coach, Manager, Referee, Player roles
    Given A rolesmask exists for "user@example.com" for "Ice Hockey" with roles "Coach, Manager, Referee, Player"
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And A rolesmask exists for "user@example.com" for "Basketball" with roles "Coach, Manager, Referee, Player"
    Given I am on the "profile:finish" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Atlantic Division - Knicks" from "id_coach-team"
    And I press "finish_profile_btn"
    Then I should be on the "profile:finish" page
    And "This field is required." should show up 6 times
    And I should see "1 sport remaining"
