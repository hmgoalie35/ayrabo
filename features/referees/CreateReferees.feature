Feature: Multiple referee registration
  As a referee,
  I want to be able to register as multiple referees for the same sport

  Background: Finish userprofile creation
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following league objects exist
      | full_name                         | sport      |
      | Long Island Amateur Hockey League | Ice Hockey |
      | National Hockey League            | Ice Hockey |
    And "user@ayrabo.com" is registered for "Ice Hockey" with role "Referee"
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Submit valid referee form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"
    When I select "Long Island Amateur Hockey League" from "id_referees-0-league"
    And I press "create_objects_btn"
    Then I should see "You have been registered as a referee for the LIAHL."

  Scenario: Submit invalid referee form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"
    And I press "create_objects_btn"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"
    And "This field is required." should show up 1 time

  Scenario: Add another referee form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"
    When I press "add_another_form_btn"
    Then "id_referees-TOTAL_FORMS" should have value "2"

  Scenario: Remove added referee form
    Given I am on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"
    When I press "add_another_form_btn"
    And I press ".fa.fa-trash.fa-trash-red"
    And I wait for ".multiField" to be removed
    Then "id_referees-TOTAL_FORMS" should have value "1"

  Scenario: Add form but don't fill it out
    Given I am on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"
    And I press "add_another_form_btn"
    When I select "Long Island Amateur Hockey League" from "id_referees-0-league"
    And I press "create_objects_btn"

  Scenario: Submit 2 valid forms
    Given I am on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"
    And I press "add_another_form_btn"
    And I press "add_another_form_btn"
    When I select "Long Island Amateur Hockey League" from "id_referees-0-league"
    And I select "National Hockey League" from "id_referees-1-league"
    And I press "create_objects_btn"
    Then I should see "You have been registered as a referee for the LIAHL, NHL."
