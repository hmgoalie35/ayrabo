Feature: List games for a team
  As a user, I want to be able to view all games for a team
  So that I can see what their schedule is like

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@ayrabo.com  | myweakpassword |
      | Jane       | Doe       | user1@ayrabo.com | myweakpassword |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 3  | Aviator Gulls         | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And "user1@ayrabo.com" is completely registered for "Ice Hockey" with role "Player"
    And The following manager objects exist
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And The following generic choice objects exist
      | content_type | short_value | long_value | type             |
      | sports.Sport | exhibition  | Exhibition | game_type        |
      | sports.Sport | league      | League     | game_type        |
      | sports.Sport | 2           | 2          | game_point_value |
    And The following location object exists
      | name    |
      | Iceland |
    And The following season object exists
      | id | league                            | start_date | end_date   | teams                 |
      | 1  | Long Island Amateur Hockey League | 2017-09-14 | 2018-09-14 | Green Machine IceCats |
    And I login with "user@ayrabo.com" and "myweakpassword"

#  Scenario: Navigate to hockey game list page as manager
#    Given I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
#    And I press "manager_tab"
#    And I press "actions-dropdown-manager-green-machine-icecats"
#    And I press "list_games_manager_btn_green-machine-icecats"
#    Then I should be on the "teams:games:list" page with kwargs "team_pk=1"
#
#  Scenario: Navigate to hockey game list page as player
#    Given I add the "Player" role to "user@ayrabo.com" for "Ice Hockey"
#    And The following player object exists
#      | username_or_email | sport      | team                  |
#      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats |
#    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
#    And I press "player_tab"
#    And I press "actions-dropdown-player-green-machine-icecats"
#    And I press "list_games_player_btn_green-machine-icecats"
#    Then I should be on the "teams:games:list" page with kwargs "team_pk=1"
#
#  Scenario: Navigate to hockey game list page as coach
#    Given I add the "Coach" role to "user@ayrabo.com" for "Ice Hockey"
#    And The following coach object exists
#      | username_or_email | team                  |
#      | user@ayrabo.com   | Green Machine IceCats |
#    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
#    And I press "coach_tab"
#    And I press "actions-dropdown-coach-green-machine-icecats"
#    And I press "list_games_coach_btn_green-machine-icecats"
#    Then I should be on the "teams:games:list" page with kwargs "team_pk=1"

  Scenario: Helpful text displayed to user
    Given I am on the "teams:games:list" page with kwargs "team_pk=1"
    Then I should see "Games for Green Machine IceCats"
    And I should see "Midget Minor AA - LIAHL"

  Scenario: No games
    Given I am on the "teams:games:list" page with kwargs "team_pk=1"
    Then "no-games-header" should be visible
    And I should see "There are no games for this team."
    And "create-game-btn-empty-state" should be visible

  Scenario: Games exist
    Given The following game objects exist
      | id | home_team             | away_team             | type   | point_value | location | start               | end                 | timezone   | season |
      | 1  | Green Machine IceCats | Long Island Edge      | league | 2           | Iceland  | 10/23/2017 07:00 PM | 10/23/2017 09:00 PM | US/Eastern | 1      |
      | 2  | Long Island Edge      | Green Machine IceCats | league | 2           | Iceland  | 10/30/2017 07:00 PM | 10/30/2017 09:00 PM | US/Eastern | 1      |
      | 3  | Long Island Edge      | Aviator Gulls         | league | 2           | Iceland  | 10/31/2017 07:00 PM | 10/31/2017 09:00 PM | US/Eastern | 1      |

    And I am on the "teams:games:list" page with kwargs "team_pk=1"
    Then "create-game-btn" should be visible
    And I should see "1"
    And I should see "Green Machine IceCats"
    And I should see "League"
    And I should see "Scheduled"
    And I should see "Iceland"
    And I should see "10/23/2017 07:00 PM EDT"
    And I should see "10/23/2017 09:00 PM EDT"
    And I should see "2017-2018 Season"
    And I should not see "Aviator Gulls"

  Scenario: Not team manager
    Given The following game objects exist
      | home_team             | away_team             | type   | point_value | location | start               | end                 | timezone   | season |
      | Green Machine IceCats | Long Island Edge      | league | 2           | Iceland  | 10/23/2017 07:00 PM | 10/23/2017 09:00 PM | US/Eastern | 1      |
      | Long Island Edge      | Green Machine IceCats | league | 2           | Iceland  | 10/30/2017 07:00 PM | 10/30/2017 09:00 PM | US/Eastern | 1      |
      | Long Island Edge      | Aviator Gulls         | league | 2           | Iceland  | 10/31/2017 07:00 PM | 10/31/2017 09:00 PM | US/Eastern | 1      |
    And I login with "user1@ayrabo.com" and "myweakpassword"
    And I am on the "teams:games:list" page with kwargs "team_pk=1"
    Then "create-game-btn" should not exist on the page
    And "create-game-btn-empty-state" should not exist on the page
    And "i.fa.fa-pencil" should not exist on the page
