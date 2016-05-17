Feature: Logout
  As a user of the site
  So that I can prevent my account from unauthorized use
  I want to be able to logout of my account

  Scenario: Logout after logging in
    Given I am logged in
    And I am on the "home" page
    When I press "account_menu"
    And I press "logout_btn_acct_menu"
    # xpath seems to work because it is direct access to the element, which is technically not visible (and why id is failing)
    # could add in a webdriver wait
    And I press "//*[@id="logout_btn_modal"]"
    Then I should not be logged in
