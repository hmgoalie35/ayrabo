Feature: Create season rosters
  As a site admin, team manager or team coach,
  I want to be able to create season rosters each season for my team,
  So that I can group, organize and keep track of players on a per season basis

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team objects exist
      | id | name                  | division             | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA      | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | New York Yankees      | American League East | Major League Baseball             | Baseball   |
    And The following seasons exist
      | id | league                            | start_date | end_date | teams                 |
      | 1  | Long Island Amateur Hockey League | today      | 1y       | Green Machine IceCats |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to season roster create page from dashboard
    Given The following sport registration exists
      | id | username_or_email | sport      | roles   | complete |
      | 20 | user@ayrabo.com   | Ice Hockey | Manager | true     |
    And The following manager objects exist
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "manager-tab"
    And I press "actions-dropdown-manager-green-machine-icecats"
    And I press "create_season_roster_btn_green-machine-icecats"
    Then I should be on the "teams:season_rosters:create" page with kwargs "team_pk=1"
    And I should see "Create Season Roster for Green Machine IceCats"

  Scenario: Navigate to season roster create page from season roster list page
    Given The following sport registration exists
      | id | username_or_email | sport      | roles   | complete |
      | 20 | user@ayrabo.com   | Ice Hockey | Manager | true     |
    And The following manager objects exist
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    And I press "create-season-roster-btn"
    Then I should be on the "teams:season_rosters:create" page with kwargs "team_pk=1"

  Scenario: Informative text displayed to user
    Given The following sport registration exists
      | id | username_or_email | sport      | roles   | complete |
      | 20 | user@ayrabo.com   | Ice Hockey | Manager | true     |
    And The following manager objects exist
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "teams:season_rosters:create" page with kwargs "team_pk=1"
    Then I should see "Green Machine IceCats - Midget Minor AA"
    And I should see "Long Island Amateur Hockey League"
    And I should see "Create Season Roster"

  Scenario: Submit valid ice hockey form
    Given The following sport registration exists
      | id | username_or_email | sport      | roles   | complete |
      | 25 | user@ayrabo.com   | Ice Hockey | Manager | true     |
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And The following player objects exist
      | username_or_email | sport      | team                  |
      | test1@ayrabo.com  | Ice Hockey | Green Machine IceCats |
      | test2@ayrabo.com  | Ice Hockey | Green Machine IceCats |
      | test3@ayrabo.com  | Ice Hockey | Green Machine IceCats |
      | test4@ayrabo.com  | Ice Hockey | Green Machine IceCats |
      | test5@ayrabo.com  | Ice Hockey | Green Machine IceCats |
    Given I am on the "teams:season_rosters:create" page with kwargs "team_pk=1"
    And I fill in "id_name" with "Main Squad"
    And I select "1" from "id_season"
    And I select 5 players from "id_players"
    And I press "create_season_roster_btn"
    Then I should see "Your season roster has been created."
    And I should be on the "teams:season_rosters:list" page with kwargs "team_pk=1"

  Scenario: Submit invalid ice hockey form
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And The following player objects exist
      | username_or_email | sport      | team                  |
      | test1@ayrabo.com  | Ice Hockey | Green Machine IceCats |
      | test2@ayrabo.com  | Ice Hockey | Green Machine IceCats |
      | test3@ayrabo.com  | Ice Hockey | Green Machine IceCats |
      | test4@ayrabo.com  | Ice Hockey | Green Machine IceCats |
      | test5@ayrabo.com  | Ice Hockey | Green Machine IceCats |
    And The following season rosters for "Ice Hockey" exist
      | id | name          | season_id | team                  | default |
      |    | Default Squad | 1         | Green Machine IceCats | True    |
    And I am on the "teams:season_rosters:create" page with kwargs "team_pk=1"
    When I fill in "id_name" with "Main Squad"
    And I select "1" from "id_season"
    And I select 5 players from "id_players"
    And I press "id_default"
    And I press "create_season_roster_btn"
    Then I should see "A default season roster for this team and season already exists."
    And I should be on the "teams:season_rosters:create" page with kwargs "team_pk=1"
