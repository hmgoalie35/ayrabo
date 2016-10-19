Feature: List season rosters
  As a site admin, team manager or team coach,
  I want to be able to view all season rosters for a team,
  So that I can see all season rosters and update them as needed

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team exists "Green Machine IceCats" in division "Midget Minor AA" in league "Long Island Amateur Hockey League" in sport "Ice Hockey"
    And I login with "user@example.com" and "myweakpassword"

  Scenario Outline: Can't view season roster list page w/o manager role
    Given "user@example.com" is completely registered for "Ice Hockey" with role "<role>"
    When I go to the "teams.Team" "" "team:create_season_roster" page with url kwargs "team_pk=pk"
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
    And I am on the "manager:home" page
    When I press "green-machine-icecats_manage_link"
    And I wait for "green-machine-icecats_create_season_roster_btn" to be visible
    And I press "green-machine-icecats_list_season_rosters_btn"
    Then I should be on the "teams.Team" "" "team:list_season_roster" page with url kwargs "team_pk=pk"

  Scenario: No season rosters created
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following season object exists
      | league                            | start_date | end_date   | teams                 |
      | Long Island Amateur Hockey League | 2016-09-14 | 2017-09-14 | Green Machine IceCats |
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the "teams.Team" "" "team:list_season_roster" page with url kwargs "team_pk=pk"
    Then I should see "Season Rosters for Green Machine IceCats"
    And I should see "A season roster has not been created for this team yet. You can create a season roster"

  Scenario: Season rosters are listed
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following season object exists
      | league                            | start_date | end_date   | teams                 |
      | Long Island Amateur Hockey League | 2016-09-14 | 2017-09-14 | Green Machine IceCats |
    And The following season rosters for "Ice Hockey" exist
      | season_start_date | season_end_date | team                  |
      | 2016-09-14        | 2017-09-14      | Green Machine IceCats |
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the "teams.Team" "" "team:list_season_roster" page with url kwargs "team_pk=pk"
    Then I should see "Season Rosters for Green Machine IceCats"
    And I should see "2016-2017 Season"
