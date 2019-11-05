Feature: Change password when logged in
  As a user,
  I want to be able to change my password when I already know it.

  Background: User account exists
    Given The following users exist
      | id | first_name | last_name | email           | username        | password       |
      | 1  | John       | Doe       | user@ayrabo.com | user@ayrabo.com | myweakpassword |

  Scenario: Login required
    Given I am on the "home" page
    When I go to the "account_change_password" page
    Then I should be on the "account_login" page

  Scenario: Navigate to change password page
    Given I login with "user@ayrabo.com" and "myweakpassword"
    And I am on the "users:detail" page with kwargs "pk=1"
    When I press "tab-item-change-password"
    Then I should be on the "account_change_password" page

  Scenario: Navigate back to user detail page
    Given I login with "user@ayrabo.com" and "myweakpassword"
    And I am on the "account_change_password" page
    When I press "tab-item-information"
    Then I should be on the "users:detail" page with kwargs "pk=1"

  Scenario: Valid form
    Given I login with "user@ayrabo.com" and "myweakpassword"
    And I am on the "account_change_password" page
    When I fill in "id_oldpassword" with "myweakpassword"
    And I fill in "id_password1" with "mynewpassword"
    And I fill in "id_password2" with "mynewpassword"
    And I press "change_password_btn"
    Then I should see "Your password has been updated."
    And I should be on the "users:detail" page with kwargs "pk=1"

  Scenario: Invalid form
    Given I login with "user@ayrabo.com" and "myweakpassword"
    And I am on the "account_change_password" page
    When I fill in "id_oldpassword" with "notmycurrentpassword"
    And I fill in "id_password1" with "mynewpassword"
    And I fill in "id_password2" with "mynewpassword"
    And I press "change_password_btn"
    Then I should see "Please type your current password."
