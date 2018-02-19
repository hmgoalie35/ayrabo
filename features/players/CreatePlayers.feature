Feature: Multiple player registration
  As a player,
  I want to be able to register as multiple players for the same sport

  Background: Finish userprofile creation
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@ayrabo.com" is registered for "Ice Hockey" with role "Player"
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Submit valid player form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_players-0-team"
    And I fill in "id_players-0-jersey_number" with "35"
    And I select "G" from "id_players-0-position"
    And I select "Left" from "id_players-0-handedness"
    And I press "create_objects_btn"
    Then I should see "You have been registered as a player for the Green Machine IceCats."
    And I should be on the "home" page

  Scenario: Submit invalid player form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"
    And I press "create_objects_btn"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"
    And "This field is required." should show up 4 times

  Scenario: Add another player form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"
    When I press "add_another_form_btn"
    Then "id_players-TOTAL_FORMS" should have value "2"

  Scenario: Remove added player form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"
    When I press "add_another_form_btn"
    And I press ".fa.fa-trash.fa-trash-red"
    And I wait for ".multiField" to be removed
    Then "id_players-TOTAL_FORMS" should have value "1"

  Scenario: Add form but don't fill it out
    Given I am on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"
    And I press "add_another_form_btn"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_players-0-team"
    And I fill in "id_players-0-jersey_number" with "35"
    And I select "G" from "id_players-0-position"
    And I select "Left" from "id_players-0-handedness"
    And I press "create_objects_btn"
    Then I should be on the "home" page

  Scenario: Submit 2 valid forms
    Given I am on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"
    And I press "add_another_form_btn"
    And I press "add_another_form_btn"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_players-0-team"
    And I fill in "id_players-0-jersey_number" with "35"
    And I select "G" from "id_players-0-position"
    And I select "Left" from "id_players-0-handedness"
    And I select "Long Island Edge - Midget Minor AA" from "id_players-1-team"
    And I fill in "id_players-1-jersey_number" with "23"
    And I select "LW" from "id_players-1-position"
    And I select "Left" from "id_players-1-handedness"
    And I press "create_objects_btn"
    Then I should see "You have been registered as a player for the Green Machine IceCats, Long Island Edge."
    And I should be on the "home" page

