Feature: User profiles
  As a developer of the site,
  So that I can better organize site users
  I want to be able to collect extra information about users

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email             | password       | create_userprofile |
      | John       | Doe       | user@example.com  | myweakpassword | false              |
      | Jane       | Doe       | user1@example.com | myweakpassword | true               |

# Userprofile does not exist
  Scenario: Prompted to fill out user profile after logging in for the first time
    Given I login with "user@example.com" and "myweakpassword"
    When I go to the "home" page
    Then I should be on the "create_userprofile" page
    And I should see "Complete Your Profile"
    And I should see "We need a few more pieces of information from you before you can access the site"

  Scenario: Navigate to another page when profile doesn't exist
    Given I login with "user@example.com" and "myweakpassword"
    When I go to the "account_edit" page
    Then I should be on the "create_userprofile" page

  Scenario: Fill out with invalid height
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "create_userprofile" page
    When I select "male" from "id_gender"
    When I fill in "id_height" with "5' 7"
    When I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should see "Invalid format, please use the following format: 5' 7""

  Scenario: Fill out with invalid weight
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "create_userprofile" page
    When I select "male" from "id_gender"
    When I fill in "id_height" with "5' 7""
    When I fill in "id_weight" with "-1"
    And I press "create_userprofile_btn"
    Then I should see "Weight must be greater than zero and less than 400"

  Scenario: Submit invalid form
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "create_userprofile" page
    When I press "create_userprofile_btn"
    Then "This field is required." should show up 3 times

  Scenario: Submit valid form
    Given I login with "user@example.com" and "myweakpassword"
    And I am on the "create_userprofile" page
    When I select "male" from "id_gender"
    When I fill in "id_height" with "5' 7""
    When I fill in "id_weight" with "130"
    And I press "create_userprofile_btn"
    Then I should see "Thank you for filling out your profile, you now have access to the entire site"
    And I should be on the "home" page

# Userprofile exists
  Scenario: Userprofile already exists
    Given I login with "user1@example.com" and "myweakpassword"
    When I go to the "home" page
    Then I should see "You are currently logged in as Jane Doe, user1@example.com"

  Scenario: Navigate to user profile creation page when profile already exists
    Given I login with "user1@example.com" and "myweakpassword"
    When I go to the "create_userprofile" page
    Then I should be on the "home" page
    Then I should see "You are currently logged in as Jane Doe, user1@example.com"

