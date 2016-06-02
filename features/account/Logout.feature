Feature: Logout
  As a user of the site
  So that I can prevent my account from unauthorized use
  I want to be able to logout of my account

  Scenario: Logout after logging in
    Given The following confirmed user accounts exist
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And I login with "user@example.com" and "myweakpassword"
    And I am on the "home" page
    When I press "account_menu"
    And I press "logout_btn_acct_menu"
    And I press "logout_btn"
    Then I should not be logged in
