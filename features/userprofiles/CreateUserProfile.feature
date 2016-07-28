Feature: User profiles
  As a developer of the site,
  So that I can better organize site users
  I want to be able to collect extra information about users

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email             | password       | create_userprofile |
      | John       | Doe       | user@example.com  | myweakpassword | false              |
      | Jane       | Doe       | user1@example.com | myweakpassword | true               |

# Userprofile does not exist, create profile page
  Scenario: Prompted to fill out user profile after logging in for the first time
    Given I login with "user@example.com" and "myweakpassword"
    When I go to the "home" page
    Then I should be on the "profile:create" page
    And I should see "Create Your Profile"
    And I should see "You will fill out your team and any role specific information in the next step"

  Scenario: Navigate to another page when profile doesn't exist
    Given I login with "user@example.com" and "myweakpassword"
    When I go to the "home" page
    Then I should be on the "profile:create" page

  Scenario: Fill out with invalid height
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:create" page
    When I press "id_roles_1"
    And I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7"
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should see "Invalid format, please use the following format: 5' 7""

  Scenario: Fill out with invalid weight
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:create" page
    When I press "id_roles_1"
    And I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "-1"
    And I press "create_userprofile_btn"
    Then I should see "Ensure this value is greater than or equal to 1."

  Scenario: Fill out with no roles
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:create" page
    When I select "Male" from "id_gender"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "-1"
    And I press "create_userprofile_btn"
    Then I should see "This field is required."

  Scenario: Submit invalid form
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:create" page
    When I press "create_userprofile_btn"
    Then "This field is required." should show up 5 times

  Scenario: Submit valid form
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "profile:create" page
    When I press "id_roles_1"
    And I press "id_roles_2"
    And I select "Male" from "id_gender"
    # 4 stands for April
    And I select "4" from "id_birthday_month"
    And I select "4" from "id_birthday_day"
    And I select "1994" from "id_birthday_year"
    And I fill in "id_height" with "5' 7""
    And I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should be on the "profile:finish" page

    # See coaches, players, referees, managers folders in features/ for tests regarding the next steps for filling out coach, players, etc. specific info


# Userprofile exists
  Scenario: Userprofile already exists
    Given I login with "user1@example.com" and "myweakpassword"
    When I go to the "home" page
    Then I should see "You are currently logged in as Jane Doe, user1@example.com"

  Scenario: Navigate to user profile creation page when profile already exists
    Given I login with "user1@example.com" and "myweakpassword"
    When I go to the "profile:create" page
    Then I should be on the "home" page
    And I should see "You are currently logged in as Jane Doe, user1@example.com"

