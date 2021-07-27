var maxphonelength = 14;
var vid = 0;
var monthOffset = 0;
var dateout = null;
var reservationid = null;

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
    $('.calendar-container').load('ajax_calendar.cfm?mo=' + monthOffset + '&vid=' + vid, function() {
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
            } else if (!$(this).hasClass('rental') && vid) {
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
        vehicleid: vid,
        dateout: dateout,
        numdays: $('#reserve_number_days').val(),
    }
console.log(params);
    $('#dialog_reserve_vehicle').dialog('close');
    $.post('ajax_post.cfm',params,function(data) {
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
            alert(data.error);
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
    $.post('ajax_post.cfm',params,function(data) {
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
