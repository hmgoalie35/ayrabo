Feature: Sport dashboard
  As a user,
  I want to be able to see all sports I have been registered for
  So that I can have a single place linking me to other parts of the site

  Background: User exists
    Given The following confirmed user accounts exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following sport registrations exist
      | username_or_email | sport      | roles         | complete |
      | user@ayrabo.com   | Ice Hockey | Player, Coach | true     |
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

  Scenario: User registered for sports, role objects exist
    Given The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following player objects exist
      | username_or_email | sport      | team                  |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats |
    And The following coach object exists
      | username_or_email | team             |
      | user@ayrabo.com   | Long Island Edge |
    And I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    Then I should see "Long Island Edge"
    And I press "player-tab"
    Then I should see "Green Machine IceCats"
