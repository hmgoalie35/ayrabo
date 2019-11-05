Feature: Login

  Background:
    Given I am on the "home" page
    And I am logged out
    And The following users exist
      | first_name | last_name | email           | username        | password       |
      | John       | Doe       | user@ayrabo.com | user@ayrabo.com | myweakpassword |
    And I am on the "account_login" page

  Scenario: Login with valid email
    When I fill in "id_login" with "user@ayrabo.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "login_main"
    Then I should be logged in

  Scenario: Login with invalid email
    When I fill in "id_login" with "testing@ayrabo.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "login_main"
    Then I should be logged out
    And I should see "The e-mail address and/or password you specified are not correct."

#  Uncomment when switch to usernames
#  Scenario: Login with valid username
#    When I fill in "id_login" with "theboss"
#    And I fill in "id_password" with "myweakpassword"
#    And I press "login_main"
#    Then I should be logged in

#  TODO Form input is of type email so the error doesn't happen bcz form doesn't get submitted
#  Scenario: Login with invalid username
#    When I fill in "id_login" with "invalidusername"
#    And I fill in "id_password" with "myweakpassword"
#    And I press "login_main"
#    Then I should be logged out
#    And I should see "The e-mail address and/or password you specified are not correct."

  Scenario: Login with invalid password
    When I fill in "id_login" with "user@ayrabo.com"
    And I fill in "id_password" with "myincorrectpassword"
    And I press "login_main"
    Then I should be logged out
    And I should see "The e-mail address and/or password you specified are not correct."

  Scenario: Login with unconfirmed email
    Given The following users exist
      | first_name | last_name | email                  | password       | account_type |
      | Jane       | Doe       | unconfirmed@ayrabo.com | myweakpassword | unconfirmed  |
    When I fill in "id_login" with "unconfirmed@ayrabo.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "login_main"
    Then I should be logged out
    And I should be on the "account_email_verification_sent" page
    And I should see "Verify Your E-mail Address"
    And I should see "An email with a confirmation link has been sent to your email address. Please follow the"

  Scenario: Login with inactive account
    Given The following users exist
      | first_name | last_name | username          | email             | is_active | password       |
      | Michael    | Scarn     | mscarn@ayrabo.com | mscarn@ayrabo.com | false     | myweakpassword |
    When I fill in "id_login" with "mscarn@ayrabo.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "login_main"
    Then I should be on the "account_inactive" page
    And I should see "Account Inactive"
    And I should see "Please contact us at"
