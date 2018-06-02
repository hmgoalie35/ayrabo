Feature: Contact us page
  As someone browsing the site for contact info
  So that I can contact the creator(s) of the site
  I want to be able to contact the creator(s) of the site

  Scenario: View contact info
    Given I am on the "home" page
    When I press "contact_us"
    Then I should be on the "contact_us" page
    And I should see "Contact Us"
    And I should see "Harris Pittinsky"
    And I should see "harris@pittinsky.com"
