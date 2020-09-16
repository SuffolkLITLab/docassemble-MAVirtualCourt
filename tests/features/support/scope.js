module.exports = {
  trySubmitButton: async function trySubmitButton(scope) {//, button_text) {
    /* See if there's a validation message instead of a
    *     page navigation when continue button is pressed.
    * 
    * Do all buttons on DA pages navigate? Not sure about that.
    * 
    * ISSUE MADE ON PUPPETEER REPO for async hang: https://github.com/puppeteer/puppeteer/issues/6379
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
        // scope.page[ scope.device_map[ scope.emulating ]](button_selector),
        scope.page[ scope.device_map[ scope.emulating ]]( 'button.btn-primary[type="submit"]' ),
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
    await scope.page.waitFor('label[class*="datext"]');

    let field_id = await scope.page.$$eval('label[class*="datext"]', (elements, field_label) => {
      let elems_array = Array.from( elements );
      for ( let elem of elems_array ) {
        if (( elem.innerText ).includes( field_label )) {
          return elem.getAttribute( 'for' );
        }
      }  // End for labels

    }, field_label);

    return field_id;
  },

  waitForShowIf: async function waitForShowIf(scope) {
    // If something might be hidden or shown, wait extra time to let it hide or show
    let showif = await scope.page.$('.dashowif');
    if ( showif ) {
      // console.log('showif exists');
      await scope.page.waitFor(500);
    }
  },
};
