Feature: Forgotten password
  As a user who has forgotten their password
  So that I can regain access to my account
  I want to be able to reset my password

  Background: Confirmed user account exists
    Given The following users exist
      | first_name | last_name | email           | username        | password       |
      | John       | Doe       | user@ayrabo.com | user@ayrabo.com | myweakpassword |

  Scenario: Navigate to password reset page
    Given I am on the "account_login" page
    When I press "forgot_password_link"
    Then I should be on the "account_reset_password" page

  Scenario: Request a password reset with valid email address
    Given I am on the "account_reset_password" page
    When I fill in "id_email" with "user@ayrabo.com"
    And I press "password_reset_btn"
    Then I should see "You will receive an email with instructions for resetting your password in a few minutes."
    And "user@ayrabo.com" should receive an email with subject "Password Reset E-mail"
    When "user@ayrabo.com" follows the email link with subject "Password Reset E-mail"
    And I fill in "id_password1" with "mynewpassword"
    And I fill in "id_password2" with "mynewpassword"
    And I press "reset_password_btn"
    Then I should see "Your password has been updated."
    And I should see "to access your account."

  Scenario: Request a password reset with invalid email
    Given I am on the "account_reset_password" page
    When I fill in "id_email" with "myinvalidemail@ayrabo.com"
    And I press "password_reset_btn"
    Then I should see "The e-mail address is not assigned to any user account"
    And "myinvalidemail@ayrabo.com" should have 0 emails

  Scenario: Invalid password reset key
    Given I am on the "account_reset_password" page
    And I fill in "id_email" with "user@ayrabo.com"
    And I press "password_reset_btn"
    When I follow an invalid password reset link
    Then I should see "This password reset link is invalid. It may have expired or was already used."


  Scenario: Reset password while already logged in
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Coach, Referee"
    And I login with "user@ayrabo.com" and "myweakpassword"
    And I am on the "account_reset_password" page
    # Because the text below contains an anchor tag, selenium can't match all of the text
    Then I should see "You are already logged in, click"
    And I should see "to change your password"
