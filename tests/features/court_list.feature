Feature: Only allowed courts are listed

- [x] Exclusion of Superior Court

Test interview will have to be modified to allow this
- [ ] Exclusion of District Court
- [ ] Exclusion of Boston Municipal Court
- [ ] Exclusion of Land Court
- [ ] Exclusion of Juvenile Court
- [ ] Exclusion of Probate and Family Court
- [ ] Exclusion of Housing Court
- [ ] Inclusion of all courts

Scenario: All except Superior Court
  Given I start the interview
  When I tap the option with the text "I accept"
  Then I tap the button "Next"
  Then I type "201 555-0123" in the "Mobile number" field
  Then I tap the button "Next"
  Then I type "Ulli" in the "First Name" field
  Then I type "User" in the "Last Name" field
  Then I tap the button "Next"
  Then I tap the button "No"
  Then I type "112 Southampton St" in the "Street address" field
  Then I type "1" in the "Unit" field
  Then I type "Boston" in the "City" field
  Then I select the "Massachusetts" option from the "State" choices
  Then I type "02118" in the "Zip" field
  Then I tap the button "Next"
  Then I tap the "Starting a new case" option
  Then I tap the button "Next"
  Then I tap the button "Yes"
  Then I tap the option with the text "Business or organization"
  Then I type "Defendant LLC" in the "Name of organization or business" field
  Then I tap the button "Next"
  Then the question id should be "choose a court (courts matching provided address were found)"
  Then I should not see the phrase "Superior Court"
  Then I should see the phrase "District Court"
  Then I should see the phrase "Boston Municipal Court"
  Then I should see the phrase "Land Court"
  Then I should see the phrase "Juvenile Court"
  Then I should see the phrase "Probate and Family Court"
  Then I should see the phrase "Housing Court"
