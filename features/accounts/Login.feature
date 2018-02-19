Feature: Login to my existing account
  As a user of the site
  So that I can use the site
  I want to be able to login to my account

  Background: Not logged in
    Given I am on the "home" page
    And I am not logged in
    And The following confirmed user accounts exist
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following unconfirmed user accounts exist
      | first_name | last_name | email        | password       |
      | Jane       | Doe       | jane@doe.com | myweakpassword |
    And The following sport exists "Ice Hockey"

  Scenario: Login successfully via navbar
    Given I login with "user@ayrabo.com" and "myweakpassword" via "navbar"
    Then I should be logged in

  Scenario: Login successfully via login page
    Given I login with "user@ayrabo.com" and "myweakpassword" via "login_page"
    Then I should be logged in

  Scenario: Login with invalid email
    Given I login with "myincorrectemail@testing.com" and "myweakpassword" via "login_page"
    Then I should not be logged in
    And I should see "The e-mail address and/or password you specified are not correct."

  Scenario: Login with invalid password
    When I login with "user@ayrabo.com" and "myincorrectpassword" via "login_page"
    Then I should not be logged in
    And I should see "The e-mail address and/or password you specified are not correct."

  Scenario: Login with unconfirmed account
    Given I login with "jane@doe.com" and "myweakpassword" via "login_page"
    Then I should not be logged in
    And I should be on the "account_email_verification_sent" page
    And I should see "Verify Your E-mail Address"
    And I should see "An email with a confirmation link has been sent to your email address. Please follow the"
