Feature: Update account info
  As a user,
  I want to be able to update my account information (first name, last name, height, etc)

  Background: Users exist
    Given The following users exist
      | id | email           | first_name | last_name | password       | create_userprofile |
      | 1  | user@ayrabo.com | Jon        | Doe       | myweakpassword | false              |
    And The following userprofiles exist
      | username_or_email | gender | birthday | height | weight | timezone   |
      | user@ayrabo.com   | male   | today    | 6' 0"  | 200    | US/Eastern |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Navigate to user update page
    Given I am on the "users:detail" page with kwargs "pk=1"
    And I press "user-edit-link"
    Then I should be on the "users:update" page

  Scenario: Basic info shown to user
    Given I am on the "users:update" page
    Then I should see "Jon Doe"
    And I should see "Male"
    And I should see "200"
    And I should see "US/Eastern"

  Scenario: Navigate to sports tab
    Given I am on the "users:update" page
    When I press "tab-item-sports"
    # Should really be checking tab query param is `sports`, but for now this is fine
    Then I should be on the "users:detail" page with kwargs "pk=1"

  Scenario: Submit valid form
    Given I am on the "users:update" page
    And I fill in "id_user-first_name" with "John"
    And I fill in "id_user_profile-height" with "5' 7""
    And I press "user-update-btn"
    Then I should see "Your account information has been updated."
    And I should be on the "users:detail" page with kwargs "pk=1"
    And I should see "John"
    And I should see "5' 7""

  Scenario: Submit invalid form
    Given I am on the "users:update" page
    And I fill in "id_user_profile-height" with "5' 7"
    And I press "user-update-btn"
    Then I should see "Invalid format, please enter your height according to the format below."
    And I should be on the "users:update" page
