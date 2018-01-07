Feature: Location details
  As a user, I want to be able to view the address, phone, website, etc for a location
  so that I can navigate to and contact the location

  Background: Users exist
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The following team objects exist
      | id | name                  | division        | league                            | sport      |
      | 1  | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
      | 2  | Long Island Edge      | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And "user@example.com" is completely registered for "Ice Hockey" with role "Manager"
    And The following manager objects exist
      | username_or_email | team                  |
      | user@example.com  | Green Machine IceCats |
    And The following generic choice objects exist
      | content_type | short_value | long_value | type             |
      | sports.Sport | exhibition  | Exhibition | game_type        |
      | sports.Sport | league      | League     | game_type        |
      | sports.Sport | 2           | 2          | game_point_value |
    And The following location object exists
      | name    | street_number | street       | city          | state | zip_code | phone_number   | website                            |
      | Iceland | 3345          | Hillside Ave | New Hyde Park | NY    | 11040    | (516) 746-1100 | https://www.icelandlongisland.com/ |
    And The following season object exists
      | id | league                            | start_date | end_date   | teams                 |
      | 1  | Long Island Amateur Hockey League | 2017-09-14 | 2018-09-14 | Green Machine IceCats |
    And The following game object exists
      | home_team             | away_team        | type   | point_value | location | start               | end                 | timezone   | season |
      | Green Machine IceCats | Long Island Edge | league | 2           | Iceland  | 10/23/2017 07:00 PM | 10/23/2017 09:00 PM | US/Eastern | 1      |
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Navigate to location detail page
    Given I am on the "/teams/1/games/" page
    When I press "Iceland"
    Then I should be on the "locations:detail" page with kwargs "slug=iceland"

  Scenario: Relevant information displayed
    Given I am on the "locations:detail" page with kwargs "slug=iceland"
    Then I should see "Iceland"
    And I should see "Address:"
    And I should see "3345 Hillside Ave,"
    And I should see "New Hyde Park, NY 11040"
    And I should see "Phone:"
    And I should see "(516) 746-1100"
    And I should see "Website:"
    And I should see "https://www.icelandlongisland.com/"
    And I should see "Map"
