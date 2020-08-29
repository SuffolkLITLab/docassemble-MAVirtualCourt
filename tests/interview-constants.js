const putils = require('./puppeteer-utils');

// Each repo has its own interview that it's testing
// We'll deal with multiple urls when it becomes an issue
const INTERVIEW_URL = `${putils.BASE_INTERVIEW_URL}%3Abasic_questions_tests.yml`;


module.exports = {
  INTERVIEW_URL,
};
