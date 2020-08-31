module.exports = {
  canContinue: async function canContinue(scope) {
    /* See if there's a validation message instead of a
    *     page navigation when continue button is pressed.
    * 
    * Could use `this`, but I've found it can be confusing.
    */
    let original_url = scope.page.url();
    // 'targetchanged' with `once` possibly causes cucumber to hang.
    // Explore in the future.

    // Promise.any isn't defined in this context
    let winner = await Promise.race([
      scope.page.waitForSelector('.alert-danger'),  // Not sure this is useful with url detection now
      scope.page.waitForSelector('.da-has-error'),
      Promise.all([
        scope.page[ scope.device_map[ scope.emulating ]]('button[type="submit"]'),
        scope.page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
      ])
    ]);

    let validation_message_won = winner.constructor.name != 'ElementHandle';
    let url_changed = original_url != scope.page.url();
    return validation_message_won && url_changed;
  },
};