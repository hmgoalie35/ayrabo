Feature: User profiles
  As a developer of the site,
  So that I can better organize site users
  I want to be able to collect extra information about users

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email            | password       | create_userprofile |
      | John       | Doe       | user@example.com | myweakpassword | false              |
    And I login with "user@example.com" and "myweakpassword"

# Userprofile does not exist, create profile page
  Scenario: Prompted to fill out user profile after logging in for the first time
    Given I go to the "home" page
    Then I should be on the "profile:create" page
    And I should see "Create Your Profile"
    And I should see "Please fill out the required information below."
    And I should see "You will be prompted to register for sports on the next page."

  Scenario: Navigate to new sport registration page when userprofile not complete
    Given I go to the "sport:create_sport_registration" page
    Then I should be on the "profile:create" page

#  Scenario: Navigate to finish sport registration page when userprofile not complete
#    Given I go to the "" page
#    Then I should be on the "profile:create" page

  Scenario: Fill out with invalid height
    Given I am on the "profile:create" page
    When I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7"
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should see "Invalid format, please use the following format: 5' 7""

  Scenario: Fill out with invalid weight
    Given I am on the "profile:create" page
    When I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "-1"
    And I press "create_userprofile_btn"
    Then I should see "Ensure this value is greater than or equal to 1."

  Scenario: Fill out with invalid birthday
    Given I am on the "profile:create" page
    When I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "100"
    And I press "create_userprofile_btn"
    Then I should see "This field is required."

  Scenario: Submit invalid form
    Given I am on the "profile:create" page
    When I press "create_userprofile_btn"
    Then "This field is required." should show up 4 times

  Scenario: Submit valid form
    Given I am on the "profile:create" page
    When I select "Male" from "id_gender"
    And I select "April" from "id_birthday_month"
    And I select "4" from "id_birthday_day"
    And I select "1994" from "id_birthday_year"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should be on the "sport:create_sport_registration" page

    # See features/sportregistrations/ for the next set of tests
