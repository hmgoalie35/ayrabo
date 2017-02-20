Feature: Create season rosters
  As a site admin, team manager or team coach,
  I want to be able to create season rosters each season for my team,
  So that I can group, organize and keep track of players on a per season basis

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team objects exist
      | name                  | division             | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA      | Long Island Amateur Hockey League | Ice Hockey |
      | New York Yankees      | American League East | Major League Baseball             | Baseball   |
    And I login with "user@example.com" and "myweakpassword"

  Scenario Outline: Can't create season roster w/o manager role
    Given "user@example.com" is completely registered for "Ice Hockey" with role "<role>"
    When I go to the "teams.Team" "" "teams:season_rosters:create" page with url kwargs "team_pk=pk"
    Then I should be on the "home" page
    And I should see "You do not have permission to perform this action."

    Examples: Player, Coach, Referee roles
      | role    |
      | Player  |
      | Coach   |
      | Referee |

  Scenario: Create season roster for green machine icecats
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager objects exist
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the "managers:home" page
    When I press "green-machine-icecats_manage_link"
    And I wait for "green-machine-icecats_create_season_roster_btn" to be visible
    And I press "green-machine-icecats_create_season_roster_btn"
    Then I should be on the "teams.Team" "" "teams:season_rosters:create" page with url kwargs "team_pk=pk"
    And I should see "Create Season Roster for Green Machine IceCats"

  Scenario: Submit valid ice hockey create season roster form
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And The following season object exists
      | league                            | start_date | end_date   | teams                 |
      | Long Island Amateur Hockey League | 2016-09-14 | 2017-09-14 | Green Machine IceCats |
    And The following player objects exist
      | username_or_email | sport      | team                  |
      | test1@example.com | Ice Hockey | Green Machine IceCats |
      | test2@example.com | Ice Hockey | Green Machine IceCats |
      | test3@example.com | Ice Hockey | Green Machine IceCats |
      | test4@example.com | Ice Hockey | Green Machine IceCats |
      | test5@example.com | Ice Hockey | Green Machine IceCats |
    Given I am on the "teams.Team" "" "teams:season_rosters:create" page with url kwargs "team_pk=pk"
    And I select "Long Island Amateur Hockey League: 2016 - 2017 Season" from "id_season"
    And I select 5 players from "id_players"
    And I press "create_season_roster_btn"
    Then I should see "Season roster created for Green Machine IceCats."
    And I should be on the "home" page

  Scenario: Submit invalid ice hockey create season roster form
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And The following season object exists
      | league                            | start_date | end_date   | teams                 |
      | Long Island Amateur Hockey League | 2016-09-14 | 2017-09-14 | Green Machine IceCats |
    And The following player objects exist
      | username_or_email | sport      | team                  |
      | test1@example.com | Ice Hockey | Green Machine IceCats |
      | test2@example.com | Ice Hockey | Green Machine IceCats |
      | test3@example.com | Ice Hockey | Green Machine IceCats |
      | test4@example.com | Ice Hockey | Green Machine IceCats |
      | test5@example.com | Ice Hockey | Green Machine IceCats |
    Given I am on the "teams.Team" "" "teams:season_rosters:create" page with url kwargs "team_pk=pk"
    And I press "create_season_roster_btn"
    Then "This field is required." should show up 2 times
    And I should be on the "teams.Team" "" "teams:season_rosters:create" page with url kwargs "team_pk=pk"

      # TODO add in tests for BaseballSeasonRoster, etc.
