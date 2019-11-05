Feature: Sport dashboard
  As a user,
  I want to be able to see all sports I have been registered for
  So that I can have a single place linking me to other parts of the site

  Background: User exists
    Given The following confirmed user accounts exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following sport registrations exist
      | username_or_email | sport      | roles                           | complete |
      | user@ayrabo.com   | Ice Hockey | Player, Coach, Referee, Manager | true     |
    And The following organization object exists
      | id | name                  | sport      |
      | 1  | Long Island Edge      | Ice Hockey |
      | 2  | Green Machine IceCats | Ice Hockey |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      | organization |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey | 2            |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey | 1            |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to ice hockey sport dashboard page from navbar
    Given I am on the "home" page
    And I press "sport-dashboards-dropdown"
    And I press "ice-hockey-dashboard-link"
    Then I should be on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I should see "Ice Hockey Dashboard"

  Scenario: User registered for sports, no role objects
    Given I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I should see "Players"
    And I should see "Coaches"
    # Don't need to go crazy and test all cases...
    And I should see "There are currently no coaches associated with your account."

  Scenario: Coaches tab
    Given The following coach object exists
      | username_or_email | team             | position        |
      | user@ayrabo.com   | Long Island Edge | assistant_coach |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "coach-tab"
    Then I should see "Midget Minor AA"
    And I should see "Assistant Coach"
    When I press "Long Island Edge"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=2"

  Scenario: Coaches tab actions dropdown
    Given The following coach object exists
      | username_or_email | team             | position        |
      | user@ayrabo.com   | Long Island Edge | assistant_coach |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "coach-tab"
    And I press "actions-dropdown-coach-long-island-edge"
    And I press "list_games_coach_btn_long-island-edge"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=2"

  Scenario: Managers tab
    Given The following manager object exists
      | username_or_email | team             | position        |
      | user@ayrabo.com   | Long Island Edge | assistant_coach |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "manager-tab"
    Then I should see "Midget Minor AA"
    When I press "Long Island Edge"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=2"

  Scenario: Managers tab actions dropdown
    Given The following manager object exists
      | username_or_email | team             | position        |
      | user@ayrabo.com   | Long Island Edge | assistant_coach |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "manager-tab"
    And I press "actions-dropdown-manager-long-island-edge"
    And I press "list_games_manager_btn_long-island-edge"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=2"

  Scenario: Organizations tab
    Given The following permissions exist
      | username_or_email | name  | model                      | object_id |
      | user@ayrabo.com   | admin | organizations.Organization | 1         |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "organization-tab"
    Then I should see "Long Island Edge"
    When I press "Long Island Edge"
    Then I should be on the "organizations:detail" page with kwargs "pk=1"

  Scenario: Players tab
    Given The following player object exists
      | username_or_email | team             | sport      | jersey_number | position   |
      | user@ayrabo.com   | Long Island Edge | Ice Hockey | 35            | Goaltender |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "player-tab"
    Then I should see "Midget Minor AA"
    And I should see "35"
    And I should see "Goaltender"
    When I press "Long Island Edge"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=2"

  Scenario: Players tab actions dropdown
    Given The following player object exists
      | username_or_email | team             | sport      | jersey_number | position   |
      | user@ayrabo.com   | Long Island Edge | Ice Hockey | 35            | Goaltender |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "player-tab"
    And I press "actions-dropdown-player-long-island-edge"
    And I press "list_games_player_btn_long-island-edge"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=2"

  Scenario: Referees tab
    Given The following referee object exists
      | username_or_email | league                            |
      | user@ayrabo.com   | Long Island Amateur Hockey League |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    And I press "referee-tab"
    Then I should see "Long Island Amateur Hockey League"
    When I press "Long Island Amateur Hockey League"
    Then I should be on the "leagues:schedule" page with kwargs "slug=liahl"
