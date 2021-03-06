Feature: Update season roster
  As a site admin, team manager or team coach,
  I want to be able to update a season roster
  So that I can keep the season roster up to date

  Background: User exists
    Given The following users exist
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following seasons exist
      | id | league                            | teams                 |
      | 1  | Long Island Amateur Hockey League | Green Machine IceCats |
    And The following season rosters for "Ice Hockey" exist
      | id | name          | season_id | team                  | default |
      | 1  | Main Squad    | 1         | Green Machine IceCats | False   |
      |    | Default Squad | 1         | Green Machine IceCats | True    |
    And The following "Ice Hockey" players have been added to season roster "1"
      | first_name | last_name | jersey_number | position | team_id |
      | John       | Doe       | 1             | C        | 1       |
      | Lee        | Doe       | 2             | LW       | 1       |

    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to season roster update page
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    When I press "actions-dropdown-1"
    And I press "update-season-roster-1-link"
    Then I should be on the "teams:season_rosters:update" page with kwargs "team_pk=1, pk=1"
    And I should see "Green Machine IceCats - Midget Minor AA"
    And I should see "Long Island Amateur Hockey League"
    And I should see "Update Season Roster"

  Scenario: Submit valid ice hockey form
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "teams:season_rosters:update" page with kwargs "team_pk=1, pk=1"
    And I fill in "id_name" with "Bash Brothers"
    And I press "update_season_roster_btn"
    Then I should be on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    And I should see "Your season roster has been updated."

  Scenario: Submit invalid ice hockey form
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "teams:season_rosters:update" page with kwargs "team_pk=1, pk=1"
    And I press "id_default"
    And I press "update_season_roster_btn"
    Then I should see "A default season roster for this team and season already exists."
    And I should be on the "teams:season_rosters:update" page with kwargs "team_pk=1, pk=1"

    # Am omitting a test for "Attempt to add another default season roster for a team/season" because this is handled
    # in the view tests. Not really worth it to duplicate the test here also. The test in CreateSeasonRoster is being
    # kept solely for reference

  Scenario: Form disabled for past seasons
    Given The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And The following seasons exist
      | id | league                            | teams                 | start_date | end_date |
      | 2  | Long Island Amateur Hockey League | Green Machine IceCats | -1y        | -5d      |
    And The following season rosters for "Ice Hockey" exist
      | id | name          | season_id | team                  |
      | 2  | Bash Brothers | 2         | Green Machine IceCats |
    And I am on the "teams:season_rosters:update" page with kwargs "team_pk=1, pk=2"
    Then I should see "Updates to this season roster are no longer permitted."
    And "id_name" should be disabled
    And "id_season" should be disabled
    And "id_default" should be disabled
    And "id_players" should be disabled
    And "update_season_roster_btn" should not exist on the page
