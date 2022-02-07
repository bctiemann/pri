var maxphonelength = 14;

var reserveValidateForm = function(reservationType, section) {
    var params = {};
    var formArray = $('#reservation_form').serializeArray();
    for (var elem in formArray) {
        params[formArray[elem].name] = formArray[elem].value;
    }
    // params.component = 'cassidy';
    // params.method = method;
    params.createReservation = section == 'confirm';
    console.log(params);

    $('.' + section + ' .btn').prop('disabled', true);
    $('.next-form-spinner.' + section + '-spinner').show();

    $('#reservation_' + section + '_error').hide();
    // $.post('ajax_post.cfm',params,function(data) {
    $.post(`/api/validate/${reservationType}/${section}/`, params, function(data) {

        $('.next-form-spinner').hide();

        console.log(data);
        $('.field-error').removeClass('field-error');
        if (data.success) {
            $('.' + section + ' .btn').prop('disabled', false);
            if (section == 'price') {
                if (method == 'validateReservation') {
                    $('.price-numdays').html(data.numdays + ' day' + (data.numdays != 1 ? 's' : ''));
                    $('.price-rental-total').html(data.tcostRaw.toFixed(2));
                    $('.price-multi-day-discount').html(data.multi_day_discount.toFixed(2));
                    $('.price-multi-day-discount-pct').html(data.multi_day_discount_pct);
                    $('.price-specific-discount').html(data.price_data.specific_discount.toFixed(2));
                    $('.price-specific-discount-label').html(data.price_data.specific_discount_label);
                    $('.price-extra-miles').html(data.extra_miles);
                    $('.price-extra-miles-cost').html(data.extra_miles_cost.toFixed(2));
                    $('.price-subtotal').html(data.subtotal.toFixed(2));
                    $('.price-tax').html(data.tax_amt.toFixed(2));
                    $('.price-tax-rate').html(data.tax_rate);
                    $('.price-total').html(data.total_w_tax.toFixed(2));
                    $('.price-reservation-deposit').html(data.reservation_deposit.toFixed(2));
                    if (data.delivery == 0) {
                        $('.price-delivery-smallprint').css('visibility', 'hidden');
                    } else {
                        $('.price-delivery-smallprint').css('visibility', 'visible');
                    }
                } else if (method == 'validateJoyPerf') {
                    $('.price-nodrv').html(data.nodrv + ' driver' + (data.nodrv != 1 ? 's' : ''));
                    $('.price-drvcost').html(data.drvcost.toFixed(2));
                    $('.price-nopax').html(data.nopax + ' passenger' + (data.nopax != 1 ? 's' : ''));
                    $('.price-paxcost').html(data.paxcost.toFixed(2));
                    $('.price-event-total').html(data.trate.toFixed(2));
                    $('.price-coupon-discount').html(data.coupon_discount.toFixed(2));
                    $('.price-customer-discount').html(data.customer_discount.toFixed(2));
                    $('.price-subtotal').html(data.subtotal.toFixed(2));
                    $('.price-tax').html(data.tax_amt.toFixed(2));
                    $('.price-tax-rate').html(data.tax_rate);
                    $('.price-total').html(data.total_w_tax.toFixed(2));
                }
                $('#reservation_price_error').hide();  
                $('#reservation_confirm').show();
            } else {
                if (data.reservation_type === 'rental') {
                    window.location.href = data.customer_site_url;
                    // window.location.href = data.custsite + 'reserve_confirm.cfm?confcode=' + data.confcode;
                } else if (data.reservation_type == 'perfexp') {
                    window.location.href = data.custsite + 'perfexp_confirm.cfm?confcode=' + data.confcode;
                } else if (data.reservation_type == 'joyride') {
                    window.location.href = data.custsite + 'joyride_confirm.cfm?confcode=' + data.confcode;
                }
            }
        } else {
            $('.' + section + ' .btn').prop('disabled', false);
            $('#reservation_' + section + '_error .alert-message').html(data.error);
            $('#reservation_' + section + '_error').show(); 
            let selectedFirst = false;
            for (var field in data.errors) {
                const input = $('#id_' + field.toLowerCase());
                input.addClass('field-error');
                if (!selectedFirst) {
                    if (reservationType === 'rental') {
                        alert(data.errors[field]);
                    }
                    $('#reservation_' + section + '_error .alert-message').html(data.errors[field]);
                    input.select();
                    input[0].scrollIntoView();
                    selectedFirst = true;
                }
            } 
        }
    }, 'json')
    .fail(function() {
        var error = 'There was an error communicating with our system. Please try again.';
        $('#reserve-' + section + '-btn').prop('disabled', false); 
        $('#reservation_' + section + '_error .alert-message').html(error);
        $('#reservation_' + section + '_error').show();
        $('.' + section + ' .btn').prop('disabled', false);
        $('.next-form-spinner').hide();
    });
};

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

var setVehicles = function() {
    $('#choice1').val($($('.vehicle-picker-pick.picked')[0]).attr('vehicleid') || 0);
    $('#choice2').val($($('.vehicle-picker-pick.picked')[1]).attr('vehicleid') || 0);
    $('#choice3').val($($('.vehicle-picker-pick.picked')[2]).attr('vehicleid') || 0);
    $('#dialog_pick_vehicles').dialog('close');
    var picktype = $('.vehicle-picker-pick.picked').attr('type'); 
    var numpicked = $('.vehicle-picker-pick.picked').length;
    $('.vehicles-picked').html(numpicked + ' ' + picktype + (numpicked == 1 ? '' : 's') + ' picked');
};

var pickVehicle = function(vehicleid) {
    var vehicle = $('.vehicle-picker-pick[vehicleid=' + vehicleid + ']');
    var num_picked = $('.vehicle-picker-pick.picked').length;
    if (num_picked < 3 || vehicle.hasClass('picked')) {
        vehicle.toggleClass('picked');
    }
    num_picked = $('.vehicle-picker-pick.picked').length;
    $('#button_vehicle_picker_done').button({'disabled': num_picked == 0});
};

var toggleDeliveryZip = function() {
    if ($('#delivery').val() == 1) {
        $('.delivery-zip').show();
    } else {
        $('.delivery-zip').hide();
    }
};

var formatPhone = function(str) {
    if (str.match('^[+]')) {
        return '+' + str.replace(/[^0-9 ]/gi, '');
    }
    var strRaw = str;
    var p = str.replace(/[^\d]*/gi, '');

    var pp = p.substring(0, 3);
    if (p.length >= 3) {
        if (p.length > 3 || (p.length == 3 && !strRaw.match(' $'))) {
            pp = '(' + pp + ') ';
        }
        pp = pp + p.substring(3, 6);
    }
    if (p.length >= 6) {
        if (p.length > 6 || (p.length == 6 && !strRaw.match('-$'))) {
            pp = pp + '-';
        }
        pp = pp+p.substring(6, 10);
    }
    str = pp.substring(0, maxphonelength);
    return str;
};

var confirmDeleteCard = function(form) {
    if (confirm('This card\'s information will be deleted. Are you sure?')) {
        form.submit();
    }
    return false;
};


$(document).ready(function() {

    // Credit card input processing
    $('input#ccnum').payment('formatCardNumber');
    $('input#cc2num').payment('formatCardNumber');
    $('input#cccvv').payment('formatCardCVC');
    $('input#cc2cvv').payment('formatCardCVC');
    $('input#ccnum').trigger($.Event( 'keyup', {which:$.ui.keyCode.SPACE, keyCode:$.ui.keyCode.SPACE}));
    $('input#cc2num').trigger($.Event( 'keyup', {which:$.ui.keyCode.SPACE, keyCode:$.ui.keyCode.SPACE}));

    // Date pickers
    $('#dateout').datepicker();
    $('#dateback').datepicker();
    $('#reqdate').datepicker();
    $('#bupdate').datepicker();
    $('#dob').datepicker({
        changeMonth: true,
        changeYear: true,
        yearRange: '1940:2000',
        defaultDate: '01/01/1970',
    });

    // Tooltips
    $('.tooltip').tooltip();
    $('.delivery-pricing').tooltip({
        content: function() {
            return $('#delivery_pricing').html();
        },
    });
 
    // Enforce formatting for phone numbers
    $('.phone').on('keyup change', function() {
        $(this).val(formatPhone($(this).val()));
    });

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

    $('.pick-vehicles-btn').click(function() {
        var vehicle_type = $(this).attr('type');
        $('.vehicle-picker-pick').hide().removeClass('picked');
        var current_picks = [
            $('#choice1').val(),
            $('#choice2').val(),
            $('#choice3').val(),
        ];
        $('.vehicle-picker-pick[type=' + vehicle_type + ']').show().each(function() {
            if (current_picks.indexOf($(this).attr('vehicleid')) > -1) {
                $(this).addClass('picked');
            }
        });
        $('#dialog_pick_vehicles').dialog({
            modal: true,
            height: 600,
            width: 1000,
            buttons: [
                {
                    id: 'button_vehicle_picker_done',
                    text: 'Done',
                    disabled: true,
                    click: function() {
                        setVehicles();
                    },
                },
                {
                    id: 'button_vehicle_picker_cancel',
                    text: 'Cancel',
                    click: function() {
                        $(this).dialog('close');
                    },
                },
            ],
        });
        num_picked = $('.vehicle-picker-pick.picked').length;
        $('#button_vehicle_picker_done').button({'disabled': num_picked == 0});
    });
    $('.reserve-submit-info-btn').click(function() {
        reserveValidateForm('rental', 'confirm');
    });
    $('.vehicle-picker-pick').click(function() {
        pickVehicle($(this).attr('vehicleid'));
    });
    $('.reserve-rental-price-btn').click(function() {
        reserveValidateForm('validateReservation', 'price');
    });
    $('.reserve-rental-confirm-btn').click(function() {
        reserveValidateForm('validateReservation', 'confirm');
    });
    $('.reserve-joyperf-price-btn').click(function() {
        reserveValidateForm('validateJoyPerf', 'price');
    });
    $('.reserve-joyperf-confirm-btn').click(function() {
        reserveValidateForm('validateJoyPerf', 'confirm');
    });

    $('.vehicle-pick-buttons').show();
    $('.vehicle-choice').hide();
    $('.delivery-zip').hide();

});
