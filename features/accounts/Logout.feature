Feature: Logout

  Scenario: Logout
    Given The following users exist
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And I am on the "account_login" page
    And I fill in "id_login" with "user@ayrabo.com"
    And I fill in "id_password" with "myweakpassword"
    And I press "login_main"

  Scenario: Logout (not logged in)
    When I press "account_menu"
    And I press "logout_btn_acct_menu"
    And I should be logged out
    And "logout_btn_acct_menu" should not exist on the page
