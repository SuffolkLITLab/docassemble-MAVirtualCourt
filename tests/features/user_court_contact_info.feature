Feature: User contact info for the court

Tests:
- [x] ID
- [x] Can't continue without input
- [ ] Get invalidation message without input
- [ ] Green help text exists
- [ ] Help button exists

Scenario: User contact info page should exist
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  Then the question id should be "your contact information"

Scenario: Can't continue with no input
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  When I do nothing
  Then I can't continue
  