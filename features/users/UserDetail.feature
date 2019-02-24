Feature: User profile
  As a user,
  I want to be able to view another user's profile

  Background: Users exist
    Given The following confirmed user account exists
      | id | first_name | last_name | email              | password       | create_userprofile |
      | 1  | John       | Doe       | user@ayrabo.com    | myweakpassword | false              |
      |    | Michael    | Scott     | michael@ayrabo.com | myweakpassword | true               |
    And The following userprofile exists for "user@ayrabo.com"
      | gender | birthday   | height | weight | timezone   |
      | male   | 1996-02-12 | 5' 7"  | 150    | US/Eastern |
    And The following waffle switch exists
      | name                | active |
      | sport_registrations | True   |
    And I login with "michael@ayrabo.com" and "myweakpassword"

  Scenario: View another user's profile information
    Given I am on the "users:detail" page with kwargs "pk=1"
    Then I should see "John Doe"
    And I should see "Gender"
    And I should see "Male"
    # Not worth the headache to check the value for age here
    And I should see "Age"
    And I should see "Birthday"
    And I should see "Feb. 12, 1996"
    And I should see "Height"
    And I should see "5' 7""
    And I should see "Weight"
    And I should see "150"

  Scenario: View another user's sports information
    Given The following sport registrations exist
      | username_or_email | sport      | roles                        | complete |
      | user@ayrabo.com   | Ice Hockey | Coach, Referee               | true     |
      | user@ayrabo.com   | Baseball   | Player, Manager, Scorekeeper | true     |
    And I am on the "users:detail" page with kwargs "pk=1"
    And I press "tab-item-sports"
    And I press "list-item-ice-hockey"
    Then I should see "At a glance"
    And I should see "Coach"
    And I should see "Manager"
    And I should see "Player"
    And I should see "Referee"
    And I should see "Scorekeeper"
    And "register_for_sport_btn" should not exist on the page

  Scenario: View another user's sports information, empty state
    Given I am on the "users:detail" page with kwargs "pk=1"
    And I press "tab-item-sports"
    Then I should see "John Doe is not registered for any sports at this time."
