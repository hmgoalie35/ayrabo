Feature: List season rosters
  As a site admin, team manager or team coach,
  I want to be able to view all season rosters for a team,
  So that I can see all season rosters and update them as needed

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@example.com" and "myweakpassword"

  Scenario Outline: Can't view season roster list page w/o manager role
    Given "user@example.com" is completely registered for "Ice Hockey" with role "<role>"
    When I go to the "teams.Team" "" "teams:season_rosters:create" page with url kwargs "team_pk=pk"
    Then I should be on the "home" page
    And I should see "You do not have permission to perform this action."

    Examples: Player, Coach, Referee roles
      | role    |
      | Player  |
      | Coach   |
      | Referee |

  Scenario: Navigate to season roster list page
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I press "manager_tab"
    And I press "actions-dropdown-manager-green-machine-icecats"
    And I press "list_season_rosters_btn_green-machine-icecats"
    Then I should be on the "teams.Team" "" "teams:season_rosters:list" page with url kwargs "team_pk=pk"

  Scenario: No season rosters created
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following season object exists
      | league                            | teams                 |
      | Long Island Amateur Hockey League | Green Machine IceCats |
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the "teams.Team" "" "teams:season_rosters:list" page with url kwargs "team_pk=pk"
    Then I should see "Season Rosters for Green Machine IceCats"
    And I should see "A season roster has not been created for this team yet."

  Scenario: Season rosters are listed
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following season object exists
      | league                            | start_date | end_date   | teams                 |
      | Long Island Amateur Hockey League | 2016-09-14 | 2017-09-14 | Green Machine IceCats |
      | Long Island Amateur Hockey League | 2017-09-14 | 2018-09-14 | Green Machine IceCats |
    And The following season rosters for "Ice Hockey" exist
      | name       | season_start_date | season_end_date | team                  | created_by       |
      | Main Squad | 2016-09-14        | 2017-09-14      | Green Machine IceCats | user@example.com |
      | Main Squad | 2017-09-14        | 2018-09-14      | Green Machine IceCats | user@example.com |
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the "teams.Team" "" "teams:season_rosters:list" page with url kwargs "team_pk=pk"
    Then I should see "Season Rosters for Green Machine IceCats"
    And I should see "2016-2017 Season"
    And I should see "Main Squad - 2017-2018 Season"
    And I should see "Created By:"
    And "You" should show up 2 times
