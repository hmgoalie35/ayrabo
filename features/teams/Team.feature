# use admin panel for all actions
Feature: Team: used to organize players, coaches, managers, scoresheets, etc.
  As a developer/user of the site
  So that I can group players, coaches, scoresheets and more under a specific team
  I want to be able to create a team that is used to organize players, coaches, scoresheets, etc


  Background: Staff user exists and is logged into admin panel
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And "user@ayrabo.com" has the following permissions "is_staff is_superuser"
    And "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Coach, Referee"
    And I am on the "admin:login" page
    And I fill in "id_username" with "user@ayrabo.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "#login-form > div.submit-row > input[type='submit']"

  Scenario: Make sure team is registered with admin panel
    When I press "Teams"
    Then I should be on the "admin:teams_team_changelist" page
    And I should see "Add team"
