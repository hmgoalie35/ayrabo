Feature: Finish sport registration, filling in any coach/manager/player/referee specific info
  As a site user with one or more sport registrations,
  So that I can specify what position, handedness, team, etc. for player, coach, referee, manager, etc.
  I want to be able to fill out any role specific information

  Background: User exists with incomplete sport registrations
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team objects exist
      | name                  | division          | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA   | Long Island Amateur Hockey League | Ice Hockey |
      | Knicks                | Atlantic Division | National Basketball Association   | Basketball |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Redirect when trying to navigate to profile create page when sport registration not complete
    Given "user@example.com" is registered for "Ice Hockey" with roles "Player, Coach, Referee, Manager"
    And "user@example.com" is registered for "Basketball" with roles "Player, Coach, Referee, Manager"
    When I go to the "profile:create" page
    Then I should be on the "sport:finish_sport_registration" page

  Scenario: Redirect when trying to navigate to create sport registration page when sport registration not complete
    Given "user@example.com" is registered for "Ice Hockey" with roles "Player, Coach, Referee, Manager"
    And "user@example.com" is registered for "Basketball" with roles "Player, Coach, Referee, Manager"
    When I go to the "sport:create_sport_registration" page
    Then I should be on the "sport:finish_sport_registration" page

  Scenario: Forms rendered correctly for ice hockey Coach and Manager roles
    Given "user@example.com" is registered for "Ice Hockey" with roles "Coach, Manager"
    And "user@example.com" is registered for "Basketball" with roles "Coach, Manager"
    And I am on the "sport:finish_sport_registration" page
    Then I should see "Ice Hockey"
    And I should see "Please fill out any role specific information below."
    And I should see "Ice Hockey Coach"
    And I should see "Ice Hockey Manager"
    And I should not see "Ice Hockey Player"
    And I should not see "Ice Hockey Referee"
    And I should see "2 sport registrations remaining"
    And I should see "Next sport registration"

  Scenario: Submit valid form for ice hockey and Coach and Manager roles
    Given "user@example.com" is registered for "Ice Hockey" with roles "Coach, Manager"
    And "user@example.com" is registered for "Basketball" with roles "Coach, Manager"
    And I am on the "sport:finish_sport_registration" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_coach-team"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_manager-team"
    And I should see "Next sport registration"
    And I press "next_sport_registration_btn"
    Then I should see "1 sport registration remaining"
    And I should be on the "sport:finish_sport_registration" page
    And I should see "Finish sport registration"

  Scenario: Submit invalid form for Coach and Manager roles
    Given "user@example.com" is registered for "Ice Hockey" with roles "Coach, Manager"
    And "user@example.com" is registered for "Basketball" with roles "Coach, Manager"
    And I am on the "sport:finish_sport_registration" page
    When I select "Head Coach" from "id_coach-position"
    And I press "next_sport_registration_btn"
    Then I should be on the "sport:finish_sport_registration" page
    And "This field is required." should show up 2 times
    And I should see "2 sport registrations remaining"

  Scenario: Submit valid form for basketball Coach, Manager, Referee roles
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Coach, Manager, Referee"
    And "user@example.com" is registered for "Basketball" with roles "Coach, Manager, Referee"
    And I am on the "sport:finish_sport_registration" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Knicks - Atlantic Division" from "id_coach-team"
    And I select "Knicks - Atlantic Division" from "id_manager-team"
    And I select "National Basketball Association" from "id_referee-league"
    And I should see "Finish sport registration"
    And I press "next_sport_registration_btn"
    Then I should see "Your profile is now complete, you may now access the site"
    And I should see "You have finished registering for Basketball."
    And I should be on the "home" page

  Scenario: Submit invalid form for basketball Coach, Manager, Referee roles
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Coach, Manager, Referee"
    And "user@example.com" is registered for "Basketball" with roles "Coach, Manager, Referee"
    And I am on the "sport:finish_sport_registration" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Knicks - Atlantic Division" from "id_coach-team"
    And I press "next_sport_registration_btn"
    Then I should be on the "sport:finish_sport_registration" page
    And "This field is required." should show up 2 times
    And I should see "1 sport registration remaining"

  Scenario: Submit valid form for basketball Coach, Manager, Referee, Player roles
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Coach, Manager, Referee, Player"
    And "user@example.com" is registered for "Basketball" with roles "Coach, Manager, Referee, Player"
    And I am on the "sport:finish_sport_registration" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Knicks - Atlantic Division" from "id_basketballplayer-team"
    And I fill in "id_basketballplayer-jersey_number" with "35"
    And I select "PG" from "id_basketballplayer-position"
    And I select "Left" from "id_basketballplayer-shoots"
    And I select "Knicks - Atlantic Division" from "id_coach-team"
    And I select "Knicks - Atlantic Division" from "id_manager-team"
    And I select "National Basketball Association" from "id_referee-league"
    And I press "next_sport_registration_btn"
    Then I should see "Your profile is now complete, you may now access the site"
    And I should see "You have finished registering for Basketball."
    And I should be on the "home" page

  Scenario: Submit invalid form for basketball Coach, Manager, Referee, Player roles
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Coach, Manager, Referee, Player"
    And "user@example.com" is registered for "Basketball" with roles "Coach, Manager, Referee, Player"
    Given I am on the "sport:finish_sport_registration" page
    When I select "Head Coach" from "id_coach-position"
    And I select "Knicks - Atlantic Division" from "id_coach-team"
    And I press "next_sport_registration_btn"
    Then I should be on the "sport:finish_sport_registration" page
    And "This field is required." should show up 6 times
    And I should see "1 sport registration remaining"
