Feature: Update coach information
  As a user,
  I want to be able to update my coach information for a given team

  Background: Coach obj exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       |
      | John       | Doe       | user@ayrabo.com | myweakpassword |
    And The following team object exists
      | name                  | division        | league                            | sport      |
      | Green Machine IceCats | Midget Minor AA | Long Island Amateur Hockey League | Ice Hockey |
    And The following sport registrations exist
      | id | username_or_email | sport      | roles | complete |
      | 1  | user@ayrabo.com   | Ice Hockey | Coach | true     |
    And The following coach object exists
      | id | username_or_email | team                  | position   |
      | 1  | user@ayrabo.com   | Green Machine IceCats | head_coach |
    And I login with "user@ayrabo.com" and "myweakpassword"

#  Scenario: Navigate to the coach update page
#    Given I am on the absolute url page for "sports.SportRegistration" and "user__email=user@ayrabo.com, sport__name=Ice Hockey"
#    When I press "id_coach"
#    And I press "actions-dropdown-coach-green-machine-icecats"
#    And I press "update-coach-link"
#    Then I should be on the "/sports/ice-hockey/coaches/1/update/" page
#    And I should see "Update Coach Information for Green Machine IceCats"

  Scenario: Submit changed form
    Given I am on the "/sports/ice-hockey/coaches/1/update/" page
    And I select "assistant_coach" from "id_position"
    And I press "update_coach_btn"
    Then I should see "Your coach information has been updated."
    And I should be on the "home" page

  Scenario: Submit unchanged form
    Given I am on the "/sports/ice-hockey/coaches/1/update/" page
    And I press "update_coach_btn"
    Then I should not see "Your coach information has been updated."
    And I should be on the "home" page
