$(document).on('daPageLoad', function(){
  // I believe this is async. We won't rely on `await` for now -
  // it's less browser compatible.
  get_interview_variables( function( data ){
    var verText = ''
    if ( data.success && data.variables.package_version_number ) {
      verText = ', v' + data.variables.package_version_number;
    }
    $( "#qId" ).html( "<code>Page id: " + daQuestionID['id'] + verText + "</code>" );
  });
});
