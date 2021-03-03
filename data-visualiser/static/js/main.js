/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

$('#dataupload').change(function() {
    console.log(this.files[0].name)
    var lbl = document.getElementsByTagName('LABEL')[0];
    lbl.innerHTML = this.files[0].name;
});

$('#picture').hide(); // hide at beginning
$('#button').click(function(){
  $('#picture').show(); // show on button click
});