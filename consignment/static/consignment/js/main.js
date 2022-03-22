var maxphonelength = 14;
var vehicleSlug = '';
var monthOffset = 0;
var dateout = null;
var reservationid = null;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var sendResetPassword = function() {
    var params = {
        component: 'cassidy',
        method: 'sendResetPassword',
        email: $('#email').val(),
    }
    $('#dialog_reset_password').dialog('close');
    $.post('ajax_post.cfm',params,function(data) {
        console.log(data);
        if (data.success) {
            $('#dialog_reset_password_done').dialog({
                modal: true,
                buttons: {
                    'Close': function() {
                        $(this).dialog('close');
                    },
                }
            });
        } else { 
            alert(data.error);
        }
    });
};

var loadCalendar = function(mo) {
    monthOffset += mo;
    let url = '/special/calendar_widget/';
    if (vehicleSlug) {
        url += `${vehicleSlug}/`;
    }
    url += `?month_offset=${monthOffset}`;
    $('.calendar-container').load(url, function() {
    // $('.calendar-container').load('ajax_calendar.cfm?mo=' + monthOffset + '&vid=' + vid, function() {
        $('.calendar-date').click(function() {
            if ($(this).hasClass('reservation')) {
                $('.reserve-date').html($(this).attr('date'));
                reservationid = $(this).attr('reservationid');
                $('#dialog_clear_reservation').dialog({
                    modal: true,
                    buttons: {
                        'Clear Reservation': clearReservation,
                        'Cancel': function() {
                            $(this).dialog('close');
                        },
                    }
                });
            } else if ($(this).attr('date') && !$(this).hasClass('rental') && vehicleSlug) {
                $('.reserve-date').html($(this).attr('date'));
                $('#reserve_number_days').val('');
                dateout = $(this).attr('date');
                $('#dialog_reserve_vehicle').dialog({
                    modal: true,
                    buttons: {
                        'Reserve Vehicle': reserveVehicle,
                        'Cancel': function() {
                            $(this).dialog('close');
                        },
                    }
                });
            }
        });
    });
};

var reserveVehicle = function() {
    var params = {
        component: 'cassidy',
        method: 'reserveVehicle',
        // vehicleid: vid,
        out_at: dateout,
        num_days: $('#reserve_number_days').val(),
    }
console.log(params);
    $('#dialog_reserve_vehicle').dialog('close');
    $.post(`/special/reserve/${vehicleSlug}/`,params,function(data) {
        console.log(data);
        if (data.success) {
            $('#dialog_reserve_vehicle_done').dialog({
                modal: true,
                buttons: {
                    'Close': function() {
                        $(this).dialog('close');
                    },
                }
            });
            loadCalendar(0);
        } else { 
            alert(data.errors);
        }
    });
};

var clearReservation = function() {
    var params = {
        component: 'cassidy',
        method: 'clearReservation',
        reservationid: reservationid,
    }
console.log(params);
    $('#dialog_clear_reservation').dialog('close');
    // $.post('ajax_post.cfm',params,function(data) {
    $.post(`/special/unreserve/${reservationid}/`,params,function(data) {
        console.log(data);
        if (data.success) {
            loadCalendar(0);
        } else { 
            alert(data.error);
        }
    });
};


$(document).ready(function() {

    // Tooltips
    $('.tooltip').tooltip();
 
    // Reset Password dialog
    $('.forgot-password').click(function() {
        $('#password_reset_email').val($('#email').val());
        $('#dialog_reset_password').dialog({
            modal: true,
            buttons: {
                'Reset Password': sendResetPassword,
                'Cancel': function() {
                    $(this).dialog('close');
                },   
            }
        });
    });

    loadCalendar(0);
    $('.calendar-control').button();

});
