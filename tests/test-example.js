const chai = require('chai');
const putils = require('./puppeteer-utils');

// Tell Chai that we want to use the expect syntax
const expect = chai.expect;

// useful cheat sheet for assertions: https://devhints.io/chai
// run tests with "npm run test"

const FILENAME_209A = `209a_package.yml`;  // May become larger scope variable for multiple tests
const TEST_URL = `${putils.BASE_INTERVIEW_URL}%3A${FILENAME_209A}`;

describe('Making sure we can log into Docassemble playground', () => {
  it('login and get to the interviews page', async () => {
    let {page, browser} = await putils.login();
    expect(page).to.exist;
    expect(browser).to.exist;
    expect(page.url()).to.include('/interviews');
    const bodyText = await page.$eval('body', elem => elem.textContent);
    expect(bodyText).to.have.string('You have signed in successfully.');
    await browser.close();
  });
});


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
