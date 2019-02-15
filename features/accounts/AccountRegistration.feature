Feature: Register for an account
  As a potential user of the site
  So that I can register for an account and have my data saved
  I want to be able to register for an account

  Scenario: Submit valid form
    Given I am on the "account_register" page
    When I fill in "id_first_name" with "John"
    And I fill in "id_last_name" with "Doe"
    And I fill in "id_email" with "user@ayrabo.com"
    And I fill in "id_password1" with "myweakpassword"
    And I fill in "id_password2" with "myweakpassword"
    And I press "id_submit"
    Then I should be on the "account_email_verification_sent" page
    And I should see "Verify Your E-mail Address"
    And I should see "An email with a confirmation link has been sent to your email address. Please follow the"
    # Note this does not test confirming the account, that is done below.
    And A user account should exist for "user@ayrabo.com"

  Scenario: Submit invalid form
    Given I am on the "account_register" page
    And I fill in "id_first_name" with "Michael"
    And I fill in "id_last_name" with "Scott"
    And I fill in "id_email" with "test@ayrabo.com"
    And I fill in "id_password1" with "myweakpassword"
    And I fill in "id_password2" with "helloworld"
    When I press "id_submit"
    Then I should see "You must type the same password each time."
    And I should be on the "account_register" page

  Scenario: Confirm email address with a valid link
    Given The following unconfirmed user accounts exist
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    When I confirm "user@ayrabo.com" via "email_link"
    Then I should be on the "account_login" page
    And I should see "You have confirmed user@ayrabo.com"

  Scenario: Attempt to confirm email address with an invalid link
    Given The following unconfirmed user accounts exist
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    When I follow an invalid email link
    Then I should see "This confirmation link is invalid or has expired."
    And I should see "Enter your email below to request a new link."
