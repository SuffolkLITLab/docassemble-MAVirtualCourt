Feature: User contact info for the court

Tests:
- [x] ID
- [x] Can't continue without input
- [x] Get invalidation message without input
- [x] Input in mobile number will allow continuing
- [x] Input in other phone number will allow continuing
- [x] Input in email will allow continuing
- [ ] Input in "other ways" will allow continuing
- [ ] Green help text exists
- [ ] Help button exists

Scenario: User contact info page should exist
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  Then the question id should be "your contact information"

Scenario: Can't continue if gave no information
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  When I do nothing
  Then I can't continue
  
Scenario: Get invalidation message if gave no information
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  When I do nothing
  Then I can't continue
  Then I will be told an answer is invalid

Scenario: Giving a mobile number will allow the user to continue
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "201 555-0123" in the "Mobile number" field
  Then I continue to the next page

Scenario: Giving a mobile number will allow the user to continue
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "201 555-0123" in the "Other phone number" field
  Then I continue to the next page

Scenario: Giving a mobile number will allow the user to continue
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "user@example.com" in the "Email address" field
  Then I continue to the next page
