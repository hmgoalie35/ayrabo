Feature: Bulk upload teams from csv
  As a staff member
  So that I can upload many teams at once
  I want to be able to upload teams from a .csv file

  Background: Staff user exists and is logged into admin panel
    Given The following confirmed user account exists
      | first_name | last_name | email                  | password       |
      | John       | Doe       | user@example.com       | myweakpassword |
      | Jane       | Doe       | non_staff@example.com | myweakpassword |
    And "user@example.com" has the following permissions "is_staff is_superuser"

  Scenario: Navigate to bulk upload team page
    Given I am on the "admin:login" page
    And I fill in "id_username" with "user@example.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "#login-form > div.submit-row > input[type="submit"]"
    And I am on the "admin:teams_team_changelist" page
    When I press "bulk_upload_teams_btn"
    Then I should be on the "bulk_upload_teams" page

  Scenario: Download example csv
    Given I am on the "admin:login" page
    And I fill in "id_username" with "user@example.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "#login-form > div.submit-row > input[type="submit"]"
    And I am on the "admin:teams_team_changelist" page
    Then I should see "Download Example .csv"

  Scenario: Must be logged in to access bulk upload team page
    When I go to the "bulk_upload_teams" page
    Then I should be on the "account_login" page

  Scenario: Must be staff to access bulk upload team page
    Given I login with "non_staff@example.com" and "myweakpassword"
    When I go to the "bulk_upload_teams" page
    Then I should be on the "home" page

  Scenario: Upload valid file
    Given I am on the "admin:login" page
    And I fill in "id_username" with "user@example.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "#login-form > div.submit-row > input[type="submit"]"
    And I am on the "bulk_upload_teams" page
    And The following division exists "Midget Minor AA"
    When I upload "valid_team_csv_formatting.csv" into "id_file"
    And I press "bulk_upload_submit_btn"
    Then I should see "1 out of 1 teams successfully created"

  Scenario: Upload invalid file
    Given I am on the "admin:login" page
    And I fill in "id_username" with "user@example.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "#login-form > div.submit-row > input[type="submit"]"
    And I am on the "bulk_upload_teams" page
    When I upload "division_dne.csv" into "id_file"
    And I press "bulk_upload_submit_btn"
    Then I should see "The division Division DNE does not currently exist, you need to create it under the correct league and sport"
