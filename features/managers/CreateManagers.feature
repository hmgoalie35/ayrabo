Feature: Multiple manager registration
  As a manager,
  I want to be able to register as multiple managers for the same sport

  Background: Finish userprofile creation
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@ayrabo.com" is registered for "Ice Hockey" with role "Manager"
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Submit valid manager form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_managers-0-team"
    And I press "create_objects_btn"
    Then I should see "You have been registered as a manager for the Green Machine IceCats."

  Scenario: Submit invalid manager form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
    And I press "create_objects_btn"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
    And "This field is required." should show up 1 time

  Scenario: Add another manager form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
    When I press "add_another_form_btn"
    Then "id_managers-TOTAL_FORMS" should have value "2"

  Scenario: Remove added manager form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
    When I press "add_another_form_btn"
    And I press ".fa.fa-trash.fa-trash-red"
    And I wait for ".multiField" to be removed
    Then "id_managers-TOTAL_FORMS" should have value "1"

  Scenario: Add form but don't fill it out
    Given I am on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
    And I press "add_another_form_btn"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_managers-0-team"
    And I press "create_objects_btn"

  Scenario: Submit 2 valid forms
    Given I am on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
    And I press "add_another_form_btn"
    And I press "add_another_form_btn"
    When I select "Green Machine IceCats - Midget Minor AA" from "id_managers-0-team"
    And I select "Long Island Edge - Midget Minor AA" from "id_managers-1-team"
    And I press "create_objects_btn"
    Then I should see "You have been registered as a manager for the Green Machine IceCats, Long Island Edge."
