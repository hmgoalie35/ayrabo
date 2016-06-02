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

  Scenario: Navigate to the create sport page as staff
    Given I login with "staff@example.com" and "myweakpassword"
    When I press "create_dropdown_btn"
    And I press "new_sport_link"
    Then I should be on the "create_sport" page

  Scenario: Can't navigate to create sport page as non staff
    Given I login with "user@example.com" and "myweakpassword"
    When I go to the "home" page
    Then I should not see "Sport"

  Scenario: Create a new sport as a staff member
    Given I login with "staff@example.com" and "myweakpassword"
    And I am on the "create_sport" page
    When I fill in "id_name" with "Hockey"
    And I press "create_sport_btn"
    Then I should see "Hockey successfully created"
    And I should be on the "home" page

  Scenario: Attempt to create sport that already exists
    Given I login with "staff@example.com" and "myweakpassword"
    And The sport "Hockey" already exists
    And I am on the "create_sport" page
    When I fill in "id_name" with "Hockey"
    And I press "create_sport_btn"
    Then I should see "Sport with this name already exists (case-insensitive)"

  Scenario: Attempt to create sport with blank name
    Given I login with "staff@example.com" and "myweakpassword"
    And I am on the "create_sport" page
    When I fill in "id_name" with ""
    And I press "create_sport_btn"
    Then I should see "This field is required"

  Scenario: Unable to create new sport as non-admin
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "create_sport" page
    Then I should see "You do not have permission to access the requested page"

  Scenario: Not logged in
    Given I go to the "create_sport" page
    Then I should be on the "account_login" page

