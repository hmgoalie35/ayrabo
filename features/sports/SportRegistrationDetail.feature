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
    And I should see "Coaches"
    And I should see "Players"
    And I should see "Referees"
    And I should see "Scorekeepers"
    # 6 because the team logo alt text is the team name
    And "Green Machine IceCats" should show up 6 times
    And "Ice Hockey" should show up 4 times
    And I should see "Long Island Amateur Hockey League"
