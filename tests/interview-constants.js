const putils = require('./puppeteer-utils');

// Each repo has its own interview that it's testing
// We'll deal with multiple urls when it becomes an issue
let filename = '209a_package';  // Easier to edit
const INTERVIEW_URL = process.env.INTERVIEW_URL || `${putils.BASE_INTERVIEW_URL}%3A${filename}.yml`;


module.exports = {
  INTERVIEW_URL,
};
