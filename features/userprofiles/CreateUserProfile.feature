Feature: User profiles
  As a developer of the site,
  So that I can better organize site users
  I want to be able to collect extra information about users

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       | create_userprofile |
      | John       | Doe       | user@example.com | myweakpassword | false              |
    And The following sport exists "Ice Hockey"
    And The following sport exists "Baseball"
    And I login with "user@example.com" and "myweakpassword"

# Userprofile does not exist, create profile page
  Scenario: Prompted to fill out user profile after logging in for the first time
    Given I go to the "home" page
    Then I should be on the "account_complete_registration" page
    And I should see "Complete Your Account Registration"
    And I should see "You will register for sports in the next step."

  Scenario: Redirected when trying to navigate to new sport registration page when userprofile not complete
    Given I go to the "sportregistrations:create" page
    Then I should be on the "account_complete_registration" page

  Scenario: Fill out with invalid height
    Given I am on the "account_complete_registration" page
    When I select "male" from "id_gender"
    And I fill in "id_height" with "5' 7"
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should see "Invalid format, please enter your height according to the format below."

  Scenario: Fill out with invalid weight
    Given I am on the "account_complete_registration" page
    When I select "male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "-1"
    And I press "create_userprofile_btn"
    Then I should see "Ensure this value is greater than or equal to 1."

  Scenario: Fill out with invalid birthday
    Given I am on the "account_complete_registration" page
    When I select "male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "100"
    And I press "create_userprofile_btn"
    Then I should see "This field is required."

  Scenario: Submit invalid form
    Given I am on the "account_complete_registration" page
    When I press "create_userprofile_btn"
    Then "This field is required." should show up 4 times

  Scenario: Submit valid form
    Given I am on the "account_complete_registration" page
    When I select "male" from "id_gender"
    And I select "April" from "id_birthday_month"
    And I select "4" from "id_birthday_day"
    And I select "1994" from "id_birthday_year"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should be on the "sportregistrations:create" page

    # See features/sports/NewSportRegistration.feature for the next set of tests
