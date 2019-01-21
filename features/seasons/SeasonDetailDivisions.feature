Feature: Season detail divisions
  As a user,
  I want to be able to view the divisions and teams for a season
  So that I can see an overview of the season

  Background:
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following league objects exist
      | name                              | sport      |
      | Long Island Amateur Hockey League | Ice Hockey |
      | National Hockey League            | Ice Hockey |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 3  | Aviator Gulls         | PeeWee          | Long Island Amateur Hockey League | Ice Hockey |
      | 4  | Long Island Rebels    | PeeWee          | Long Island Amateur Hockey League | Ice Hockey |
    And The following season objects exist
      | id | league                            | teams                                                                      |
      | 1  | Long Island Amateur Hockey League | Green Machine IceCats, Long Island Edge, Aviator Gulls, Long Island Rebels |
      | 2  | National Hockey League            |                                                                            |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to season divisions page
    Given I am on the "leagues:seasons:schedule" page with kwargs "slug=liahl, season_pk=1"
    And I press "tab-item-divisions"
    Then I should be on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=1"

  Scenario: Basic info displayed to user
    Given I am on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=1"
    Then I should see "Divisions"
    And I should see "Midget Minor AA"
    And I should see "Green Machine IceCats"
    And I should see "Long Island Edge"
    And I should see "PeeWee"
    And I should see "Aviator Gulls"
    And I should see "Long Island Rebels"

  Scenario: Team names are links
    Given I am on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=1"
    When I press "Green Machine IceCats"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=1"

  Scenario: No divisions exist
    Given I am on the "leagues:seasons:divisions" page with kwargs "slug=nhl, season_pk=2"
    Then I should see "There are no divisions tied to National Hockey League at this time."

