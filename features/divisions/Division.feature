# use admin panel for all actions
Feature: Division: used to organize a league (i.e. NHL -> Atlantic, Metropolitan, Central, Pacific Divisions)
  As a developer/user of the site
  So that I can group teams, games, players, under a specific division
  I want to be able to create a division that is used to organize teams for a league


  Background: Staff user exists and is logged into admin panel
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And "user@example.com" has the following permissions "is_staff is_superuser"
    And I am on the "admin:login" page
    And I fill in "id_username" with "user@example.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "#login-form > div.submit-row > input[type="submit"]"

  Scenario: Make sure division is registered with admin panel
    When I press "Divisions"
    Then I should be on the "admin:divisions_division_changelist" page
    And I should see "Add division"
