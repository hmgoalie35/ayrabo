Feature: Team season rosters

  Background:
    Given The following users exist
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And The following seasons exist
      | id | league                            | start_date | end_date | teams                 |
      | 1  | Long Island Amateur Hockey League | today      | 1y       | Green Machine IceCats |
      | 2  | Long Island Amateur Hockey League | -1y        | -5d      | Green Machine IceCats |
      | 3  | Long Island Amateur Hockey League | 1y         | 2y       | Green Machine IceCats |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to season roster list page from dashboard
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "manager-tab"
    And I press "actions-dropdown-manager-green-machine-icecats"
    And I press "list_season_rosters_btn_green-machine-icecats"
    Then I should be on the "teams:season_rosters:list" page with kwargs "team_pk=1"

  Scenario: Informative text shown to user
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And I am on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    Then I should see "Green Machine IceCats - Midget Minor AA"
    And I should see "Long Island Amateur Hockey League"
    And I should see season "today" "1y"
    And "create-season-roster-btn" should be visible

  Scenario: No season rosters
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And I am on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    Then I should see "There are no season rosters for Green Machine IceCats at this time."

  Scenario: Season rosters exist
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following season rosters for "Ice Hockey" exist
      | id | name    | season_id | team                  | created_by      |
      | 1  | Squad A | 1         | Green Machine IceCats | user@ayrabo.com |
      | 2  | Squad B | 1         | Green Machine IceCats | user@ayrabo.com |
    And I am on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    Then I should see "Squad A"
    And I should see "Squad B"
    And I should see "John Doe"
    And I should see "(you)"
    And I press "view-players-1-link" which opens "1-modal"
    Then "1-modal" should be visible

  Scenario: Not team manager
    Given I am on the "teams:season_rosters:list" page with kwargs "team_pk=2"
    Then I should see "Your account does not currently have access to this functionality."
    And I should see "Please contact us at "

  Scenario: Navigate to team season rosters page for past season
    Given I am on the "teams:schedule" page with kwargs "team_pk=1"
    And I press "tab-item-seasons"
    And I press "season-2"
    And I press "tab-item-season-rosters"
    Then I should be on the "teams:seasons:season_rosters-list" page with kwargs "team_pk=1, season_pk=2"

  Scenario: View past season
    Given I am on the "teams:seasons:season_rosters-list" page with kwargs "team_pk=1, season_pk=2"
    Then I should see "This season has been archived."
    And I should see "The current season's rosters are available"
    And "create-season-roster-btn" should exist on the page
    And I should see season "-1y" "-5d"
    And I should see "There are no season rosters for Green Machine IceCats at this time."

  Scenario: View past season, press season rosters nav tab again
    Given I am on the "teams:seasons:season_rosters-list" page with kwargs "team_pk=1, season_pk=2"
    And I press "tab-item-season-rosters"
    Then I should be on the "teams:seasons:season_rosters-list" page with kwargs "team_pk=1, season_pk=2"

  Scenario: Navigate to team season rosters page for future season
    Given I am on the "teams:schedule" page with kwargs "team_pk=1"
    And I press "tab-item-seasons"
    And I press "season-3"
    And I press "tab-item-season-rosters"
    Then I should be on the "teams:seasons:season_rosters-list" page with kwargs "team_pk=1, season_pk=3"

  Scenario: View future season
    Given I am on the "teams:seasons:season_rosters-list" page with kwargs "team_pk=1, season_pk=3"
    Then I should see "This season has not started yet."
    And I should see "The current season's rosters are available"
    And "create-season-roster-btn" should exist on the page
    And I should see season "1y" "2y"
    And I should see "There are no season rosters for Green Machine IceCats at this time."

  Scenario: View future season, press season rosters nav tab again
    Given I am on the "teams:seasons:season_rosters-list" page with kwargs "team_pk=1, season_pk=3"
    And I press "tab-item-season-rosters"
    Then I should be on the "teams:seasons:season_rosters-list" page with kwargs "team_pk=1, season_pk=3"
