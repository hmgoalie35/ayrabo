Feature: Select sport roles
  As a user of the site,
  So that I can register for different roles for different sports
  I want to be able to choose which roles I want for each sport I register for

  """
  NOTE: The following 3 lines, and any variations of them are used to simulate a user filling out the rolesmask for the
  desired sport. It makes sure the template displays the correct # of sports remaining, and more. Just using the second
  line won't work because the view won't set the context variable that displays the # remaining sports correctly

    Given I am on the "profile:select_roles" page
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And I am on the "profile:select_roles" page
  """

  Background: User, userprofile, rolesmasks exist
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       |
      | John       | Doe       | user@example.com | myweakpassword |
    And The userprofile for "user@example.com" is not complete
    And A rolesmask exists for "user@example.com" for "Ice Hockey"
    And A rolesmask exists for "user@example.com" for "Soccer"
    And A rolesmask exists for "user@example.com" for "Tennis"
    And I login with "user@example.com" and "myweakpassword"

  Scenario: Correct descriptions and text are displayed
    Given I am on the "profile:select_roles" page
    Then I should be on the "profile:select_roles" page
    Then I should see "Select Roles for Ice Hockey"
    And I should see "The roles you choose here will affect the permissions you have throughout"
    And I should see "3 sports remaining"

  Scenario: Prompted to fill out Ice Hockey form first
    Given I am on the "profile:select_roles" page
    Then I should see "Select Roles for Ice Hockey"
    And I should see "3 sports remaining"
    And I should see "Ice Hockey"

  Scenario: Submit valid form for ice hockey
    Given I am on the "profile:select_roles" page
    When I press "id_roles_1"
    And I press "id_roles_4"
    And I press "select_roles_next_sport"
    Then I should be on the "profile:select_roles" page
    And I should see "2 sports remaining"

  Scenario: Submit invalid form for ice hockey
    Given I am on the "profile:select_roles" page
    When I press "select_roles_next_sport"
    Then "This field is required." should show up 1 time
    And I should see "3 sports remaining"

  Scenario: Prompted to fill out Soccer form second
    Given I am on the "profile:select_roles" page
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And I am on the "profile:select_roles" page
    Then I should see "Select Roles for Soccer"
    And I should see "2 sports remaining"
    And I should see "Soccer"

  Scenario: Submit valid form for soccer
    Given I am on the "profile:select_roles" page
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And I am on the "profile:select_roles" page
    When I press "id_roles_1"
    And I press "id_roles_2"
    And I press "select_roles_next_sport"
    Then I should be on the "profile:select_roles" page
    And I should see "1 sport remaining"

  Scenario: Submit invalid form for soccer
    Given I am on the "profile:select_roles" page
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And I am on the "profile:select_roles" page
    When I press "select_roles_next_sport"
    Then "This field is required." should show up 1 time
    And I should see "2 sports remaining"

  Scenario: Prompted to fill out Tennis form last
    Given I am on the "profile:select_roles" page
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And The rolesmask for "user@example.com" and "Soccer" is complete
    And I am on the "profile:select_roles" page
    Then I should see "Select Roles for Tennis"
    And I should see "1 sport remaining"
    And I should see "Tennis"

  Scenario: Submit valid form for tennis
    Given I am on the "profile:select_roles" page
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And The rolesmask for "user@example.com" and "Soccer" is complete
    And I am on the "profile:select_roles" page
    When I press "id_roles_1"
    And I press "id_roles_3"
    And I press "select_roles_next_sport"
    Then I should be on the "profile:finish" page

  Scenario: Submit invalid form for tennis
    Given I am on the "profile:select_roles" page
    And The rolesmask for "user@example.com" and "Ice Hockey" is complete
    And The rolesmask for "user@example.com" and "Soccer" is complete
    And I am on the "profile:select_roles" page
    When I press "select_roles_next_sport"
    Then "This field is required." should show up 1 time
    And I should see "1 sport remaining"
