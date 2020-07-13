const puppeteerutils = require('./puppeteer-utils');

const setup = async () => {
  let {page, browser} = await puppeteerutils.login();
  try {
    await puppeteerutils.createProject(page);
    await puppeteerutils.installRepo(page);
  }
  catch (error) {
    console.log(error);
  }
  finally {
    browser.close();
  }
};

const takedown = async () => {
  let {page, browser} = await puppeteerutils.login();
  try {
    await puppeteerutils.deleteProject(page);
  }
  catch (error) {
    console.log(error);
  }
  finally {
    browser.close();
  }
};


module.exports = {setup, takedown};
