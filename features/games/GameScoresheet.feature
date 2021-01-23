Feature: Game scoresheet
  As an authenticated user,
  I want to be able to view a game's scoresheet

  Background: User exists
    Given The following users exist
      | first_name | last_name | email               | password       |
      | Michael    | Scott     | mscott@ayrabo.com   | myweakpassword |
      | Dwight     | Schrute   | dschrute@ayrabo.com | myweakpassword |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following manager objects exist
      | username_or_email   | team                  |
      | dschrute@ayrabo.com | Green Machine IceCats |
    And The following generic choice objects exist
      | content_type | short_value | long_value | type             |
      | sports.Sport | league      | League     | game_type        |
      | sports.Sport | 2           | 2          | game_point_value |
    And The following location object exists
      | name    |
      | Iceland |
    And The following seasons exist
      | id | league                            | start_date | end_date   | teams                                   |
      | 1  | Long Island Amateur Hockey League | 2017-09-01 | 2018-09-02 | Green Machine IceCats, Long Island Edge |
      | 2  | Long Island Amateur Hockey League | today      | 1y         | Green Machine IceCats, Long Island Edge |
    And The following game objects exist
      | id | home_team             | away_team        | type   | point_value | location | start               | end                 | timezone   | season |
      | 1  | Green Machine IceCats | Long Island Edge | league | 2           | Iceland  | 10/23/2017 07:00 PM | 10/23/2017 09:00 PM | US/Eastern | 1      |
      | 2  | Green Machine IceCats | Long Island Edge | league | 2           | Iceland  | today               | today               | US/Eastern | 2      |
      | 3  | Green Machine IceCats | Long Island Edge | league | 2           | Iceland  | tomorrow            | tomorrow            | US/Eastern | 2      |

  Scenario: View basic game details
    Given I login with "mscott@ayrabo.com" and "myweakpassword"
    And I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=1"
    Then I should see "Home Team"
    And I should see "Green Machine IceCats"
    And I should see "Long Island Amateur Hockey League"
    And I should see "10/23/2017 07:00 PM"
    And I should see "Iceland"
    And I should see "League"
    And I should see "Scheduled"
    And I should see "2017-2018"
    And I should see "Away Team"
    And I should see "Long Island Edge"
    And I should see "Long Island Amateur Hockey League"

  Scenario: User can't take score, view game before started
    Given I login with "mscott@ayrabo.com" and "myweakpassword"
    And I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=1"
    Then "Scheduled" should show up 2 times
    And I should see "Countdown to Game Start"
    And I should see "minutes"

  Scenario: User can take score, navigates to game roster edit page
    Given I login with "dschrute@ayrabo.com" and "myweakpassword"
    And I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=2"
    When I press "game-roster-edit-btn"
    Then I should be on the "sports:games:rosters:update" page with kwargs "slug=ice-hockey, game_pk=2"

  Scenario: User can take score, submits valid form via save button
    Given The following player objects exist
      | id | username_or_email  | sport      | team                  | jersey_number | position | handedness |
      | 1  | goalie1@ayrabo.com | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
      | 2  | goalie2@ayrabo.com | Ice Hockey | Long Island Edge      | 30            | G        | Right      |
    And The following game players exist
      | id | player_pk | game_pk | team_pk | is_starting |
      | 1  | 1         | 2       | 1       | True        |
      | 2  | 2         | 2       | 2       | True        |
    And I login with "dschrute@ayrabo.com" and "myweakpassword"
    And I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=2"
    And I fill in "id_period_duration" with "15"
    And I press "save-btn"
    Then I should see "Your updates have been saved."
    And I should be on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=2"
    And I should see "Initialize Game"

  Scenario: User can take score, submits invalid form via save button
    Given The following player objects exist
      | id | username_or_email  | sport      | team                  | jersey_number | position | handedness |
      | 1  | goalie1@ayrabo.com | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
      | 2  | goalie2@ayrabo.com | Ice Hockey | Long Island Edge      | 30            | G        | Right      |
    And The following game players exist
      | id | player_pk | game_pk | team_pk | is_starting |
      | 1  | 1         | 2       | 1       | False       |
      | 2  | 2         | 2       | 2       | False       |
    And I login with "dschrute@ayrabo.com" and "myweakpassword"
    And I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=2"
    And I fill in "id_period_duration" with "20"
    And I press "save-btn"
    Then "Please select a starting goaltender." should show up 2 times
    And I should not see "Your updates have been saved."

  Scenario: User can take score, submits valid form via save and start game button
    Given The following player objects exist
      | id | username_or_email  | sport      | team                  | jersey_number | position | handedness |
      | 1  | goalie1@ayrabo.com | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
      | 2  | goalie2@ayrabo.com | Ice Hockey | Long Island Edge      | 30            | G        | Right      |
    And The following game players exist
      | id | player_pk | game_pk | team_pk | is_starting |
      | 1  | 1         | 2       | 1       | True        |
      | 2  | 2         | 2       | 2       | True        |
    And I login with "dschrute@ayrabo.com" and "myweakpassword"
    And I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=2"
    And I fill in "id_period_duration" with "15"
    And I press "save-and-start-game-btn"
    Then "save-and-start-game-modal" should be visible
    When I press "modal-btn-continue"
    Then I should see "You have successfully started this game."
    And I should be on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=2"

  Scenario: User can take score, submits invalid form via save and start game button
    Given The following player objects exist
      | id | username_or_email  | sport      | team                  | jersey_number | position | handedness |
      | 1  | goalie1@ayrabo.com | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
      | 2  | goalie2@ayrabo.com | Ice Hockey | Long Island Edge      | 30            | G        | Right      |
    And The following game players exist
      | id | player_pk | game_pk | team_pk | is_starting |
      | 1  | 1         | 2       | 1       | False       |
      | 2  | 2         | 2       | 2       | False       |
    And I login with "dschrute@ayrabo.com" and "myweakpassword"
    And I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=2"
    And I fill in "id_period_duration" with "20"
    And I press "save-and-start-game-btn"
    Then "save-and-start-game-modal" should be visible
    When I press "modal-btn-continue"
    Then "Please select a starting goaltender." should show up 2 times
    And I should not see "Your updates have been saved."

  Scenario: User can take score, save and start game button disabled
    Given I login with "dschrute@ayrabo.com" and "myweakpassword"
    And I am on the "sports:games:scoresheet" page with kwargs "slug=ice-hockey, game_pk=3"
    Then I should see "Games can only be started 30 minutes before the scheduled start time."
