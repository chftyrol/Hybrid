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

function updateUI() { // define this function, we'll need it a lot.
  $.getJSON('/hsm/measure_status', function(data) { // Query the server for the status of all services.
    $.each(data.status_all, function(key, val) { // cicle over all services. the server returns a string of qualifiers for the service, such as "inactive, enabled".
      var valarr = val.split(' '); // split that string into an array.
      var vallen = valarr.length;
      var curstatus = '';
      // hide all icons, they will be shown contextually.
      $('a.' + key + '.start.icon').hide();
      $('a.' + key + '.restart.icon').hide();
      $('a.' + key + '.navigate.icon').hide();
      $('a.' + key + '.stop.icon').hide();
      $('a.' + key + '.disable.icon').hide();
      $('a.' + key + '.enable.icon').hide();
      for(i = 0; i < vallen; i++) { // cycle over the qualifiers and set status and icons accordingly.
        if(valarr[i] == "inactive") {
          curstatus += '<p class="status inactive">✕ Inactive</p>';
          $('a.' + key + '.start.icon').show();
        }
        else if(valarr[i] == "active") {
          curstatus += '<p class="status active">✔ Active</p>';
          $('a.' + key + '.stop.icon').show();
          $('a.' + key + '.restart.icon').show();
          $('a.' + key + '.navigate.icon').show();
        }
        else if(valarr[i] == "disabled") {
          curstatus += '<p class="status disabled">✕ Disabled</p>';
          $('a.' + key + '.enable.icon').show();
        }
        else if(valarr[i] == "enabled") {
          curstatus += '<p class="status enabled">✔ Enabled</p>';
          $('a.' + key + '.disable.icon').show();
        }
        else if(valarr[i] == "failed") {
          curstatus += '<p class="status failed">X Failed</p>';
          $('a.' + key + '.restart.icon').show();
        }
        else if(valarr[i] == "unknown") {
          curstatus += '<p class="status inactive">✕ Inactive</p>';
          $('a.' + key + '.start.icon').show();
        }
        else if(valarr[i] == "unavailable") {
          curstatus += '<p class="status failed">✕ Unavailable</p>';
        }
        else {
          curstatus += '<p class="status unknown">Unknown</p>';
        }
      }
      // set the status of each service
      $('div.' + key + '.status').html(curstatus);
    });
  });
}

$(function() { // run when the page has finished loading: it's a special jquery shorthand.
  $('div.buttoncontainer > a').bind('click', function() { // bind the icon buttons to their respective actions.
    var serviceid = $(this).attr('class').split(' ')[0];
    var action = $(this).attr('class').split(' ')[1];
    $('div.' + serviceid + '.status').html('<p class="status loading">Working...</p>');
    $.get('/hsm/perform_action', { who:serviceid, what:action }, function(data){
      if(action == 'navigate'){ 
        window.location.href = window.location.protocol + '//' + window.location.hostname + ':' + data;
      }
    })
      .always(updateUI);
  });
  
  // when everything has loaded run updateUI()
  updateUI();
});
