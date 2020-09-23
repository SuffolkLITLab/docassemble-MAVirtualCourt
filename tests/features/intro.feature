Feature: Intro screen behaves as expected

Interview loads has already been tested.
Being extra thorough thinking about what I know we'll need in the future.

Tests:
- [x] ID
- [x] Custom title text should appear
- [x] Terms of use link set to open new window to the right address
- [x] Terms of use link address works
- [x] Accept terms starts as unchecked
- [x] Can't continue if don't check checkbox
- [x] Validation message if try to continue without checking checkbox
- [x] Can continue if check checkbox
- [ ] Green words/help text exists (not sure needed)

Alternative code tests (How to go about this?):
- [ ] If custom title text is not defined, placeholder text should appear

Scenario: Intro page should open
  Given I start the interview
  Then the question id should be "basic questions intro screen"

Scenario: Text needing customization should appear
  Given I start the interview
  Then I should see the phrase "Shared content tests: Mass Access Project"

Scenario: Terms link should work
  Given I start the interview
  Then I should see the link "terms of use"
  Then the link "terms of use" should lead to "https://massaccess.suffolklitlab.org/privacy/"
  Then the link "terms of use" should open a working page
  Then the link "terms of use" should open in a new window

Scenario: Accept terms starts as unchecked
  Given I start the interview
  Then the checkbox with "I accept" is unchecked

Scenario: Can't continue without accepting terms
  Given I start the interview
  When I do nothing
  Then I can't continue
  Then I will be told an answer is invalid

Scenario: Can continue after accepting terms
  Given I start the interview
  When I click the option with the text "I accept"
  Then I continue to the next page
