Feature: Add roles to a sport registration
  As a user of the site,
  So that I can add any roles I did not initially register for
  I want to be able to add roles to a sport I have registered for

  Background: User and sport registration exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@ayrabo.com" and "myweakpassword"

    # Make sure can navigate from sport registration detail page to creation page for chosen role
  Scenario: Navigate to add player role page
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Coach"
    And The following coach object exists
      | username_or_email | team                  | position   |
      | user@ayrabo.com   | Green Machine IceCats | head_coach |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    When I press "Available Roles"
    And I press "add_player_role_link"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"

  Scenario: Navigate to add coach role page
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Player, Referee"
    And The following referee object exists
      | username_or_email | league                            |
      | user@ayrabo.com   | Long Island Amateur Hockey League |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    When I press "Available Roles"
    And I press "add_coach_role_link"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"

  Scenario: Navigate to add referee role page
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Player, Coach, Manager"
    And The following coach object exists
      | username_or_email | team                  | position   |
      | user@ayrabo.com   | Green Machine IceCats | head_coach |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And The following manager object exists
      | username_or_email | team                  |
      | user@ayrabo.com   | Green Machine IceCats |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    When I press "Available Roles"
    And I press "add_referee_role_link"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"

  Scenario: Navigate to add manager role page
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Player"
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    When I press "Available Roles"
    And I press "add_manager_role_link"
    Then I should be on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"

  Scenario: Add scorekeeper role
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Player"
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    When I press "Available Roles"
    And I press "add_scorekeeper_role_link"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    And I should see "You have been registered as a scorekeeper for Ice Hockey."

    # We know we can navigate to the player, coach, etc creation page but now try to actually create an object. Scenarios
  # below are different from general player, coach, etc creation because the code is adding the new role and removing
  # it if things go wrong.
  Scenario: Add player role
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Coach"
    And The following coach object exists
      | username_or_email | team                  | position   |
      | user@ayrabo.com   | Green Machine IceCats | head_coach |
    And I am on the "sports.SportRegistration" "" "sportregistrations:players:create" page with url kwargs "pk=pk"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_players-0-team"
    And I fill in "id_players-0-jersey_number" with "35"
    And I select "LW" from "id_players-0-position"
    And I select "Left" from "id_players-0-handedness"
    And I press "create_objects_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"

  Scenario: Add coach role
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Player, Referee"
    And The following referee object exists
      | username_or_email | league                            |
      | user@ayrabo.com   | Long Island Amateur Hockey League |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And I am on the "sports.SportRegistration" "" "sportregistrations:coaches:create" page with url kwargs "pk=pk"
    And I select "head_coach" from "id_coaches-0-position"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_coaches-0-team"
    And I press "create_objects_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"

  Scenario: Add referee role
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Coach"
    And The following coach object exists
      | username_or_email | team                  | position   |
      | user@ayrabo.com   | Green Machine IceCats | head_coach |
    And I am on the "sports.SportRegistration" "" "sportregistrations:referees:create" page with url kwargs "pk=pk"
    And I select "Long Island Amateur Hockey League" from "id_referees-0-league"
    And I press "create_objects_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"

  Scenario: Add manager role
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with role "Player, Coach"
    And The following coach object exists
      | username_or_email | team                  | position   |
      | user@ayrabo.com   | Green Machine IceCats | head_coach |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And I am on the "sports.SportRegistration" "" "sportregistrations:managers:create" page with url kwargs "pk=pk"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_managers-0-team"
    And I press "create_objects_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
