Feature: User role combined with address and court finding

Tests:
- [ ] When user is plaintiff and address is in state
- [ ] When user is plaintiff and address is out of state
- [ ] When user is defendant and address is in state
- [ ] When user is defendant and address is out of state

Scenario: User contact info page should exist
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "201 555-0123" in the "Mobile number" field
  Then I continue to the next page
