const chai = require('chai');
const putils = require('./puppeteer-utils');
const interviewConstants = require('./interview-constants.js');  // interview urls, etc.

// Tell Chai that we want to use the expect syntax
const expect = chai.expect;

// useful cheat sheet for assertions: https://devhints.io/chai
// run tests with "npm run test"

const TEST_URL = `${interviewConstants.INTERVIEW_URL}`;

describe('209A url', () => {
  let page, browser;
  before(async () => {
    ({page, browser} = await putils.initPuppeteer());
  });

  after((done) => {
    browser.close();
    done();
  });

  it('opens the interview', async () => {
    let resp = await page.goto(TEST_URL, {waitUntil: 'domcontentloaded'});
    console.log('This is the TEST_URL:' + TEST_URL);  // If something is wrong, you can go see
    const questionIDElement = await page.$eval('.question-basic-questions-intro-screen', elem => elem.innerText);
    expect(questionIDElement).to.exist;
  });
});
