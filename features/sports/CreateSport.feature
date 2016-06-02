Feature: Create a sport to organize all other models, views, controllers under
  As a developer/user of the site
  So that I can organize teams, games, players for a specific sport and allow for more sports to be added
  I want to be able to create a sport that is a wrapper for everything on the website

  Background: User account exists
    Given The following confirmed user accounts exist
      | first_name | last_name | email             | password       |
      | John       | Doe       | staff@example.com | myweakpassword |
      | Jane       | Doe       | user@example.com  | myweakpassword |
    And "staff@example.com" has the following permissions "is_staff"

  Scenario: Navigate to the create sport page
    Given I login with "staff@example.com" and "myweakpassword"
    When I press "create_dropdown_btn"
    And I press "new_sport_link"
    Then I should be on the "create_sport" page

  Scenario: Create a new sport as a staff member
    Given I login with "staff@example.com" and "myweakpassword"
    And I am on the "create_sport" page
    When I fill in "id_name" with "Hockey"
    And I press "create_sport_btn"
    Then I should see "Hockey successfully created"
    And I should be on the "home" page

  Scenario: Attempt to create sport that already exists
    Given I have a confirmed "administrator" account
    And I login with valid credentials
    And "Hockey" already exists as a sport
    And I am on the "create_sport" page
    When I fill in "sport_name" with "Hockey"
    And I press "create_sport"
    Then I should see "Hockey already exists (case-insensitive)"

  Scenario: Attempt to create sport with invalid characters
    Given I have a confirmed "administrator" account
    And I login with valid credentials
    And I am on the "create_sport" page
    When I fill in "sport_name" with "hoc!@#^&y"
    And I press "create_sport"
    Then I should see "Name is invalid"

  Scenario: Attempt to create sport with blank name
    Given I have a confirmed "administrator" account
    And I login with valid credentials
    And I am on the "create_sport" page
    When I fill in "sport_name" with ""
    And I press "create_sport"
    Then I should see "Name can't be blank"

  Scenario: Unable to create new sport as non-admin
    Given I have a confirmed account
    And I login with valid credentials
    And I am on the "create_sport" page
    Then I should see "You are not authorized to access this page."


  Scenario: Not logged in

