module.exports = {
  canContinue: async function canContinue(scope) {
    /* See if there's a validation message instead of a
    *     page navigation when continue button is pressed.
    * 
    * Could use `this`, but I've found it can be confusing.
    */

    // Promise.any isn't defined in this context
    let winner = await Promise.race([
      scope.page.waitForSelector('.da-has-error'),
      Promise.all([
        scope.page[ scope.device_map[ scope.emulating ]]('button[type="submit"]'),
        scope.page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
      ])
    ]);

    return winner.constructor.name != 'ElementHandle';
  },
};