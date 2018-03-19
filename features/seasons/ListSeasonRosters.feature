Feature: List season rosters
  As a site admin, team manager or team coach,
  I want to be able to view all season rosters for a team,
  So that I can see all season rosters and update them as needed

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to season roster list page
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    And I press "manager_tab"
    And I press "actions-dropdown-manager-green-machine-icecats"
    And I press "list_season_rosters_btn_green-machine-icecats"
    Then I should be on the "teams:season_rosters:list" page with kwargs "team_pk=1"

  Scenario: Informative text shown to user
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following season object exists
      | league                            | teams                 |
      | Long Island Amateur Hockey League | Green Machine IceCats |
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    Then I should see "Season Rosters for Green Machine IceCats"
    And I should see "Midget Minor AA - LIAHL"

  Scenario: No season rosters
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following season object exists
      | league                            | teams                 |
      | Long Island Amateur Hockey League | Green Machine IceCats |
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    Then I should see "There are no season rosters for this team."
    And "create-season-roster-btn-empty-state" should be visible
    And "create-season-roster-btn" should not exist on the page

  Scenario: Season rosters are listed
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following season object exists
      | league                            | start_date | end_date   | teams                 |
      | Long Island Amateur Hockey League | 2016-09-14 | 2017-09-14 | Green Machine IceCats |
      | Long Island Amateur Hockey League | 2017-09-14 | 2018-09-14 | Green Machine IceCats |
    And The following season rosters for "Ice Hockey" exist
      | name    | season_start_date | season_end_date | team                  | created_by      |
      | Squad A | 2016-09-14        | 2017-09-14      | Green Machine IceCats | user@ayrabo.com |
      | Squad B | 2017-09-14        | 2018-09-14      | Green Machine IceCats | user@ayrabo.com |
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the "teams:season_rosters:list" page with kwargs "team_pk=1"
    Then I should see "Squad A"
    And I should see "Squad B"
    And I should see "2016-2017 Season"
    And I should see "2017-2018 Season"
    And I should see "John Doe (you)"
    And "View" should show up 2 times
