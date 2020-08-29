const { When, Then, And, Given, After, AfterAll, setDefaultTimeout } = require('cucumber');
const { expect } = require('chai');
const puppeteer = require('puppeteer');
const interviewConstants = require('../../interview-constants');
const scope = require('./scope');

const INTERVIEW_URL = interviewConstants.INTERVIEW_URL;
setDefaultTimeout(120 * 1000);

//regex thoughts: https://stackoverflow.com/questions/171480/regex-grabbing-values-between-quotation-marks

// -- Puppeteer specific steps from hello_world.feature

Given(/I start the interview/, async () => {
  // If there is no browser open, start a new one
  if (!scope.browser) {
    scope.browser = await scope.driver.launch({ headless: !process.env.DEBUG });
  }
  if (!scope.page) {
    scope.page = await scope.browser.newPage();
    scope.page.setDefaultTimeout(120 * 1000)
  }

  // Then go to the given page
  await scope.page.goto(INTERVIEW_URL, {waitUntil: 'domcontentloaded'});
});

// Need to see if it's possible to remove the need for this on most occasions
When(/I wait (\d+) seconds?/, async (seconds) => {
  await scope.page.waitFor(seconds * 1000);
});


async function findElemByText(elem, text) {
  await scope.page.waitForNavigation({waitUntil: 'domcontentloaded'});
  const elems = await scope.page.$$(elem);
  for (var i=0; i < elems.length; i++) {
    let elemText = await (await elems[i].getProperty('innerText')).jsonValue();
    if (elemText.includes(text)) {
      return elems[i];
    }
  }
  return null;
}

When(/I click the (button|link) "([^"]+)"/, async (elemType, phrase) => {
  let elem;
  if (elemType === 'button') {
    [elem] = await scope.page.$x(`//button/span[contains(text(), "${phrase}")]`);
  } else {
    [elem] = await scope.page.$x(`//a[contains(text(), "${phrase}")]`);
  }

  if (elem) {
    await Promise.all([
      elem.click(),
      scope.page.waitForNavigation({waitUntil: 'domcontentloaded'})
  ]);
  } else {
    if (process.env.DEBUG) {
      await scope.page.screenshot({ path: './error.jpg', type: 'jpeg' });
    }
    throw `No ${elemType} with text ${phrase} exists.`;
  }
});

When('I click the defined text link {string}', async (phrase) => {
  const [link] = await scope.page.$x(`//a[contains(text(), "${phrase}")]`);
  if (link) {
    await link.click();
  } else {
    if (process.env.DEBUG) {
      await scope.page.screenshot({ path: './error.jpg', type: 'jpeg' });
    }
    throw `No link with text ${phrase} exists.`;
  }
});

Then('the question id should be {string}', async (question_class) => {
  const element = await scope.page.waitFor('body.' + question_class);
  expect(element).to.exist;
});

Then('an element should have the id {string}', async (id) => {
  const element = await scope.page.waitFor('#' + id);
  expect(element).to.exist;
});

Then('I should see the phrase {string}', async (phrase) => {
  const bodyText = await scope.page.$eval('body', elem => elem.innerText);
  expect(bodyText).to.contain(phrase);
});

Then('I should see link {string}', async (linkText) => {
  let [link] = await scope.page.$x(`//a[contains(text(), "${linkText}")]`);
  expect(link).to.exist;
});

Then(/the link "([^"]+)" should lead to "([^"]+)"/, async (linkText, expected_url) => {
  let [link] = await scope.page.$x(`//a[contains(text(), "${linkText}")]`);
  
  let url_obj = await link.getProperty('href');
  let actual_url = await url_obj.jsonValue();
  expect( actual_url ).to.equal( expected_url );
});

Then(/the link "([^"]+)" should open a working page/, async (linkText) => {
  let [link] = await scope.page.$x(`//a[contains(text(), "${linkText}")]`);
  let url_obj = await link.getProperty('href');
  let actual_url = await url_obj.jsonValue();
  
  let linkPage = await scope.browser.newPage();
  let response = await linkPage.goto(actual_url, {waitUntil: 'domcontentloaded'});
  expect( response.ok() ).to.be.true;
  linkPage.close()
});

Then(/the link "([^"]+)" should open in (a new window|the same window)/, async (linkText, which_window) => {
  let [link] = await scope.page.$x(`//a[contains(text(), "${linkText}")]`);

  let target_obj = await link.getProperty('target');
  let target = await await target_obj.jsonValue();
  
  let should_open_a_new_window = which_window === 'a new window';
  let opens_a_new_window = target === '_blank';
  let hasCorrectWindowTarget =
    ( should_open_a_new_window && opens_a_new_window )
    || ( !should_open_a_new_window && !opens_a_new_window );

  expect( hasCorrectWindowTarget ).to.be.true;
});

After(async (scenario) => {
  if (scenario.result.status === "failed") {
    const name = scenario.pickle.name.replace(/[^A-Za-z0-9]/gi, '');
    await scope.page.screenshot({ path: `error-${name}.jpg`, type: 'jpeg' });
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