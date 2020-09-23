const { When, Then, And, Given, After, AfterAll, setDefaultTimeout } = require('cucumber');
const { expect } = require('chai');
const puppeteer = require('puppeteer');
const interviewConstants = require('../../interview-constants');
const scope = require('./scope');

/* Of Note:
- We're using `*=` because sometimes da text has funny characters in it that are hard to anticipate

*/


/* TODO:
1. 'choice' to be any kind of choice - radio, checkbox,
    dropdown, etc. Have to research the different DOM for each
1. 'choice' to have a more specific way to access each item. For
    example, for a list collect or other things that have multiple
    things with the same text on the page.
1. Figure out how to test allowing felxibility for coder. For example:
    there is placeholder text for the title of the form and if it's not
    defined, placeholder text should appear (though that behavior may
    bear discussion).
1. Add links to resources on:
   1. taps that trigger navigation need Promise.all: https://stackoverflow.com/a/60789449/14144258
       > I ran into a scenario, where there was the classic POST-303-GET
       and an input[type=submit] was involved. It seems that in this case, 
       the tap of the button won't resolve until after the associated form's 
       submission and redirection, so the solution was to remove the waitForNavigation, 
       because it was executed after the redirection and thus was timing out.

       I think Promise.all is what's taking care of these situations.
   1. Listening for `targetchanged` or changed URL
   1. Listening for responses

Should post example of detecting new page/no new page on submit when there
is a DOM change that you can detect. I suspect no request is
being sent, but I could be wrong. Haven't yet figured out how
to detect that.

regex thoughts: https://stackoverflow.com/questions/171480/regex-grabbing-values-between-quotation-marks
*/


const INTERVIEW_URL = interviewConstants.INTERVIEW_URL;
setDefaultTimeout(120 * 1000);

let device_touch_map = {
  mobile: 'tap',
  pc: 'click',
};

Given(/I start the interview[ on ]?(.*)/, async (optional_device) => {
  scope.click_type = device_touch_map;  // changing vocab

  // If there is no browser open, start a new one
  if (!scope.browser) {
    scope.browser = await scope.driver.launch({ headless: !process.env.DEBUG });
  }

  if (!scope.page) {
    scope.page = await scope.browser.newPage();
    scope.page.setDefaultTimeout(120 * 1000)
  }

  // Let developer pick mobile device if they want to
  // TODO: Add 'phone' and 'computer' and 'desktop'?
  if (optional_device && optional_device.includes( 'mobile' )) {
    await scope.page.setUserAgent("Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36");
    scope.device = 'mobile';
  } else {
    await scope.page.setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36");
    scope.device = 'pc';
  }

  // Then go to the given page
  await scope.page.goto(INTERVIEW_URL, {waitUntil: 'domcontentloaded'});
  // This shouldn't be needed, but I think it may help with the ajax
  // requests. Might not solve all race conditions.
  await scope.page.waitForSelector('#daMainQuestion');
  // I've seen stuff take an extra moment or two. Shame to have it everywhere
  await scope.afterStep(scope, {waitForTimeout: 200});
});

//#####################################
//#####################################
// Passive/Observational
//#####################################
//#####################################

// Need to see if it's possible to remove the need for this on most occasions
When(/I wait (\d+) seconds?/, async (seconds) => {
  await scope.afterStep(scope, {waitForTimeout: (seconds * 1000)});
});

When("I do nothing", async () => {
  /* Here to make writing tests more comfortable. */
  await scope.afterStep(scope);
});

Then('I should see the phrase {string}', async (phrase) => {
  /* In Chrome, this `innerText` gets only visible text */
  const bodyText = await scope.page.$eval('body', elem => elem.innerText);
  expect(bodyText).to.contain(phrase);

  await scope.afterStep(scope);
});

Then('I should see the link {string}', async (linkText) => {
  let [link] = await scope.page.$x(`//a[contains(text(), "${linkText}")]`);
  expect(link).to.exist;

  await scope.afterStep(scope);
});

// TODO: Switch to getting the id and then checking it against the argument
//     which will make for more useful test error messages.
Then('the question id should be {string}', async (question_id) => {
  /* Looks for a santized version of the question id as it's written
  *     in the .yml. docassemble:
  *     re.sub(r'[^A-Za-z0-9]+', '-', interview_status.question.id.lower())
  *  
  *  WARNING: Does not handle actual html `class` name on page
  */
  clean_id = question_id.toLowerCase().replace(/[^A-Za-z0-9]+/g, '-');
  question_class = 'question-' + clean_id;
  const element = await scope.page.waitFor('body.' + question_class);
  expect(element).to.exist;

  await scope.afterStep(scope);
});

Then('an element should have the id {string}', async (id) => {
  const element = await scope.page.waitFor('#' + id);
  expect(element).to.exist;

  await scope.afterStep(scope);
});

Then('I will be told an answer is invalid', async () => {
  let error_message_elem = await Promise.race([
      scope.page.waitForSelector('.alert-danger'),
      scope.page.waitForSelector('.da-has-error'),
    ]);
  expect( error_message_elem ).to.exist;

  await scope.afterStep(scope);
});

Then(/the checkbox with "([^"]+)" is (checked|unchecked)/, async (label_text, expected_status) => {
  /* Tests whether the first "checkbox" label "containing"
  *    the "label text" is of the "checked" status given.
  *    Anything more complex will be a future feature.
  * 
  * "checkbox": label that contains checkbox-like behavior.
  */
  let checkbox = await scope.page.waitFor( `label[aria-label*="${ label_text }"]` );
  let is_checked = await scope.page.evaluate( async(elem, label_text) => {
    return elem.getAttribute('aria-checked') === 'true';
  }, checkbox, label_text );

  let what_it_should_be = expected_status === 'checked';
  expect( is_checked ).to.equal( what_it_should_be );

  await scope.afterStep(scope);
});

Then('I arrive at the next page', async () => {
  /* Tests for detection of url change from button or link tap.
  *    Can other things trigger navigation? Re: other inputs things
  *    like 'Enter' acting like a click is a test for docassemble */
  expect( scope.navigated ).to.be.true;
  await scope.afterStep(scope);
});

Then(/I (don't|can't) continue/, async (unused) => {
  /* Tests for detection of url change from button or link tap.
  *    Can other things trigger navigation? Re: other inputs things
  *    like 'Enter' acting like a click is a test for docassemble */
  expect( scope.navigated ).to.be.false;
  await scope.afterStep(scope);
});

Then(/the link "([^"]+)" should lead to "([^"]+)"/, async (linkText, expected_url) => {
  let [link] = await scope.page.$x(`//a[contains(text(), "${linkText}")]`);
  
  let prop_obj = await link.getProperty('href');
  let actual_url = await prop_obj.jsonValue();
  expect( actual_url ).to.equal( expected_url );
  
  await scope.afterStep(scope);
});

Then(/the link "([^"]+)" should open in (a new window|the same window)/, async (linkText, which_window) => {
  let [link] = await scope.page.$x(`//a[contains(text(), "${linkText}")]`);

  let prop_obj = await link.getProperty('target');
  let target = await await prop_obj.jsonValue();
  
  let should_open_a_new_window = which_window === 'a new window';
  let opens_a_new_window = target === '_blank';
  let hasCorrectWindowTarget =
    ( should_open_a_new_window && opens_a_new_window )
    || ( !should_open_a_new_window && !opens_a_new_window );

  expect( hasCorrectWindowTarget ).to.be.true;
  
  await scope.afterStep(scope);
});



//#####################################
//#####################################
// Actions
//#####################################
//#####################################

//#####################################
// Possible navigation
//#####################################

// Consider people wanting to use this for an in-interview page
// Also consider 'the link url "..." should open...'?
Then(/the link "([^"]+)" should open a working page/, async (linkText) => {
  let [link] = await scope.page.$x(`//a[contains(text(), "${linkText}")]`);
  let prop_obj = await link.getProperty('href');
  let actual_url = await prop_obj.jsonValue();
  
  let linkPage = await scope.browser.newPage();
  let response = await linkPage.goto(actual_url, {waitUntil: 'domcontentloaded'});
  expect( response.ok() ).to.be.true;
  linkPage.close()
  
  await scope.afterStep(scope);
});


When(/I tap the (button|link) "([^"]+)"/, async (elemType, phrase) => {
  /* Taps a button and stores or reacts to what happens:
  *    navigation, validation error, page error, just a click. */
  let start_url = await scope.page.url()

  let elem;
  if (elemType === 'button') {
    [elem] = await scope.page.$x(`//button/span[contains(text(), "${phrase}")]`);
  } else {
    [elem] = await scope.page.$x(`//a[contains(text(), "${phrase}")]`);
  }

  if (elem) {
    result = await Promise.race([
      Promise.all([
        // Click with no navigation will end immediately
        elem[ scope.click_type[ scope.device ]](),
        scope.page.waitForNavigation({waitUntil: 'domcontentloaded'}),
      ]),
      scope.page.waitForSelector('.alert-danger'),
      scope.page.waitForSelector('.da-has-error'),
      scope.page.waitForSelector('#da-retry'),  // Actual error
    ]);
  }

  let end_url = await scope.page.url();

  await scope.afterStep(scope, {waitForShowIf: true, navigated: start_url !== end_url});
});

//#####################################
// UI element interaction
//#####################################

When('I tap the defined text link {string}', async (phrase) => {
  /* Not sure what 'defined' means here. Maybe for terms? */
  const [link] = await scope.page.$x(`//a[contains(text(), "${phrase}")]`);
  if (link) {
    await link[ scope.click_type[ scope.device ]]();
  } else {
    // Is this needed or will it cause an error anyway?
    if (process.env.DEBUG) {
      await scope.page.screenshot({ path: './error.jpg', type: 'jpeg', fullPage: true });
    }
    throw `No link with text ${phrase} exists.`;
  }

  await scope.afterStep(scope, {waitForShowIf: true});
});

// TODO: Develop more specific choice selection
// Then(/the choice with "([^"]+)" of the "([^"]+)" options is (selected|unselected)/,
//   async (choice_label, field_label, expected_status) => {
//     let note = 'This is more annoying to implement even though it would let you get more specific.'
//   }
// );

When(/I tap the option with the text "([^"]+)"/, async (label_text) => {
  /* taps the first element with the label "containing" the "label text".
  *    Very limited. Anything more is a future feature.
  * 
  * May switch to using the below instead - almost same code, but
  *    its text has to match exactly and it turns out taping labels
  *    works for more than one thing.
  */
  let choice = await scope.page.waitFor( `label[aria-label*="${ label_text }"]` );
  await choice[ scope.click_type[ scope.device ]]();

  await scope.afterStep(scope, {waitForShowIf: true});
});

When('I tap the {string} option', async (label_text) => {
  /* taps the first label with the exact `label_text`.
  *    Very limited. Anything more is a future feature.
  */
  // Page has loaded? Should not wait?
  let choice = await scope.page.waitForSelector( `label[aria-label*="${ label_text }"]` );
  await choice[ scope.click_type[ scope.device ]]();

  await scope.afterStep(scope, {waitForShowIf: true});
});

// TODO: Should it be 'containing', or should it be exact? Might be better to be exact.
// TODO: Should we have a test just for the state of MA to be selected? Much easier... Or states in general
When('I select the {string} option from the {string} choices', async (choice_text, label_text) => {
  /* Selects the option having exactly the text `choice_text`
  * in the <select> with the label "containing" the `label text`.
  *    Finding one out of a bunch is a future feature.
  * 
  * Note: `page.select()` is the only way to tap on an element in a <select>
  */
  // Make sure ajax is finished getting the items in the <select>
  await scope.page.waitForSelector('option');

  // The <label> will have the `id` for the <select> we're looking for
  let [label] = await scope.page.$x(`//label[contains(text(), "${label_text}")]`);
  let select_id = await scope.page.evaluate(( label ) => {
    return label.getAttribute('for');
  }, label);

  // Get the actual option to pick. Can't use `value` here unfortunately as it doesn't reflect the text
  // Waiting for possible ajax request.
  let select = await scope.page.waitForSelector(`#${ select_id }`);

  // Get the option with the exactly matching text
  // Might want to make this flexible for reasons noted at the top of the script
  let option_value = await scope.page.evaluate(( select_elem, option_text ) => {
    let options = select_elem.querySelectorAll( 'option' );
    for ( let option of options ) {
      if ( option.textContent === option_text ) { return option.getAttribute('value'); }
    }
    return null;
  }, select, choice_text);

  // No other way to tap on an element in a <select>
  await scope.page.select(`#${ select_id }`, option_value);

  await scope.afterStep(scope, {waitForShowIf: true});
});

// TODO: Develop more specific choice selection
// Then(/check the "([^"]+)" checkbox in the "([^"]+)" options/,
//   async (choice_label, field_label, expected_status) => {
//     let note = 'This is more annoying to implement even though it would let you get more specific.'
//   }
// );

Then('I type {string} in the {string} field', async (value, field_label) => {
  let id = await scope.getTextFieldId(scope, field_label);
  await scope.page.type( '#' + id, value );

  await scope.afterStep(scope, {waitForShowIf: true});
});



//#####################################
//#####################################
// After
//#####################################
//#####################################

After(async (scenario) => {
  if (scenario.result.status === "failed") {
    const name = scenario.pickle.name.replace(/[^A-Za-z0-9]/gi, '');
    await scope.page.screenshot({ path: `error-${name}.jpg`, type: 'jpeg', fullPage: true });
  }
  // If there is a browser window open, then close it
  if (scope.page) {
    await scope.page.close();
    scope.page = null;
  }
});

AfterAll(async () => {
  // If there is a browser open, then close it
  if (scope.browser) {
    await scope.browser.close();
  }
});
