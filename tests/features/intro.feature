Feature: Intro screen behaves as expected

Interview loads has already been tested.

Tests:
1. ID
1. Custom title text
1. Green words/help text
1. Terms of use link
1. Checkbox controls continuation

Scenario: Open the first page
  Given I start the interview
  Then the question id should be "question-basic-questions-intro-screen"
