Feature: User role combined with address and court finding

Tests:
- [x] When user is defendant and address is in-state (What court is your case in?)
- [x] When user is plaintiff and address is in-state (What court do you want to file in?)
- [ ] When user is defendant and address is out of state (no map)
- [ ] When user is plaintiff and address is out of state (no map)

Scenario: In-state defendant picks a court
  Given I start the interview
  Then I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "201 555-0123" in the "Mobile number" field
  Then I continue to the next page
  Then I type "Ulli" in the "First Name" field
  Then I type "User" in the "Last Name" field
  Then I continue to the next page
  Then I click the button "No"
  Then I type "112 Southampton St" in the "Street address" field
  Then I type "1" in the "Unit" field
  Then I type "Boston" in the "City" field
  Then I select the "Massachusetts" option from the "State" choices
  Then I type "02118" in the "Zip" field
  Then I continue to the next page
  Then I pick the "Responding to a case" option
  Then I continue to the next page
  Then I check the "Business or organization" checkbox
  Then I type "A Plaintiff" in the "Name of organization or business" field
  Then I continue to the next page
  Then the question id should be "matching courts choose a court"
  Then I should see the phrase "What court is your case in?"

Scenario: In-state plaintiff picks a court
  Given I start the interview
  Then I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "201 555-0123" in the "Mobile number" field
  Then I continue to the next page
  Then I type "Ulli" in the "First Name" field
  Then I type "User" in the "Last Name" field
  Then I continue to the next page
  Then I click the button "No"
  Then I type "112 Southampton St" in the "Street address" field
  Then I type "1" in the "Unit" field
  Then I type "Boston" in the "City" field
  Then I select the "Massachusetts" option from the "State" choices
  Then I type "02118" in the "Zip" field
  Then I continue to the next page
  Then I pick the "Starting a new case" option
  Then I continue to the next page
  Then the question id should be "matching courts choose a court"
  Then I should see the phrase "What court do you want to file in?"

Scenario: Out of state defendant picks a court
  Given I start the interview
  Then I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "201 555-0123" in the "Mobile number" field
  Then I continue to the next page
  Then I type "Ulli" in the "First Name" field
  Then I type "User" in the "Last Name" field
  Then I continue to the next page
  Then I click the button "No"
  Then I type "1600 Pennsylvania Avenue" in the "Street address" field
  Then I type "Washington" in the "City" field
  Then I select the "District of Columbia" option from the "State" choices
  Then I type "20500" in the "Zip" field
  Then I continue to the next page
  Then I pick the "Responding to a case" option
  Then I continue to the next page
  Then I check the "Business or organization" checkbox
  Then I type "A Plaintiff" in the "Name of organization or business" field
  Then I continue to the next page
  Then the question id should be "empty matches choose a court"
  Then I should see the phrase "What court is your case in?"

Scenario: Out of state plaintiff picks a court
  Given I start the interview
  Then I check the "I accept" checkbox
  Then I continue to the next page
  Then I type "201 555-0123" in the "Mobile number" field
  Then I continue to the next page
  Then I type "Ulli" in the "First Name" field
  Then I type "User" in the "Last Name" field
  Then I continue to the next page
  Then I click the button "No"
  Then I type "1600 Pennsylvania Avenue" in the "Street address" field
  Then I type "Washington" in the "City" field
  Then I select the "District of Columbia" option from the "State" choices
  Then I type "20500" in the "Zip" field
  Then I continue to the next page
  Then I pick the "Starting a new case" option
  Then I continue to the next page
  Then the question id should be "empty matches choose a court"
  Then I should see the phrase "What court do you want to file in?"
