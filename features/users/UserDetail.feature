Feature: User profile
  As a user,
  I want to be able to view another user's profile

  Background: Users exist
    Given The following confirmed user account exists
      | id | first_name | last_name | email              | password       | create_userprofile |
      | 1  | John       | Doe       | user@ayrabo.com    | myweakpassword | false              |
      |    | Michael    | Scott     | michael@ayrabo.com | myweakpassword | true               |
    And The following userprofile exists for "user@ayrabo.com"
      | gender | birthday   | height | weight | timezone   |
      | male   | 1996-02-12 | 5' 7"  | 150    | US/Eastern |
    And I login with "michael@ayrabo.com" and "myweakpassword"

  Scenario: View profile information
    Given I am on the "users:detail" page with kwargs "pk=1"
    Then I should see "John Doe"
    And I should see "Gender"
    And I should see "Male"
    # Not worth the headache to check the value for age here
    And I should see "Age"
    And I should see "Birthday"
    And I should see "Feb. 12, 1996"
    And I should see "Height"
    And I should see "5' 7""
    And I should see "Weight"
    And I should see "150"
