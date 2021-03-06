Feature: Team players

  Background:
    Given The following users exist
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following league objects exist
      | name                              | sport      |
      | Long Island Amateur Hockey League | Ice Hockey |
    And The following team object exists
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following seasons exist
      | id | league                            | teams                                   | start_date | end_date |
      | 1  | Long Island Amateur Hockey League | Long Island Edge                        | -1y        | -2y      |
      | 2  | Long Island Amateur Hockey League | Green Machine IceCats, Long Island Edge | today      | 1y       |
      | 3  | Long Island Amateur Hockey League | Green Machine IceCats                   | 1y         | 2y       |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to players page
    Given I am on the "teams:schedule" page with kwargs "team_pk=1"
    And I press "tab-item-players"
    Then I should be on the "teams:players" page with kwargs "team_pk=1"

  Scenario: Informative text displayed to user
    Given I am on the "teams:players" page with kwargs "team_pk=1"
    Then I should see "Green Machine IceCats - Midget Minor AA"
    And I should see "Long Island Amateur Hockey League"
    And I should see "All Players"

  Scenario: No players
    Given I am on the "teams:players" page with kwargs "team_pk=1"
    Then I should see "There are no players for Green Machine IceCats at this time."
    And I should see "Jersey Number"
    And I should see "Name"
    And I should not see "Position"

  Scenario: Players exist
    Given The following users exist
      | email            | first_name | last_name |
      | user1@ayrabo.com | Michael    | Scott     |
      | user2@ayrabo.com | Dwight     | Schrute   |
    And The following player objects exist
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user1@ayrabo.com  | Ice Hockey | Green Machine IceCats | 11            | C        | Right      |
      | user2@ayrabo.com  | Ice Hockey | Green Machine IceCats | 21            | G        | Left       |
    And I am on the "teams:players" page with kwargs "team_pk=1"
    Then I should see "11"
    And I should see "Michael Scott"
    And I should see "Center"
    And I should see "Right"
    And I should see "21"
    And I should see "Dwight Schrute"
    And I should see "Goaltender"
    And I should see "Left"

  Scenario: View team detail players page for past season
    Given I am on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=1"
    And I press "tab-item-players"
    Then I should be on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=1"
    And I should see "This functionality is not currently available for past seasons."

  Scenario: View team detail players page for future season
    Given I am on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=3"
    And I press "tab-item-players"
    Then I should be on the "teams:seasons:schedule" page with kwargs "team_pk=1, season_pk=3"
    And I should see "This functionality is not currently available for future seasons."
