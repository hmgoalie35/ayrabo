Feature: Organization profile
  As an organization admin,
  I want to be able to administrate my organization
  So that I can effectively administrate my organization

  Background: User exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following organization object exists
      | id | name                  |
      | 1  | Green Machine IceCats |
    And "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Manager"
    And "user@ayrabo.com" has the "admin" permission for "organizations.Organization" with kwargs "name=Green Machine IceCats"
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Basic info displayed
    Given I am on the "organizations:detail" page with kwargs "pk=1"
    Then I should see "Green Machine IceCats Organization"
    And "sidebar-item-organization-admins" should be visible
    And "sidebar-item-teams" should be visible

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

  Scenario: Teams tab (empty state)
    Given I am on the "organizations:detail" page with kwargs "pk=1"
    Then I should see "This organization does not have any teams."

  Scenario: Organization admins tab
    Given I am on the "organizations:detail" page with kwargs "pk=1"
    And I press "sidebar-item-organization-admins"
    Then "organization_admins" should be visible
    And "list-group" should contain text "John Doe"
    And "list-group" should contain text "user@ayrabo.com"
    And I should see "Organization admins are managed by our staff."

  # Scenario below is not currently possible
  # Scenario: Organization admins tab (empty state)
