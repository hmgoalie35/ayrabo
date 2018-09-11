Feature: Sport dashboard
  As a user,
  I want to be able to see all sports I have been registered for
  So that I can have a single place linking me to other parts of the site

  Background: User exists
    Given The following confirmed user accounts exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to sport dashboard page from navbar
    Given I am on the "home" page
    And I press "sport-dashboard-btn"
    Then I should be on the "sports:dashboard" page
    And I should see "Sports Dashboard"

  Scenario: User not registered for any sports
    Given I am on the "sports:dashboard" page
    Then I should see "You have not been registered for any sports."

  Scenario: User registered for sports, no role objects
    Given The following sport registrations exist
      | username_or_email | sport      | roles            | is_complete |
      | user@ayrabo.com   | Ice Hockey | Player, Coach    | true        |
      | user@ayrabo.com   | Baseball   | Referee, Manager | true        |
    And I am on the "sports:dashboard" page
    Then I should see "Ice Hockey"
    And I should see "Baseball"
    And I should see "Any additional sports you are registered for will be displayed here."
    And I should see "Players"
    And I should see "Coaches"
    And I should see "Referees"
    And I should see "Managers"
    # Don't need to go crazy and test all cases...
    And I should see "There are currently no coaches associated with your account."

  Scenario: User registered for sports, role objects exist
    Given The following sport registrations exist
      | username_or_email | sport      | roles            | is_complete |
      | user@ayrabo.com   | Ice Hockey | Player, Coach    | true        |
      | user@ayrabo.com   | Baseball   | Referee, Manager | true        |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following player objects exist
      | username_or_email | sport      | team                  |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats |
    And The following coach objects exist
      | username_or_email | team             |
      | user@ayrabo.com   | Long Island Edge |
    And I am on the "sports:dashboard" page
    When I press "sidebar-item-ice-hockey"
    Then I should see "Long Island Edge"
    When I press "ice-hockey-player-tab"
    Then I should see "Green Machine IceCats"
