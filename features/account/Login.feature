Feature: Login to my existing account
  As a user of the site
  So that I can use the site
  I want to be able to login to my account

  Background: Not logged in
    Given I am not logged in

  Scenario: Login successfully via navbar
    Given I have a confirmed account
    When I login with valid credentials via "navbar"
    Then I should be logged in

  Scenario: Login successfully via login page
    Given I have a confirmed account
    When I login with valid credentials via "login_page"
    Then I should be logged in

  Scenario: Login with invalid email
    Given I have a confirmed account
    When I login with an invalid "email"
    Then I should not be logged in
    And I should see "The login and/or password you specified are not correct."

  Scenario: Login with invalid password
    Given I have a confirmed account
    When I login with an invalid "password"
    Then I should not be logged in
    And I should see "The login and/or password you specified are not correct."

  Scenario: Login with unconfirmed account
    Given I have an unconfirmed account
    When I login with valid credentials
    Then I should not be logged in
    And I should be on the "account_email_verification_sent" page
    And I should see "Verify Your E-mail Address"
    And I should see "An email with a confirmation link has been sent to your email address. Please follow the link to activate your account."
