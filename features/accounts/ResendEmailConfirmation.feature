Feature: Resend account confirmation
  As a user
  So that I can confirm and login to my account
  I want to be able to confirm my account in the event I didn't receive an email or the confirmation email link expired

  Background: Users exist
    Given The following unconfirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And An empty inbox

  Scenario: Navigate to resend confirmation page
    Given I am on the "account_login" page
    When I press "didnt_receive_confirmation_email"
    Then I should be on the "/account/confirm-email/new-confirmation-link/" page
    And I should not see "This confirmation link is invalid or has expired."
    And I should not see "Enter your email below to request a new link."

  Scenario: Request a new email confirmation with valid email
    Given I am on the "/account/confirm-email/new-confirmation-link/" page
    When I fill in "new_email_confirmation" with "user@ayrabo.com"
    And I press "request_new_confirmation_email"
    Then I should see "A new confirmation email has been sent to user@ayrabo.com."
    And "user@ayrabo.com" should receive an email with subject "Please Confirm Your E-mail Address"
    And "user@ayrabo.com" should have 1 email

  Scenario: Request a new email confirmation with invalid email
    Given I am on the "/account/confirm-email/new-confirmation-link/" page
    When I fill in "new_email_confirmation" with "myinvalidemail@ayrabo.com"
    And I press "request_new_confirmation_email"
    Then I should see "myinvalidemail@ayrabo.com is not a valid e-mail address or has already been confirmed."
    And "user@ayrabo.com" should have no emails


  Scenario: Request email confirmation when already logged in
    Given The following confirmed user account exists
      | first_name | last_name | email              | password       |
      | Jane       | Doe       | testing@ayrabo.com | myweakpassword |
    And "testing@ayrabo.com" is completely registered for "Ice Hockey" with roles "Coach, Referee"
    And I login with "testing@ayrabo.com" and "myweakpassword"
    When I go to the "/account/confirm-email/new-confirmation-link/" page
    Then I should see "You have already confirmed your e-mail address"
