Feature: User role combined with address and court finding

Tests:
- [ ] When user is plaintiff and address is in state
- [ ] When user is plaintiff and address is out of state
- [ ] When user is defendant and address is in state
- [ ] When user is defendant and address is out of state

Scenario: In-state user is plaintiff and picks court
  Given I start the interview
  When I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "201 555-0123" in the "Mobile number" field
  Then I continue to the next page
  Then I type "112 Southampton St" in the "Street address" field
  Then I type "1" in the "Unit" field
  Then I type "Boston" in the "City" field
  Then I select the "Iowa" option from the "State" choices
  Then I type "02118" in the "Zip" field
