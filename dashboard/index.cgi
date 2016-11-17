#!/usr/bin/ruby

require_relative "html"
require_relative "../config_defaults"
require "csv"
require "cgi"
require 'cgi/session'
$cgi = CGI.new
$session = CGI::Session.new($cgi)

h = HTML.new("Dashboard")

if $cgi.include?("refresh")
	time = $cgi["refresh"].to_i == 0 ? 60 : $cgi["refresh"].to_i
	h.add_html_head("<meta http-equiv='refresh' content='#{time}'>")
end

h.add_css("dashboard.css")

h << <<HEAD
<div id="head">
<img src='mgm-sp-logo.png' id="logo"></img>
<span style="padding-left:2em" class="green">
Dashboard
</span>
</div>
HEAD


timewidget = <<CONTENT
<div class='widget'>
<h1>Current Time</h1>
<div id="txt"></div>
</div>
CONTENT
h.add_script <<TIMEWIDGET
function startTime() {
    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    var s = today.getSeconds();
    m = checkTime(m);
    s = checkTime(s);
    document.getElementById('txt').innerHTML =
    h + ":" + m + ":" + s;
    var t = setTimeout(startTime, 500);
}
function checkTime(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
    return i;
}
$(document).ready(startTime);
TIMEWIDGET

h << timewidget


h.add_head_script("jquery-2.2.3.min.js")

h << <<MAILWIDGET


<!-- BEGIN MAIL WIDGET -->
MAILWIDGET
h.add_script_file("mail.js")

h << <<MAILWIDGET
<div class='widget'>
<h1>New Mail</h1>
<div id='inbox'>No new Mail</div>
</div>
MAILWIDGET
#h.add_script_file("http://mail.#{$conf.domain}/api/mail.cgi?jsonp=updateMail")

h << "<!-- END MAIL WIDGET -->"

h << "\n"*3

h << <<WEATHERWIDGET
<!-- BEGIN WEATHER WIDGET -->
<div class='widget'>
<h1>Weather for #{$conf.location}</h1>
<div id='weather'></div>
</div>
WEATHERWIDGET
h.add_script_file("jquery.simpleWeather.min.js")
h.add_script <<JS
$(document).ready(function() {
  $.simpleWeather({
    location: '#{$conf.location}',
    woeid: '',
    unit: 'c',
    success: function(weather) {
      html = '<h2><i class="icon-'+weather.code+'"></i> '+weather.temp+'&deg;'+weather.units.temp+'</h2>';
      html = '<h2><i class="icon-'+weather.code+'"></i>'+weather.temp+'&deg;'+weather.units.temp+'<img style="vertical-align:middle; display:inline-block; height:3em; margin-left: 0.3em" src="'+weather.forecast[0].image+'"></img></h2>';

      html += '<ul><li>'+weather.city+', '+weather.region+'</li>';
      html += '<li class="currently">'+weather.currently+'</li>';
      html += '<li>'+weather.wind.direction+' '+weather.wind.speed+' '+weather.units.speed+'</li></ul>';
  
      $("#weather").html(html);
    },
    error: function(error) {
      $("#weather").html('<p>'+error+'</p>');
    }
  });
});
JS
h << "<!-- END WEATHER WIDGET -->"


h << <<TIMEWIDGET


<!-- BEGIN TIME WIDGET -->
TIMEWIDGET

h << <<TIMEWIDGET
<div class='widget'>
<h1>Today's Schedule</h1>
<div id='calendar'></div>
</div>
TIMEWIDGET
h.add_css("fullcalendar/fullcalendar.min.css")
h.add_script_file("fullcalendar/moment.min.js")
h.add_script_file("fullcalendar/fullcalendar.min.js")
h.add_script_file("fullcalendar/locale/de.js")
h.add_script <<JS
$(document).ready(function() {
	$('#calendar').fullCalendar({
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'agendaWeek,agendaDay,listWeek'
		},
		defaultView: 'agendaDay',
		navLinks: false, // can click day/week names to navigate views
		editable: false,
		eventLimit: true, // allow "more" link when too many events
		nowIndicator: true,
		slotDuration: '00:30:00',
		events: "events.json"
	});
});
JS

h << "<!-- END TIME WIDGET -->"

h.out($cgi)
