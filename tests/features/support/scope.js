module.exports = {
  tryContinue: async function tryContinue(scope) {
    /* See if there's a validation message instead of a
    *     page navigation when continue button is pressed.
    * 
    * Could use `this`, but I've found it can be confusing.
    * 
    * ISSUE MADE ON PUPPETEER for async hang: https://github.com/puppeteer/puppeteer/issues/6379
    */

    // // Causes hang at end of successful tests
    // let original_url = await scope.page.url();

    // Also causes hang at end of successful tests
    let target_changed = false;
    await scope.browser.once('targetchanged', function() { target_changed = true; return; });

    // Promise.any isn't defined in this context
    let winner = await Promise.race([
      scope.page.waitForSelector('.alert-danger'),  // Not sure this is useful with url detection now
      scope.page.waitForSelector('.da-has-error'),
      Promise.all([
        scope.page[ scope.device_map[ scope.emulating ]]('button.btn-primary[type="submit"]'),
        scope.page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
      ])
    ]);

    // // Success still doesn't exit
    // await scope.browser.removeAllListeners();

    // ISSUE MADE ON PUPPETEER: https://github.com/puppeteer/puppeteer/issues/6379
    // This solves the hang, but I don't like handling race conditions this way
    await scope.page.waitFor(10);

    let navigation_won = winner.constructor.name != 'ElementHandle';
    // let current_url = await scope.page.url();
    // let url_changed = original_url != current_url;
    // return navigation_won && url_changed;

    return navigation_won && target_changed;
  },

  getTextFieldId: async function getTextFieldId(scope, field_label) {
    // make sure at least one is on screen
    await scope.page.waitFor('div.da-field-container-datatype-text label');

    let field_id = await scope.page.$$eval('div.da-field-container-datatype-text label', (elements, field_label) => {
      let elems_array = Array.from( elements );
      for ( let elem of elems_array ) {
        if (( elem.innerText ).includes( field_label )) {
          return elem.getAttribute( 'for' );
        }
      }  // End for labels

    }, field_label);

    return field_id;
  },
};
