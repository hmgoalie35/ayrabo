Feature: League divisions

  Background:
    Given The following users exist
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
    And The following seasons exist
      | id | league                            | teams                                                                      | start_date | end_date |
      # Past
      | 3  | Long Island Amateur Hockey League | Long Island Edge                                                           | -1y        | -2y      |
      # Current
      | 1  | Long Island Amateur Hockey League | Green Machine IceCats, Long Island Edge, Aviator Gulls, Long Island Rebels | today      | 1y       |
      # Future
      | 4  | Long Island Amateur Hockey League | Green Machine IceCats                                                      | 1y         | 2y       |
      | 2  | National Hockey League            |                                                                            | today      | 1y       |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Team names are links
    Given I am on the "leagues:divisions" page with kwargs "slug=liahl"
    When I press "Green Machine IceCats"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=1"

  Scenario: No divisions exist
    Given I am on the "leagues:divisions" page with kwargs "slug=nhl"
    Then I should see "There are no divisions tied to National Hockey League at this time."

  Scenario: No teams for division exist
    Given The following division object exists
      | name              | league                 |
      | Atlantic Division | National Hockey League |
    And I am on the "leagues:divisions" page with kwargs "slug=nhl"
    Then I should see "There are no teams tied to Atlantic Division at this time."

  Scenario: Navigate to league divisions page for current season
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    And I press "tab-item-divisions"
    Then I should be on the "leagues:divisions" page with kwargs "slug=liahl"

  Scenario: View current season
    Given I am on the "leagues:divisions" page with kwargs "slug=liahl"
    Then I should see "All Divisions"
    And I should see "Midget Minor AA"
    And I should see "Green Machine IceCats"
    And I should see "Long Island Edge"
    And I should see "PeeWee"
    And I should see "Aviator Gulls"
    And I should see "Long Island Rebels"

  Scenario: View current season, press divisions nav tab again
    Given I am on the "leagues:divisions" page with kwargs "slug=liahl"
    And I press "tab-item-divisions"
    Then I should be on the "leagues:divisions" page with kwargs "slug=liahl"

  Scenario: Navigate to league divisions page for past season
    Given I am on the "leagues:divisions" page with kwargs "slug=liahl"
    And I press "tab-item-seasons"
    And I press "season-3"
    And I press "tab-item-divisions"
    Then I should be on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=3"

  Scenario: View past season
    Given I am on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=3"
    Then I should see "This season has been archived."
    And I should see "Divisions for all seasons are available"
    And I should see season "-1y" "-2y"
    And I should see "Midget Minor AA"
    And I should see "Green Machine IceCats"
    And I should see "Long Island Edge"
    And I should not see "PeeWee"
    And I should not see "Aviator Gulls"

  Scenario: View past season, press divisions nav tab again
    Given I am on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=3"
    And I press "tab-item-divisions"
    Then I should be on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=3"

  Scenario: Navigate to league divisions page for future season
    Given I am on the "leagues:divisions" page with kwargs "slug=liahl"
    And I press "tab-item-seasons"
    And I press "season-4"
    And I press "tab-item-divisions"
    Then I should be on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=4"

  Scenario: View future season
    Given I am on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=4"
    Then I should see "This season has not started yet."
    And I should see "Divisions for all seasons are available"
    And I should see season "1y" "2y"
    And I should see "Midget Minor AA"
    And I should see "Green Machine IceCats"
    And I should see "Long Island Edge"
    And I should not see "PeeWee"
    And I should not see "Aviator Gulls"

  Scenario: View future season, press divisions nav tab again
    Given I am on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=4"
    And I press "tab-item-divisions"
    Then I should be on the "leagues:seasons:divisions" page with kwargs "slug=liahl, season_pk=4"
