Feature: Update player information
  As a user,
  I want to be able to update my player information for a given team

  Background: Player obj exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following sport registrations exist
      | id | username_or_email | sport      | roles  | complete |
      | 1  | user@example.com  | Ice Hockey | Player | true     |
    And The following player object exists
      | id | username_or_email | sport      | team                  | jersey_number | position | handedness |
      | 1  | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Navigate to the player update page
    Given I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "id_player"
    And I press "actions-dropdown-player-green-machine-icecats"
    And I press "update-player-link"
    Then I should be on the "/sport-registrations/1/players/1/update/" page
    And I should see "Update Player Information for Green Machine IceCats"

  Scenario: Submit changed form
    Given I am on the "/sport-registrations/1/players/1/update/" page
    And I fill in "id_jersey_number" with "23"
    And I press "update_player_btn"
    Then I should see "Your player information has been updated."
    And I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"

  Scenario: Submit unchanged form
    Given I am on the "/sport-registrations/1/players/1/update/" page
    And I press "update_player_btn"
    Then I should not see "Your player information has been updated."
    And I should be on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"


    # TODO add tests for other sports
