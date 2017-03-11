#Feature: Create coach in the system
#  As a coach,
#  So that I can manage my team
#  I want to be able to register as a coach for the team I am coaching
#
#  Background: Go to user profile creation page
#    Given The following confirmed user account exists
#      | first_name | last_name | email            | password       |
#      | John       | Doe       | user@example.com | myweakpassword |
#    And The following team object exists
#      | name                  | division        | league                            | sport      |
#      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
#    And "user@example.com" is registered for "Ice Hockey" with role "Coach"
#    And I login with "user@example.com" and "myweakpassword"
#
#  Scenario: Submit valid coach form
#    Given I am on the "sportregistrations:finish" page
#    When I select "Head Coach" from "id_coach-position"
#    And I select "Green Machine IceCats - Midget Minor AA" from "id_coach-team"
#    And I press "next_sport_registration_btn"
#    Then I should see "You are now registered for Ice Hockey."
#    And I should be on the "home" page
#
#  Scenario: Submit invalid coach form
#    Given I am on the "sportregistrations:finish" page
#    When I select "Head Coach" from "id_coach-position"
#    And I press "next_sport_registration_btn"
#    Then I should be on the "sportregistrations:finish" page
#    And "This field is required." should show up 1 time
