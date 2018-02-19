Feature: Remove roles from sport registration
  As a user of the site,
  So that I can remove any roles I do not utilize
  I want to be able to remove roles I have for a sport.

  Background: User, sport registration, related objects exist
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Multiple roles, deactivate last coach registration
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Player, Coach"
    And The following coach object exists
      | username_or_email | position   | team                  | id |
      | user@ayrabo.com   | head_coach | Green Machine IceCats | 1  |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness | id |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    And I press "actions-dropdown-coach-green-machine-icecats"
    When I press "deactivate-coach-green-machine-icecats" which opens "coach-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a coach for the Green Machine IceCats."
    And I should see "You are about to deactivate your last ice hockey coach registration."
    And I should see "This will additionally revoke your ice hockey coach privileges."
    When I press "deactivate-green-machine-icecats-coach-btn"
    And I wait for a page refresh
    Then "Green Machine IceCats" should show up 1 time

  Scenario: Multiple roles, deactivate last manager registration
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Referee, Manager"
    And The following manager object exists
      | username_or_email | team                  | id |
      | user@ayrabo.com   | Green Machine IceCats | 1  |
    And The following referee object exists
      | username_or_email | league                            | id |
      | user@ayrabo.com   | Long Island Amateur Hockey League | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    When I press "manager_tab"
    And I press "actions-dropdown-manager-green-machine-icecats"
    And I press "deactivate-manager-green-machine-icecats" which opens "manager-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a manager for the Green Machine IceCats."
    And I should see "You are about to deactivate your last ice hockey manager registration."
    And I should see "This will additionally revoke your ice hockey manager privileges."
    When I press "deactivate-green-machine-icecats-manager-btn"
    And I wait for a page refresh
    Then I should not see "Green Machine IceCats"
    And I should not see "Managers"

  Scenario: Multiple roles, deactivate last player registration
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Player, Coach"
    And The following coach object exists
      | username_or_email | position   | team                  | id |
      | user@ayrabo.com   | head_coach | Green Machine IceCats | 1  |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness | id |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    When I press "player_tab"
    And I press "actions-dropdown-player-green-machine-icecats"
    And  I press "deactivate-player-green-machine-icecats" which opens "player-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a player for the Green Machine IceCats."
    And I should see "You are about to deactivate your last ice hockey player registration."
    And I should see "This will additionally revoke your ice hockey player privileges."
    When I press "deactivate-green-machine-icecats-player-btn"
    And I wait for a page refresh
    Then "Green Machine IceCats" should show up 1 time
    And I should not see "Players"

  Scenario: Multiple roles, deactivate last referee registration
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Referee, Manager"
    And The following manager object exists
      | username_or_email | team                  | id |
      | user@ayrabo.com   | Green Machine IceCats | 1  |
    And The following referee object exists
      | username_or_email | league                            | id |
      | user@ayrabo.com   | Long Island Amateur Hockey League | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    When I press "referee_tab"
    And I press "actions-dropdown-referee-liahl"
    And I press "deactivate-referee-liahl" which opens "referee-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a referee for the Long Island Amateur Hockey League."
    And I should see "You are about to deactivate your last ice hockey referee registration."
    And I should see "This will additionally revoke your ice hockey referee privileges."
    When I press "deactivate-liahl-referee-btn"
    And I wait for a page refresh
    Then I should not see "Long Island Amateur Hockey League"
    And I should not see "Referees"

  Scenario: One role, deactivate last coach registration
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Coach"
    And The following coach object exists
      | username_or_email | position   | team                  | id |
      | user@ayrabo.com   | head_coach | Green Machine IceCats | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    Then I should see "You cannot deactivate this coach. You must be registered for at least one role."

  Scenario: One role, deactivate last player registration
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Player"
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness | id |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    Then I should see "You cannot deactivate this player. You must be registered for at least one role."

  Scenario: One role, deactivate last referee registration
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Referee"
    And The following referee object exists
      | username_or_email | league                            | id |
      | user@ayrabo.com   | Long Island Amateur Hockey League | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    Then I should see "You cannot deactivate this referee. You must be registered for at least one role."

  Scenario: One role, deactivate last manager registration
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Manager"
    And The following manager object exists
      | username_or_email | team                  | id |
      | user@ayrabo.com   | Green Machine IceCats | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    Then I should see "You cannot deactivate this manager. You must be registered for at least one role."

  Scenario: Multiple coaches
    Given "user@ayrabo.com" is completely registered for "Ice Hockey" with roles "Player, Coach"
    And The following team object exists
      | name                | division        | league                            | sport      |
      | Long Island Edge    | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | Nassau County Lions | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following coach object exists
      | username_or_email | position        | team                  | id |
      | user@ayrabo.com   | head_coach      | Green Machine IceCats | 1  |
      | user@ayrabo.com   | assistant_coach | Long Island Edge      | 2  |
      | user@ayrabo.com   | head_coach      | Nassau County Lions   | 3  |
    And The following player object exists
      | username_or_email | sport      | team                  | jersey_number | position | handedness | id |
      | user@ayrabo.com   | Ice Hockey | Green Machine IceCats | 35            | G        | Left       | 1  |
    And I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
    And I press "actions-dropdown-coach-green-machine-icecats"
    When I press "deactivate-coach-green-machine-icecats" which opens "coach-1-modal"
    Then I should see "Are You Sure?"
    And I should see "You will no longer be a coach for the Green Machine IceCats."
    When I press "deactivate-green-machine-icecats-coach-btn"
    And I wait for a page refresh
    Then I should see "Long Island Edge"
    And I should see "Nassau County Lions"
    And "Green Machine IceCats" should show up 2 times
