 /* 
    @preserve

    This file is part of Hybrid.

    Hybrid is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Hybrid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Hybrid.  If not, see <http://www.gnu.org/licenses/>.
*/

var failed_attempts = 0;

function submitForm(url) {
  var username = $('#username').val();
  var password = $('#password').val();
  var salt = username + '-hybrid_server';

  // hash the password with sha256. The salt is username + '-hybrid_server'
  // it is not necessary to use KDFs here as they do not provide any further protection
  // a MITM attack here could just use the KDF value to authenticate (the hash logically becomes the password).
  // strong hashing with bcrypt is performed server side
  var hashbits = sjcl.hash.sha256.hash(password + salt);
  // get the hex dump from the bytes
  var hash = sjcl.codec.hex.fromBits(hashbits);
  // Make a {username: hash, "rememberme" : rememberme} dictionary
  var loginData = { };
  loginData[username] = hash;
  if($('#rememberme').is(':checked')){
    loginData['rememberme'] = 1; // true
  }
  else{
    loginData['rememberme'] = 0; // false
  }

  // Send it to the server for evaluation
  $.post(url, loginData, function(data){
    // On success, redirect to where the server tells us.
    window.location.href = data;
  }).fail(function(data){
    // On fail have a little bit of fun with the user.
    if(data.responseText == 'login failed'){
      failed_attempts++;
      // Transition to red login form with dark submit button
      $('#loginform, #username, #password, h2').animate({
        backgroundColor: "#a52929"
      }, 400);
      $('input.loginbutton').animate({
        backgroundColor: "#302921",
        color: "#ddd6ce"
      }, 400);
      if(failed_attempts < 3){
        $('h2').html('Login failed');
      }
      else if(failed_attempts < 5){
        $('h2').html('Go away!');
        }
      else{
        $('h2').html('Go fuck yourself (with a cactus)!');
      }
    }
  });
}
$(function(){
  // manage our custom checkbox animation
  $('#checkboxlabel').bind('click', function(){
    if ($('#rememberme').is(":checked")){
      // hide the cookie!
      $('input[type=checkbox] + label').animate({
        backgroundSize: "0px"
      }, 280);
    }
    else{
      // show the cookie :)
      $('input[type=checkbox] + label').animate({
        backgroundSize: "30px"
      }, 280);
    }
  });
});
