Feature: User profiles
  As a user,
  I want to be able to completely fill out my profile

  Background: User account exists
    Given The following confirmed user account exists
      | first_name | last_name | email           | password       | create_userprofile |
      | John       | Doe       | user@ayrabo.com | myweakpassword | false              |
    And The following sport exists "Ice Hockey"
    And The following sport exists "Baseball"
    And The following waffle switch exists
      | name                | active |
      | sport_registrations | True   |
    And I login with "user@ayrabo.com" and "myweakpassword"

  Scenario: Useful information displayed to user
    Given I am on the "account_complete_registration" page
    Then I should see "Complete Your Account Registration"
    And I should see "Players, coaches and managers will be granted team specific access by an organization admin."

  # Userprofile does not exist, create profile page
  Scenario: Prompted to fill out user profile after logging in for the first time
    Given I go to the "home" page
    Then I should be on the "account_complete_registration" page
    And I should see "Complete Your Account Registration"
    And I should see "Players, coaches and managers will be granted team specific access by an organization admin."

  Scenario: Redirected when trying to navigate to new sport registration page when userprofile not complete
    Given I go to the "sports:register" page
    Then I should be on the "account_complete_registration" page

  Scenario: Submit invalid form
    Given I am on the "account_complete_registration" page
    When I select "male" from "id_user_profile-gender"
    And I fill in "id_user_profile-height" with "5' 7"
    And I fill in "id_user_profile-weight" with "130"
    And I select "February" from "id_user_profile-birthday_month"
    And I select "31" from "id_user_profile-birthday_day"
    And I select "2000" from "id_user_profile-birthday_year"
    And I press "create_userprofile_btn"
    Then I should see "Invalid format, please enter your height according to the format below."
    And I should see "Please choose a valid date."

  Scenario: Submit valid form
    Given I am on the "account_complete_registration" page
    When I select "male" from "id_user_profile-gender"
    And I select "April" from "id_user_profile-birthday_month"
    And I select "4" from "id_user_profile-birthday_day"
    And I select "1994" from "id_user_profile-birthday_year"
    And I fill in "id_user_profile-height" with "5' 7""
    And I fill in "id_user_profile-weight" with "130"
    And I press "create_userprofile_btn"
    Then I should be on the "sports:register" page

    # See features/sports/NewSportRegistration.feature for the next set of tests
