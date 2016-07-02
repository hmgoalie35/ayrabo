Feature: Edit information associated with my account
  As a user of the site
  So that I can keep my information up to date
  I want to be able to update my account


  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       | create_userprofile |
      | John       | Doe       | user@example.com | myweakpassword | false              |
    And The following userprofile exists for "user@example.com"
      | gender | birthday   |
      | Male   | 1996-02-12 |

  Scenario: Navigate to edit account page when authenticated
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "home" page
    When I press "account_menu"
    And I press "edit_account_link"
    Then I should be on the "profile:update" page

  Scenario: Navigate to edit account page when not authenticated
    Given I am on the "home" page
    When I go to the "profile:update" page
    Then I should be on the "account_login" page

  # See ChangePassword.feature for steps regarding actually changing the password
  Scenario: Navigate to change password page if I am already logged in
    Given I login with "user@example.com" and "myweakpassword"
    And I go to the "profile:update" page
    When I press "change_password_link"
    Then I should be on the "account_change_password" page

  Scenario: Name, email, gender, birthday are displayed
    Given I login with "user@example.com" and "myweakpassword"
    When I go to the "profile:update" page
    Then I should see "John Doe"
    And I should see "user@example.com"
    And I should see "Male"
    And I should see "Feb. 12, 1996"

  Scenario: Submit unchanged form
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:update" page
    When I press "update_userprofile_btn"
    Then I should not see "Your profile has been updated"
    And I should be on the "profile:update" page

  Scenario: Submit changed form
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:update" page
    When I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "120"
    And I press "update_userprofile_btn"
    Then I should see "Your profile has been updated"
    And I should be on the "profile:update" page
