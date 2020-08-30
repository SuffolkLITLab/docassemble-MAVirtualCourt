Feature: Intro screen behaves as expected

Interview loads has already been tested.
Being extra thorough thinking about what I know we'll need in the future.

Tests:
- [x] ID
- [x] Custom title text should appear
- [x] Terms of use link set to open new window to the right address
- [x] Terms of use link address works
- [x] Accept terms starts as unchecked
- [ ] Can't continue if don't check checkbox
- [ ] Validation message if try to continue without checking checkbox
- [ ] Can continue if check checkbox
- [ ] Green words/help text

Alternative code tests (How to go about this?):
- [ ] If custom title text is not defined, placeholder text should appear

Scenario: Intro page should open
  Given I start the interview
  Then the question id should be "question-basic-questions-intro-screen"

Scenario: Text needing customization should appear
  Given I start the interview
  Then I should see the phrase "Shared content tests: Mass Access Project"

Scenario: Terms link should open correctly
  Given I start the interview
  Then I should see link "terms of use"
  Then the link "terms of use" should lead to "https://massaccess.suffolklitlab.org/privacy/"
  Then the link "terms of use" should open a working page
  Then the link "terms of use" should open in a new window

Scenario: Accept terms starts as unchecked
  Given I start the interview
  Then the checkbox with "I accept" is unchecked
