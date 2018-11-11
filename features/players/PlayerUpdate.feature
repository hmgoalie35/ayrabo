Feature: Update player information
  As a user,
  I want to be able to update my player information for a given team

  Background: Player obj exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following sport object exists
      | slug       | name       |
      | ice-hockey | Ice Hockey |
    And The following sport registrations exist
      | username_or_email | sport      | roles  | complete |
      | user@ayrabo.com   | Ice Hockey | Player | true     |
    And The following player object exists
      | id | username_or_email | sport_slug | team                  | jersey_number | position | handedness |
      | 1  | user@ayrabo.com   | ice-hockey | Green Machine IceCats | 35            | G        | Left       |
    And The following waffle switch exists
      | name          | active |
      | player_update | True   |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to the player update page
    Given I am on the "sports:dashboard" page with kwargs "slug=ice-hockey"
    When I press "player-tab"
    And I press "actions-dropdown-player-green-machine-icecats"
    And I press "update-player-link"
    Then I should be on the "/sports/ice-hockey/players/1/update/" page
    And I should see "Update Player Information for Green Machine IceCats"

  Scenario: Submit changed form
    Given I am on the "/sports/ice-hockey/players/1/update/" page
    And I fill in "id_jersey_number" with "23"
    And I press "update_player_btn"
    Then I should see "Your player information has been updated."
    And I should be on the "sports:dashboard" page with kwargs "slug=ice-hockey"

  Scenario: Submit unchanged form
    Given I am on the "/sports/ice-hockey/players/1/update/" page
    And I press "update_player_btn"
    Then I should not see "Your player information has been updated."
    And I should be on the "sports:dashboard" page with kwargs "slug=ice-hockey"
