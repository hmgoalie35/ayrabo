Feature: About us
  As someone browsing the site for info on the developers
  So that I can learn more about the developers
  I want to be able to see info on each developer

  Scenario: View about us info
    Given I am on the "home" page
    When I press "about_us"
    Then I should be on the "about_us" page
    And I should see "About Us"
    And I should see "Harris Pittinsky"
