Feature: Remove roles from sport registration
  As a user of the site,
  So that I can remove any roles I do not utilize
  I want to be able to remove roles I have for a sport.

  Background: User, sport registration, related objects exist
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Multiple roles, deactivate last coach registration
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player, Coach"
    And The following coach object exists
      | username_or_email | position   | team                  | id |
      | user@example.com  | Head Coach | Green Machine IceCats | 1  |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness | id |
      | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "deactivate-green-machine-icecats-coach-link" which opens "coach-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a coach for the Green Machine IceCats."
    And I should see "You are about to deactivate your last ice hockey coach registration."
    And I should see "This will additionally revoke your ice hockey coach privileges."
    When I press "deactivate-green-machine-icecats-coach-btn"
    And I wait for a page refresh
    Then I should not see "You are a coach for 1 team"
    And I should not see "Coaches"

  Scenario: Multiple roles, deactivate last manager registration
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Referee, Manager"
    And The following manager object exists
      | username_or_email | team                  | id |
      | user@example.com  | Green Machine IceCats | 1  |
    And The following referee object exists
      | username_or_email | league                            | id |
      | user@example.com  | Long Island Amateur Hockey League | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I press "manager_tab"
    When I press "deactivate-green-machine-icecats-manager-link" which opens "manager-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a manager for the Green Machine IceCats."
    And I should see "You are about to deactivate your last ice hockey manager registration."
    And I should see "This will additionally revoke your ice hockey manager privileges."
    When I press "deactivate-green-machine-icecats-manager-btn"
    And I wait for a page refresh
    Then I should not see "You are a manager for 1 team"
    And I should not see "Managers"

  Scenario: Multiple roles, deactivate last player registration
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player, Coach"
    And The following coach object exists
      | username_or_email | position   | team                  | id |
      | user@example.com  | Head Coach | Green Machine IceCats | 1  |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness | id |
      | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I press "player_tab"
    When I press "deactivate-green-machine-icecats-player-link" which opens "player-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a player for the Green Machine IceCats."
    And I should see "You are about to deactivate your last ice hockey player registration."
    And I should see "This will additionally revoke your ice hockey player privileges."
    When I press "deactivate-green-machine-icecats-player-btn"
    And I wait for a page refresh
    Then I should not see "You are a player for 1 team"
    And I should not see "Players"

  Scenario: Multiple roles, deactivate last referee registration
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Referee, Manager"
    And The following manager object exists
      | username_or_email | team                  | id |
      | user@example.com  | Green Machine IceCats | 1  |
    And The following referee object exists
      | username_or_email | league                            | id |
      | user@example.com  | Long Island Amateur Hockey League | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    And I press "referee_tab"
    When I press "deactivate-long-island-amateur-hockey-league-referee-link" which opens "referee-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a referee for the Long Island Amateur Hockey League."
    And I should see "You are about to deactivate your last ice hockey referee registration."
    And I should see "This will additionally revoke your ice hockey referee privileges."
    When I press "deactivate-long-island-amateur-hockey-league-referee-btn"
    And I wait for a page refresh
    Then I should not see "You are a referee for 1 league"
    And I should not see "Referees"

  Scenario: One role, deactivate last coach registration
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Coach"
    And The following coach object exists
      | username_or_email | position   | team                  | id |
      | user@example.com  | Head Coach | Green Machine IceCats | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    Then I should see "You cannot deactivate this coach. You must be registered for at least one role."

  Scenario: One role, deactivate last player registration
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player"
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness | id |
      | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    Then I should see "You cannot deactivate this player. You must be registered for at least one role."

  Scenario: One role, deactivate last referee registration
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Referee"
    And The following referee object exists
      | username_or_email | league                            | id |
      | user@example.com  | Long Island Amateur Hockey League | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    Then I should see "You cannot deactivate this referee. You must be registered for at least one role."

  Scenario: One role, deactivate last manager registration
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Manager"
    And The following manager object exists
      | username_or_email | team                  | id |
      | user@example.com  | Green Machine IceCats | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    Then I should see "You cannot deactivate this manager. You must be registered for at least one role."

  Scenario: Multiple coaches
    Given "user@example.com" is completely registered for "Ice Hockey" with roles "Player, Coach"
    And The following team object exists
      | name                | division        | league                            | sport      |
      | Long Island Edge    | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | Nassau County Lions | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following coach object exists
      | username_or_email | position        | team                  | id |
      | user@example.com  | Head Coach      | Green Machine IceCats | 1  |
      | user@example.com  | Assistant Coach | Long Island Edge      | 2  |
      | user@example.com  | Head Coach      | Nassau County Lions   | 3  |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness | id |
      | user@example.com  | Ice Hockey | Green Machine IceCats | 35            | G        | Left       | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@example.com, sport__name=Ice Hockey"
    When I press "deactivate-green-machine-icecats-coach-link" which opens "coach-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a coach for the Green Machine IceCats."
    When I press "deactivate-green-machine-icecats-coach-btn"
    And I wait for a page refresh
    Then I should see "You are a coach for 2 teams"
