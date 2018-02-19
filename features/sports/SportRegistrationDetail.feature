Feature: Sport registration detail
  As a user of the site,
  So that I can see what roles I chose for a sport
  I want to be able to see all roles and their details

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team objects exist
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following league objects exist
      | full_name                         | sport      |
      | Long Island Amateur Hockey League | Ice Hockey |
      | National Hockey League            | Ice Hockey |
    And The following sport registrations exist
      | username_or_email | sport      | roles                               | complete |
      | user@ayrabo.com   | Ice Hockey | Player, Coach, Referee, Scorekeeper | true     |
      | user@ayrabo.com   | Baseball   | Player, Coach, Manager, Referee     | true     |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And The following coach object exists
      | username_or_email | position   | team                  |
      | user@ayrabo.com   | head_coach | Green Machine IceCats |
    And The following referee object exists
      | username_or_email | league                            |
      | user@ayrabo.com   | Long Island Amateur Hockey League |
    And The following scorekeeper object exists
      | username_or_email | sport      |
      | user@ayrabo.com   | Ice Hockey |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Informative text displayed to user
    Given I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    Then I should see "Manage Your Ice Hockey Registration"
    And I should see "Available Roles"
    And I should see "Coaches"
    And I should see "Players"
    And I should see "Referees"
    And I should see "Scorekeepers"
    And "Green Machine IceCats" should show up 4 times
    And "Ice Hockey" should show up 5 times
    And I should see "Long Island Amateur Hockey League"
    And I press "available-roles-nav-tab"
    And "add_manager_role_link" should contain text "Register"

  Scenario: Add another player
    Given I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    And I press "player_tab"
    And I press "create_player_btn"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"

  Scenario: Add another coach
    Given I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    And I press "coach_tab"
    And I press "create_coach_btn"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"

  Scenario: Add another referee
    Given I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    And I press "referee_tab"
    And I press "create_referee_btn"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"

  Scenario: Add another manager
    Given I add the "Manager" role to "user@ayrabo.com" for "Ice Hockey"
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    And I press "manager_tab"
    And I press "create_manager_btn"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
