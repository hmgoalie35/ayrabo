# use admin panel for all actions
Feature: League: used to organize a sport (i.e. Ice Hockey -> NHL, AHL, LIAHL, etc)
  As a developer/user of the site
  So that I can group teams, games, players, under a specific league
  I want to be able to create a league that is used to organize teams for a sport


  Background: Staff user exists and is logged into admin panel
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And "user@example.com" has the following permissions "is_staff is_superuser"
    And "user@example.com" is completely registered for "Ice Hockey" with roles "Coach, Referee"
    And I am on the "admin:login" page
    And I fill in "id_username" with "user@example.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "#login-form > div.submit-row > input[type="submit"]"
    
  Scenario: Make sure league is registered with admin panel
    When I press "Leagues"
    Then I should be on the "admin:leagues_league_changelist" page
    And I should see "Add league"
