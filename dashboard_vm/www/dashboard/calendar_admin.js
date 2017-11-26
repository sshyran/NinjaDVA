/**
 * *******************************************************
 * Calendar admin JS
 *********************************************************
 * this script injects an admin interface for the calendar
 * to the dashboard
 *
 *  In case of problems/bugs/questions contact: robin.herrmann@mgm-sp.com
 */

$(document).ready(function() {
    "use strict";
    // add or remove hidden state on double click
    $("#hiddenadmin").dblclick(function() {
        // check whether admin widget is in DOM
        if (document.getElementById("admincalendar")) {
            gridster.remove_widget($("#admincalendar"));
            //remove editable mode
            //and reset event click handler to open the link
            $("#calendar").fullCalendar("option", {
                editable: false,
                eventClick: function(oCalendarEvent) {
                    return true;
                }
            });

            // if not, create it
        } else {
            //function enable save button
            var fnEnableSaveButton = function() {
                $("#calendarsave").removeAttr("disabled");
                $("#calendarcancel").removeAttr("disabled");
            };

            //function disable save button
            var fnDisableSaveButton = function() {
                $("#calendarsave").prop("disabled", true);
                $("#calendarcancel").prop("disabled", true);
            };

            //define save to server function
            var fnSaveToServer = function() {
                // get current calendar entries
                var aEvents = $("#calendar")
                    .fullCalendar("clientEvents")
                    .map(e => {
                        var result = {};
                        result["title"] = e.title;
                        result["start"] = e.start._i;
                        if (e.end) {
                            result["end"] = e.end._i;
                        }
                        if (e.url) {
                            result["url"] = e.url;
                        }
                        if (e.backgroundColor) {
                            result["backgroundColor"] = e.backgroundColor;
                        }
                        return result;
                    });

                // create and send the save request
                var oXhr = new XMLHttpRequest();
                oXhr.withCredentials = true; // is necessary because of the digest authentication currently used
                var oFormData = new FormData();
                var sUrl = "http://dashboard.mgmsp-lab.com/admin/update_schedule.cgi";
                oFormData.append("schedule", JSON.stringify(aEvents));
                oXhr.open("POST", sUrl);
                oXhr.send(oFormData);

                //disable save button
                fnDisableSaveButton();

                //remove edit form
                $("#admcaleventedit").remove();
            };

            // define event handler for drop and resize events
            var fnCalendarEventHandler = function(oCalendarEvent) {
                fnEnableSaveButton();
                $("#admcaleventedit").remove();
            };

            //enable save button on change of event
            $("#calendar").fullCalendar("option", {
                eventDrop: fnCalendarEventHandler,
                eventResize: fnCalendarEventHandler
            });

            // add calendar admin widget
            var calendarAdminWidget =
                '<div class="widget" id="admincalendar"><div>' +
                "<h1>Admin Calendar</h1>" +
                '<button type="button" id="calendarsave" disabled>Save to Server</button>' +
                '<button type="button" id="calendarcancel" disabled>Cancel</button>' +
                "<hr>" +
                '<button type="button" id="calendaraddevent">Add Event</button>' +
                "</div></div>";
            gridster.add_widget.apply(gridster, [calendarAdminWidget, 2, 3]);

            //enable calendar edit mode
            $("#calendar").fullCalendar("option", { editable: true });

            //set selection granularity to 15 min
            $("#calendar").fullCalendar("option", { snapDuration: "00:15:00" });

            // set clickhandler for calendar save button
            $("#calendarsave").click(function() {
                fnSaveToServer();
            });

            // set clickhandler for calendar cancel button
            $("#calendarcancel").click(function() {
                $("#calendar").fullCalendar("refetchEvents");
                fnDisableSaveButton();
            });

            //set click handler for calendar-events ==> edit event
            $("#calendar").fullCalendar("option", {
                eventClick: function(oCalendarEvent) {
                    //remove edit form if already rendered
                    if (document.getElementById("admcaleventedit")) {
                        $("#admcaleventedit").remove();
                    }
                    //define and render new edit form
                    var sEventEditForm =
                        '<div id="admcaleventedit">' +
                        "<fieldset>" +
                        "<p><h3>Edit Event</h3></p>" +
                        '<p><label for="admcaltitle">Title:</label><span><input id="admcaltitle"></span></p>' +
                        '<p><label for="admcalurl">URL:</label><span><input id="admcalurl" type="url"></span></p>' +
                        '<p><label for="admcalcolor">Color:</label><span><input id="admcalcolor" type="color"><input type="checkbox" id="admcalusecolor"><label for="admcalusecolor">Custom</label></input></span></p>' +
                        '<p><button type="button" id="admcalsave">Save Event</button><button type="button" id="admcaldismiss">Dismiss</button></p>' +
                        "</fieldset>" +
                        "</div>";
                    $("#admincalendar>div").append(sEventEditForm);

                    //set content of input fields
                    $("#admcaltitle").val(oCalendarEvent.title);
                    $("#admcalurl").val(oCalendarEvent.url);
                    if (oCalendarEvent.backgroundColor) {
                        $("#admcalcolor").val(oCalendarEvent.backgroundColor);
                        $("#admcalusecolor").prop("checked", true);
                    } else {
                        $("#admcalcolor").hide();
                    }

                    //set clickhandler for dismiss button
                    $("#admcaldismiss").click(function() {
                        $("#admcaleventedit").remove();
                    });

                    //set clickhandler for colorcheckbox
                    $("#admcalusecolor").click(function() {
                        var bChecked = $("#admcalusecolor").prop("checked");
                        if (bChecked) {
                            $("#admcalcolor").show();
                        } else {
                            $("#admcalcolor").hide();
                        }
                    });

                    //set save button event handler
                    $("#admcalsave").click(function() {
                        //get values and change them in the original event
                        oCalendarEvent.title = $("#admcaltitle").val();
                        var sUrl = $("#admcalurl").val();

                        oCalendarEvent.url = sUrl;

                        if ($("#admcalusecolor").prop("checked")) {
                            oCalendarEvent.backgroundColor = $("#admcalcolor").val();
                        } else {
                            oCalendarEvent.backgroundColor = "";
                        }
                        //update the event in the calendar
                        $("#calendar").fullCalendar("updateEvent", oCalendarEvent);

                        //remove edit form
                        $("#admcaleventedit").remove();

                        //enable save button
                        fnEnableSaveButton();
                    });
                    return false; // avoid opening the link if one is set on click
                }
            });

            //set clickhandler for add-event button
            $("#calendaraddevent").click(function() {
                //remove edit form if already rendered
                if (document.getElementById("admcaleventedit")) {
                    $("#admcaleventedit").remove();
                }

                // define and render new edit form
                var sEventEditForm =
                    '<div id="admcaleventedit">' +
                    "<fieldset>" +
                    "<h3>Add Event</h3>" +
                    '<p><label for="admcaltitle">Date:</label><span><input type="date" id="admcaldate"></span></p>' +
                    '<p><label for="admcaltitle">Title:</label><span><input id="admcaltitle"></span></p>' +
                    '<p><label for="admcalurl">URL:</label><span><input id="admcalurl" type="url"></span></p>' +
                    '<p><label for="admcalcolor">Color:</label><span><input id="admcalcolor" type="color"><input type="checkbox" id="admcalusecolor"><label for="admcalusecolor">Custom</label></input></span></p>' +
                    '<p><button type="button" id="admcalsave">Save Event</button><button type="button" id="admcaldismiss">Dismiss</button></p>' +
                    "</fieldset>" +
                    "</div>";
                $("#admincalendar>div").append(sEventEditForm);

                //set content of date input field
                $("#admcaldate").val(
                    $("#calendar")
                        .fullCalendar("getDate")
                        .format("Y-M-D")
                );

                //initially hide the color picker
                $("#admcalcolor").hide();

                //set clickhandler for colorcheckbox
                $("#admcalusecolor").click(function() {
                    var bChecked = $("#admcalusecolor").prop("checked");
                    if (bChecked) {
                        $("#admcalcolor").show();
                    } else {
                        $("#admcalcolor").hide();
                    }
                });

                //set clickhandler for dismiss button
                $("#admcaldismiss").click(function() {
                    $("#admcaleventedit").remove();
                });

                //set save button event handler
                $("#admcalsave").click(function() {
                    //get values and change them in the original event
                    var oCalendarEvent = {};
                    oCalendarEvent.title = $("#admcaltitle").val();
                    oCalendarEvent.start = $("#admcaldate").val();
                    var sUrl = $("#admcalurl").val();
                    if (sUrl) {
                        oCalendarEvent.url = sUrl;
                    }

                    if ($("#admcalusecolor").prop("checked")) {
                        oCalendarEvent.backgroundColor = $("#admcalcolor").val();
                    } else {
                        oCalendarEvent.backgroundColor = "";
                    }
                    //update the event in the calendar
                    $("#calendar").fullCalendar("renderEvent", oCalendarEvent, true);

                    //remove edit form
                    $("#admcaleventedit").remove();

                    //enable save button
                    fnEnableSaveButton();
                });
            });
        }
    });
});
