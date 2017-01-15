Feature: Update season roster
  As a site admin, team manager or team coach,
  I want to be able to update a season roster
  So that I can keep the season roster up to date

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following season object exists
      | league                            | start_date | end_date   | teams                 |
      | Long Island Amateur Hockey League | 2016-09-14 | 2017-09-14 | Green Machine IceCats |
    And The following season rosters for "Ice Hockey" exist
      | season_start_date | season_end_date | team                  | players           |
      | 2016-09-14        | 2017-09-14      | Green Machine IceCats | John Doe, Lee Doe |
    And I login with "user@example.com" and "myweakpassword"

  Scenario Outline: Can't view season roster update page w/o manager role
    Given "user@example.com" is completely registered for "Ice Hockey" with role "<role>"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    When I go to the absolute url page for "seasons.HockeySeasonRoster" and "team__name=Green Machine IceCats"
    Then I should be on the "home" page
    And I should see "You do not have permission to perform this action."

    Examples: Player, Coach, Referee roles
      | role    |
      | Player  |
      | Coach   |
      | Referee |

  Scenario: Navigate to season roster update page
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the "teams.Team" "" "team:list_season_roster" page with url kwargs "team_pk=pk"
    When I press "update_link"
    Then I should be on the absolute url page for "seasons.HockeySeasonRoster" and "team__name=Green Machine IceCats"

  Scenario: Submit unchanged form
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the absolute url page for "seasons.HockeySeasonRoster" and "team__name=Green Machine IceCats"
    When I press "update_season_roster_btn"
    Then I should be on the "teams.Team" "" "team:list_season_roster" page with url kwargs "team_pk=pk"
    And I should not see "Season roster for Green Machine IceCats successfully updated."

  Scenario: Submit changed form
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the absolute url page for "seasons.HockeySeasonRoster" and "team__name=Green Machine IceCats"
    When I press "id_default"
    And I press "update_season_roster_btn"
    Then I should be on the "teams.Team" "" "team:list_season_roster" page with url kwargs "team_pk=pk"
    And I should see "Season roster for Green Machine IceCats successfully updated."

  Scenario: Invalid form
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the absolute url page for "seasons.HockeySeasonRoster" and "team__name=Green Machine IceCats"
    And I deselect "John Doe" from "id_players"
    And I deselect "Lee Doe" from "id_players"
    And I press "update_season_roster_btn"
    Then I should be on the absolute url page for "seasons.HockeySeasonRoster" and "team__name=Green Machine IceCats"
    And "This field is required." should show up 1 time
