Feature: Edit information associated with my account
  As a user of the site
  So that I can keep my information up to date
  I want to be able to update my account


  Background: User account exists
    Given The following confirmed user accounts exist
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |

  Scenario: Navigate to edit account page when authenticated
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "home" page
    When I press "account_menu"
    And I press "edit_account_link"
    Then I should be on the "account_edit" page

  Scenario: Navigate to edit account page when not authenticated
    Given I am on the "home" page
    When I go to the "account_edit" page
    Then I should be on the "account_login" page

  # See ChangePassword.feature for steps regarding actually changing the password
  Scenario: Navigate to change password page if I am already logged in
    Given I login with "user@example.com" and "myweakpassword"
    And I go to the "account_edit" page
    When I press "change_password_btn"
    Then I should be on the "account_change_password" page
