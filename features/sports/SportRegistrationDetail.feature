Feature: Sport registration detail
  As a user of the site,
  So that I can see what roles I chose for a sport
  I want to be able to see all roles and their details

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following sport registrations exist
      | username_or_email | sport      | roles                           | complete |
      | user@example.com  | Ice Hockey | Player, Coach, Referee          | true     |
      | user@example.com  | Baseball   | Player, Coach, Manager, Referee | true     |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And The following coach object exists
      | username_or_email | position   | team                  |
      | user@example.com  | Head Coach | Green Machine IceCats |
    And The following referee object exists
      | username_or_email | league                            |
      | user@example.com  | Long Island Amateur Hockey League |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Informative text displayed to user
    Given I am on the absolute url page for "sports.SportRegistration" and "user@example.com Ice Hockey"
    Then I should see "Manage Your Ice Hockey Registration"
    And I should see "Choose a tab below to view and manage your roles."
    And I should see "Available Roles"
    And I should see "Coaches"
    And I should see "Players"
    And I should see "Referees"
    And "Green Machine IceCats" should show up 2 times
    And I should see "Long Island Amateur Hockey League"
    And "Register" should show up 1 time
