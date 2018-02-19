# use admin panel for all actions
Feature: Sport: used to create structure for the whole website
  As a developer/user of the site
  So that I can organize teams, games, players for a specific sport and allow for more sports to be added
  I want to be able to create a sport that is a wrapper for everything on the website


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


  Scenario: Make sure sport is registered with admin panel
    When I press "Sports"
    Then I should be on the "admin:sports_sport_changelist" page
    And I should see "Add sport"
