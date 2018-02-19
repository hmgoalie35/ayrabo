Feature: Change password when logged in
  As a user of the site
  So that I can change my password
  I want to be able to change my password

  Background: User account exists
    Given The following confirmed user accounts exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Coach, Referee"

  Scenario: Navigate to change password page when not authenticated
    Given I am on the "home" page
    When I go to the "account_change_password" page
    Then I should be on the "account_login" page

  Scenario: Change password when entering correct current password
    Given I login with "user@ayrabo.com" and "myweakpassword"
    And I am on the "account_change_password" page
    When I fill in "id_oldpassword" with "myweakpassword"
    And I fill in "id_password1" with "mynewpassword"
    And I fill in "id_password2" with "mynewpassword"
    And I press "change_password_btn"
    Then I should see "Password successfully changed."
    And I should be on the "account_home" page

  Scenario: Change password when entering incorrect current password
    Given I login with "user@ayrabo.com" and "myweakpassword"
    And I am on the "account_change_password" page
    When I fill in "id_oldpassword" with "notmycurrentpassword"
    And I fill in "id_password1" with "mynewpassword"
    And I fill in "id_password2" with "mynewpassword"
    And I press "change_password_btn"
    Then I should see "Please type your current password."
