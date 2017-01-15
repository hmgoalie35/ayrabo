Feature: View and revoke api token
  As a user/developer,
  So that I can access the site's api
  I want to be able to see my api token and revoke it if need be.

  Background: User account and token exist
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@example.com" is completely registered for "Ice Hockey" with role "Coach"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: View api token
    Given "user@example.com" has "cb9667fb74360e47d5f9ff266f1389b40fbc46e0" as an api token
    And I go to the "account_home" page
    When I press "show_token_link" which opens "token_modal"
    Then I should see "You must keep this token secret, otherwise anybody with the token can impersonate you."
    And I should see "cb9667fb74360e47d5f9ff266f1389b40fbc46e0"

  Scenario: Revoke api token
    Given "user@example.com" has "cb9667fb74360e47d5f9ff266f1389b40fbc46e0" as an api token
    And I go to the "account_home" page
    And I press "show_token_link" which opens "token_modal"
    And I press "revoke_api_token_btn"
    And I wait for any ajax calls to finish
    Then I should be on the "account_home" page
    And I should not see "API Token"

  Scenario: no api token
    Given I am on the "account_home" page
    Then I should not see "API Token"

