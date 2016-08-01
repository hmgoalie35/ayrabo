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
    Then I should be on the "profile:create" page
    And I should see "Create Your Profile"
    And I should see "Please only choose the sports you are currently playing."
    And I should see "You can always register for other sports after your profile has been finished."
    And I should see "You will be able to choose from the following roles: player, coach, referee, manager for each sport you select."
    And I should see "In the next steps you will be asked to fill out your team, jersey number, etc. for every sport you chose."

  Scenario: Navigate to select_roles page when userprofile not complete
    Given I go to the "profile:select_roles" page
    Then I should be on the "profile:create" page

  Scenario: Navigate to finish profile page when userprofile not complete
    Given I go to the "profile:finish" page
    Then I should be on the "profile:create" page

  Scenario: Fill out with invalid height
    Given I am on the "profile:create" page
    When I press "id_sports_chosen"
    And I press "#id_sports_chosen > div > ul > li:nth-child(1)"
    And I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7"
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should see "Invalid format, please use the following format: 5' 7""

  Scenario: Fill out with invalid weight
    Given I am on the "profile:create" page
    When I press "id_sports_chosen"
    And I press "#id_sports_chosen > div > ul > li:nth-child(1)"
    And I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "-1"
    And I press "create_userprofile_btn"
    Then I should see "Ensure this value is greater than or equal to 1."

  Scenario: Fill out with no sports
    Given I am on the "profile:create" page
    When I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "-1"
    And I press "create_userprofile_btn"
    Then I should see "This field is required."

  Scenario: Submit invalid form
    Given I am on the "profile:create" page
    When I press "create_userprofile_btn"
    Then "This field is required." should show up 5 times

  Scenario: Submit valid form
    Given I am on the "profile:create" page
    When I press "id_sports_chosen"
    And I press "#id_sports_chosen > div > ul > li:nth-child(2)"
    And I select "Male" from "id_gender"
    And I select "April" from "id_birthday_month"
    And I select "4" from "id_birthday_day"
    And I select "1994" from "id_birthday_year"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should be on the "profile:select_roles" page

    # See features/userprofiles/SelectRoles.featture for the next set of tests
