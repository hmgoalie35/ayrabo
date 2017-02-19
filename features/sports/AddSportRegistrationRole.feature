Feature: Add roles to a sport registration
  As a user of the site,
  So that I can add any roles I did not initially register for
  I want to be able to add roles to a sport I have registered for

  Background: User and sport registration exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@example.com" and "myweakpassword"

  # as a user who does not already have player, coach, etc. objects.

  Scenario: Navigate to add player role page
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Coach"
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "add_player_role_link"
    Then I should be on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=player"

  Scenario: Navigate to add coach role page
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player, Referee"
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "add_coach_role_link"
    Then I should be on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=coach"

  Scenario: Navigate to add referee role page
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player, Coach, Manager"
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "add_referee_role_link"
    Then I should be on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=referee"

  Scenario: Navigate to add manager role page
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player"
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "add_manager_role_link"
    Then I should be on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=manager"

  Scenario: Add player role, object dne
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Coach"
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=player"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_hockeyplayer-team"
    And I fill in "id_hockeyplayer-jersey_number" with "35"
    And I select "LW" from "id_hockeyplayer-position"
    And I select "Left" from "id_hockeyplayer-handedness"
    And I press "add_role_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Player role successfully added to Ice Hockey"

  Scenario: Add coach role, object dne
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player, Referee"
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=coach"
    And I select "Head Coach" from "id_coach-position"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_coach-team"
    And I press "add_role_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Coach role successfully added to Ice Hockey"

  Scenario: Add referee role, object dne
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Coach"
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=referee"
    And I select "Long Island Amateur Hockey League" from "id_referee-league"
    And I press "add_role_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Referee role successfully added to Ice Hockey"

  Scenario: Add manager role, object dne
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player, Coach"
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=manager"
    And I select "Green Machine IceCats - Midget Minor AA" from "id_manager-team"
    And I press "add_role_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Manager role successfully added to Ice Hockey"

  # as a user who already has player, coach, etc. objects. (the user unregistered for a role and then re-registered for the role)
  Scenario: Informative text and disabled form displayed to user
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Coach"
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=player"
    Then I should see "It seems like you have previously registered as an Ice Hockey player."
    And I should see "Please confirm the information below is correct before adding the player role."
    And I should see "You will be able to update the information below on the next page."
    And "id_hockeyplayer-team" should be disabled
    And "id_hockeyplayer-jersey_number" should be disabled
    And "id_hockeyplayer-position" should be disabled
    And "id_hockeyplayer-handedness" should be disabled

  Scenario: Add player role, object exists
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Coach"
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=player"
    When I press "add_role_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Player role successfully added to Ice Hockey"

  Scenario: Add coach role, object exists
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player, Referee"
    And The following coach object exists
      | username_or_email | position   | team                  |
      | user@example.com  | Head Coach | Green Machine IceCats |
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=coach"
    When I press "add_role_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Coach role successfully added to Ice Hockey"

  Scenario: Add referee role, object exists
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Coach"
    And The following referee object exists
      | username_or_email | league                            |
      | user@example.com  | Long Island Amateur Hockey League |
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=referee"
    And I press "add_role_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Referee role successfully added to Ice Hockey"

  Scenario: Add manager role, object exists
    Given "user@example.com" is completely registered for "Ice Hockey" with role "Player, Coach"
    And The following manager object exists
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And I am on the "sports.SportRegistration" "user__email=user@example.com, sport__name=Ice Hockey" "sportregistrations:add_role" page with url kwargs "pk=pk, role=manager"
    And I press "add_role_btn"
    Then I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I should see "Manager role successfully added to Ice Hockey"
