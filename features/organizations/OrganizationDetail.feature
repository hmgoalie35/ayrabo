Feature: Organization profile
  As an organization admin,
  I want to be able to administrate my organization
  So that I can effectively administrate my organization

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following organization object exists
      | id | name                  | sport      |
      | 1  | Green Machine IceCats | Ice Hockey |
    And The following permissions exist
      | username_or_email | name  | model                      | object_id |
      | user@ayrabo.com   | admin | organizations.Organization | 1         |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Basic info displayed
    Given I am on the "organizations:detail" page with kwargs "pk=1"
    Then I should see "Green Machine IceCats Organization"
    And "tab-item-organization-admins" should be visible
    And "tab-item-teams" should be visible

  Scenario: Teams tab
    Given The following team objects exist
      | id | name                  | division        | league                            | sport      | organization |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey | 1            |
      | 2  | Green Machine IceCats | 16U Tier I      | Long Island Amateur Hockey League | Ice Hockey | 1            |
      | 3  | Green Machine IceCats | 14U Milner      | Long Island Amateur Hockey League | Ice Hockey | 1            |
    And I am on the "organizations:detail" page with kwargs "pk=1"
    Then I should see "Midget Minor AA"
    And I should see "16U Tier I"
    And I should see "14U Milner"
    And "Long Island Amateur Hockey League" should show up 3 times
    When I press "Green Machine IceCats"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=1"

  Scenario: Teams tab team name link works
    Given The following team object exists
      | id | name                  | division        | league                            | sport      | organization |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey | 1            |
    And I am on the "organizations:detail" page with kwargs "pk=1"
    When I press "Green Machine IceCats"
    Then I should be on the "teams:schedule" page with kwargs "team_pk=1"

  Scenario: Teams tab league name link works
    Given The following team object exists
      | id | name                  | division        | league                            | sport      | organization |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey | 1            |
    And I am on the "organizations:detail" page with kwargs "pk=1"
    When I press "Long Island Amateur Hockey League"
    Then I should be on the "leagues:schedule" page with kwargs "slug=liahl"

  Scenario: Teams tab (empty state)
    Given I am on the "organizations:detail" page with kwargs "pk=1"
    Then I should see "This organization does not have any teams."

  Scenario: Organization admins tab
    Given I am on the "organizations:detail" page with kwargs "pk=1"
    And I press "tab-item-organization-admins"
    Then "organization_admins" should be visible
    And "list-group" should contain text "John Doe"
    And "list-group" should contain text "user@ayrabo.com"
    And I should see "Organization admins are managed by our staff."

  # Scenario below is not currently possible
  # Scenario: Organization admins tab (empty state)
