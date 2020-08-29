Feature: Intro screen behaves as expected

Interview loads has already been tested.

Tests:
1. ID
1. Custom title text
1. Green words/help text
1. Terms of use link set to open new window to the right address
1. Terms of use link address works
1. Checkbox controls continuation

Scenario: Intro page should open
  Given I start the interview
  Then the question id should be "question-basic-questions-intro-screen"

Scenario: Terms link should open correctly
  Given I start the interview
  Then I should see link "terms of use"
  Then the link "terms of use" should lead to "https://massaccess.suffolklitlab.org/privacy/"
  Then the link "terms of use" should open a working page
  Then the link "terms of use" should open in a new window
