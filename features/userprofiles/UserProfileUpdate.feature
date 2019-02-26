Feature: Edit information associated with my account
  As a user of the site
  So that I can keep my information up to date
  I want to be able to update my account

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       | create_userprofile |
      | John       | Doe       | user@ayrabo.com | myweakpassword | false              |
    And The following userprofile exists for "user@ayrabo.com"
      | gender | birthday   |
      | male   | 1996-02-12 |
    And The following sport registrations exist
      | username_or_email | sport      | roles                        | complete |
      | user@ayrabo.com   | Ice Hockey | Coach, Referee               | true     |
      | user@ayrabo.com   | Baseball   | Player, Manager, Scorekeeper | true     |
    And The following waffle switch exists
      | name                | active |
      | sport_registrations | True   |
    And I login with "user@ayrabo.com" and "myweakpassword"

  # My Account tab tests
  Scenario: Navigate to user profile update page via navbar
    Given I am on the "home" page
    When I press "account_menu"
    And I press "edit_account_link"
    Then I should be on the "account_home" page
    And I should see "John Doe"
    And I should see "user@ayrabo.com"
    And I should see "Male"
    And I should see "Feb. 12, 1996"

  Scenario: Submit unchanged form
    Given I am on the "account_home" page
    When I press "update_userprofile_btn"
    Then I should not see "Your account has been updated."
    And I should be on the "account_home" page

  Scenario: Submit changed form
    Given I am on the "account_home" page
    When I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "120"
    And I press "update_userprofile_btn"
    Then I should see "Your account has been updated."
    And I should be on the "account_home" page

  # My Sports tab tests
  Scenario: View my sports
    Given I am on the "account_home" page
    When I press "my-sports-tab"
    Then "my_sport_registrations" should be visible
    And I should see "Ice Hockey"
    And I should see "Baseball"

  Scenario: Navigate to sports register page
    Given The following sport exists "Basketball"
    When I go to the "account_home" page
    And I press "my-sports-tab"
    And I press "register_for_sport_btn"
    Then I should be on the "sports:register" page

  Scenario: Navigate to sports register page, no more available sports
    Given I am on the "account_home" page
    When I press "my-sports-tab"
    And I press "register_for_sport_btn"
    Then I should see "You have already registered for all available sports."
    And I should be on the "account_home" page

  Scenario: Expand sport list item
    Given I am on the "account_home" page
    When I press "my-sports-tab"
    And I press "list-item-ice-hockey"
    Then "ice-hockey" should be visible
    And I should see "Player"
    And I should see "Coach"
    And I should see "Referee"
    And I should see "Manager"
