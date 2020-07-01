/*
* Inserts quick exit button for sensitive interviews into
* the page header.
* 
* Will not be compatible with all browsers. JQuery doesn't
* offer that kind of support.
*/

$(document).on('daPageLoad', function(){
  let escaper = document.createElement( 'a' );
  escaper.setAttribute( 'class', 'escape btn btn-danger' );
  escaper.setAttribute( 'href', 'https://google.com' );
  escaper.innerHTML = 'Escape';

  // Add to navbar
  let after = document.getElementById( 'damobile-toggler' );
  after.parentNode.insertBefore( escaper, after );
});
