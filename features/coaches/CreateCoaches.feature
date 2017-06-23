Feature: Multiple coach registration
  As a coach,
  I want to be able to register as multiple coaches for the same sport

  Background: Finish userprofile creation
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@example.com" is registered for "Ice Hockey" with role "Coach"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Submit valid coach form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_coaches-0-team"
    And I select "head_coach" from "id_coaches-0-position"
    And I press "create_objects_btn"
    Then I should see "You have been registered as a coach for the Green Machine IceCats."
    And I should be on the "home" page

  Scenario: Submit invalid coach form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"
    And I press "create_objects_btn"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"
    And "This field is required." should show up 2 times

  Scenario: Add another coach form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"
    When I press "add_another_form_btn"
    Then "id_coaches-TOTAL_FORMS" should have value "2"

  Scenario: Remove added coach form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"
    When I press "add_another_form_btn"
    And I press ".fa.fa-trash.fa-trash-red"
    And I wait for ".multiField" to be removed
    Then "id_coaches-TOTAL_FORMS" should have value "1"

  Scenario: Add form but don't fill it out
    Given I am on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"
    And I press "add_another_form_btn"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_coaches-0-team"
    And I select "assistant_coach" from "id_coaches-0-position"
    And I press "create_objects_btn"
    Then I should be on the "home" page

  Scenario: Submit 2 valid forms
    Given I am on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"
    And I press "add_another_form_btn"
    And I press "add_another_form_btn"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_coaches-0-team"
    And I select "head_coach" from "id_coaches-0-position"
    And I select "Long Island Edge - Midget Minor AA" from "id_coaches-1-team"
    And I select "assistant_coach" from "id_coaches-1-position"
    And I press "create_objects_btn"
    Then I should see "You have been registered as a coach for the Green Machine IceCats, Long Island Edge."
    And I should be on the "home" page

