Feature: League detail
  As an authenticated user,
  I want to be able to view details, standings and other info about a league
  So that I can have all of this info in a central place

  Background:
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following league objects exist
      | name                              | sport      |
      | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Basic info displayed to user
    Given I am on the "leagues:detail" page with kwargs "slug=liahl"
    Then I should see "Long Island Amateur Hockey League"
