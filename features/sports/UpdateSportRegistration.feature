Feature: Update sport registration
  As a user of the site,
  So that I can manage my sport registration
  I want to be able to change my jersey number, position, etc.

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA" in league "Long Island Amateur Hockey League" in sport "Ice Hockey"
    And The following sport registrations exist
      | username_or_email | sport      | roles                           | complete |
      | user@example.com  | Ice Hockey | Player, Coach, Manager, Referee | true     |
      | user@example.com  | Baseball   | Player, Coach, Manager, Referee | true     |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And The following coach object exists
      | username_or_email | position   | team                  |
      | user@example.com  | Head Coach | Green Machine IceCats |
    And The following referee object exists
      | username_or_email | league                            |
      | user@example.com  | Long Island Amateur Hockey League |
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Informative text displayed to user
    Given I am on the page for "sports.SportRegistration" and "user@example.com Ice Hockey"
    Then I should see "Update Sport Registration for Ice Hockey"
    And I should see "Current Roles"
    And I should see "Ice Hockey Player"
    And I should see "Ice Hockey Coach"
    And I should see "Ice Hockey Referee"
    And I should see "Ice Hockey Manager"
    And I should see "Changing your team or league is not currently supported."
    And "id_hockeyplayer-team" should be disabled
    And "id_coach-team" should be disabled
    And "id_referee-league" should be disabled
    And "id_manager-team" should be disabled

  Scenario: Submit unchanged form
    Given I am on the page for "sports.SportRegistration" and "user@example.com Ice Hockey"
    When I press "update_sport_registration_btn"
    Then I should be on the page for "sports.SportRegistration" and "user@example.com Ice Hockey"
    And I should not see "Sport registration for Ice Hockey successfully updated."

  Scenario: Submit changed form
    Given I am on the page for "sports.SportRegistration" and "user@example.com Ice Hockey"
    When I fill in "id_hockeyplayer-jersey_number" with "22"
    And I select "Assistant Coach" from "id_coach-position"
    And I press "update_sport_registration_btn"
#    Then I should be on the "account_home" page
    And I should see "Sport registration for Ice Hockey successfully updated."
