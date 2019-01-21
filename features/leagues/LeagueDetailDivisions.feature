Feature: League detail divisions
  As a user,
  I want to be able to view the divisions and teams for a league
  So that I can see an overview of the league

  Background:
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following league objects exist
      | name                              | sport      |
      | Long Island Amateur Hockey League | Ice Hockey |

    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 3  | Aviator Gulls         | PeeWee          | Long Island Amateur Hockey League | Ice Hockey |
      | 4  | Long Island Rebels    | PeeWee          | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to league divisions page
    Given I am on the "leagues:schedule" page with kwargs "slug=liahl"
    And I press "tab-item-divisions"
    Then I should be on the "leagues:divisions" page with kwargs "slug=liahl"

  Scenario: Basic info displayed to user
    Given I am on the "leagues:divisions" page with kwargs "slug=liahl"
    Then I should see "Divisions Archive"
    And I should see "Midget Minor AA"
    And I should see "Green Machine IceCats"
    And I should see "Long Island Edge"
    And I should see "PeeWee"
    And I should see "Aviator Gulls"
    And I should see "Long Island Rebels"

  Scenario: Team names are links
    Given I am on the "leagues:divisions" page with kwargs "slug=liahl"
    When I press "Green Machine IceCats"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=1"

  Scenario: No divisions exist
    Given The following league object exists
      | name                   | sport      |
      | National Hockey League | Ice Hockey |
    And I am on the "leagues:divisions" page with kwargs "slug=nhl"
    Then I should see "There are no divisions tied to National Hockey League at this time."

  Scenario: No teams for division exist
    Given The following league object exists
      | name                   | sport      |
      | National Hockey League | Ice Hockey |
    And The following division object exists
      | name              | league                 |
      | Atlantic Division | National Hockey League |
    And I am on the "leagues:divisions" page with kwargs "slug=nhl"
    Then I should see "There are no teams tied to Atlantic Division at this time."
