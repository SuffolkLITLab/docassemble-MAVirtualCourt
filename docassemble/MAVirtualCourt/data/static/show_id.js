$(document).on('daPageLoad', function(){
  let $qId = $( "#qId" );
  if ( $qId ) { $qId.html("<code>Page id: " + daQuestionID['id'] + "</code>"); }
});