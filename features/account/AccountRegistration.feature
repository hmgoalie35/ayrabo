Feature: Register for an account
  As a potential user of the site
  So that I can register for an account and have my data saved
  I want to be able to register for an account

  Scenario: Register for an account with valid info
    Given I am on the "account_register" page
    When I fill in "id_first_name" with "John"
    And I fill in "id_last_name" with "Doe"
    And I fill in "id_username" with "islanders1980"
    And I fill in "id_email" with "user@example.com"
    And I fill in "id_password1" with "myweakpassword"
    And I fill in "id_password2" with "myweakpassword"
    And I press "id_submit"
    Then I should be on the "account_email_verification_sent" page
    And I should see "Verify Your E-mail Address"
    And I should see "An email with a confirmation link has been sent to your email address. Please follow the link to activate your account."
    # Note this does not test confirming the account, that is done below.
    And A user account should exist for "islanders1980"

  Scenario: Confirm email address with a valid link
    Given I have an unconfirmed account
    When I confirm my account via "email"
    Then I should see "You have confirmed user@example.com"
    And I should be on the "account_login" page

  Scenario: Attempt to confirm email address with an invalid link
    Given I have an unconfirmed account
    When I follow an invalid email link
    Then I should see "This confirmation link has expired or is invalid"
    And I should see "request a new confirmation link"


  Scenario: Register for an account with no info
    Given I am on the "account_register" page
    When I press "id_submit"
    Then I should be on the "account_register" page
    And "This field is required." should show up 6 times
