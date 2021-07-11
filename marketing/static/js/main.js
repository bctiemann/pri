var maxphonelength = 14;

var reserveValidateForm = function(method, section) {
    var params = {};
    var formArray = $('#reservation_form').serializeArray();
    for (var elem in formArray) {
        params[formArray[elem].name] = formArray[elem].value;
    }
    params.component = 'porknbeans';
    params.method = method;
    console.log(params);

//    $('.' + section + ' .btn').prop('disabled', true);
    $('#reservation_' + section + '_error').hide();
    $.post('ajax_post.cfm',params,function(data) {
        console.log(data);
        $('.' + section + ' .field-error').removeClass('field-error');
        if (data.success) {
            if (section == 'identity') {
                if (method == 'validateRentalIdentity') {
                    $('.price-numdays').html(data.numdays + ' day' + (data.numdays != 1 ? 's' : ''));
                    $('.price-rental-total').html(data.tcostRaw.toFixed(2));
                    $('.price-multi-day-discount').html(data.multi_day_discount.toFixed(2));
                    $('.price-multi-day-discount-pct').html(data.multi_day_discount_pct);
                    $('.price-car-discount').html(data.car_discount.toFixed(2));
                    $('.price-customer-discount').html(data.customer_discount.toFixed(2));
                    $('.price-extra-miles').html(data.extra_miles);
                    $('.price-extra-miles-cost').html(data.extra_miles_cost.toFixed(2));
                    $('.price-subtotal').html(data.subtotal.toFixed(2));
                    $('.price-tax').html(data.tax_amt.toFixed(2));
                    $('.price-total').html(data.total_w_tax.toFixed(2));
                    $('.price-reservation-deposit').html(data.reservation_deposit.toFixed(2));
                    if (data.delivery == 0) {
                        $('.price-delivery-smallprint').css('visibility', 'hidden');
                    } else {
                        $('.price-delivery-smallprint').css('visibility', 'visible');
                    }
                } else if (method == 'validateJoyPerfIdentity') {
                    $('.price-nodrv').html(data.nodrv + ' driver' + (data.nodrv != 1 ? 's' : ''));
                    $('.price-drvcost').html(data.drvcost.toFixed(2));
                    $('.price-nopax').html(data.nopax + ' passenger' + (data.nopax != 1 ? 's' : ''));
                    $('.price-paxcost').html(data.paxcost.toFixed(2));
                    $('.price-event-total').html(data.trate.toFixed(2));
                    $('.price-customer-discount').html(data.customer_discount.toFixed(2));
                    $('.price-subtotal').html(data.subtotal.toFixed(2));
                    $('.price-tax').html(data.tax_amt.toFixed(2));
                    $('.price-total').html(data.total_w_tax.toFixed(2));
                }
                if (data.customer_discount) {
                    $('.customer-discount').show();
                } else {
                    $('.customer-discount').hide();
                }
                if (data.customerid) {
                    $('.price-breakdown').appendTo($('#price_breakdown_existing_user'));
                    $('#reservation_payment').hide();
                    $('#reservation_payment_error').hide();
                    $('#reservation_existing_user').show();
                } else {
                    $('.price-breakdown').appendTo($('#price_breakdown_new_user'));
                    $('#reservation_existing_user').hide();
                    $('#reservation_password_error').hide();
                    $('#reservation_payment').show();
                }
            } else if (section == 'password') {
                if (method == 'validateLogin') {
                    $('#customerid').val(data.customerid);
                    if (data.reservation_type == 'perfexp') {
                        reserveValidateForm('validateJoyPerfPayment','payment');
                    } else if (data.reservation_type == 'joyride') {
                        reserveValidateForm('validateJoyPerfPayment','payment');
                    } else if (data.reservation_type == 'rental') {
                        reserveValidateForm('validateRentalPayment','payment');
                    }
                } else if (method == 'validatePassword') {
                    $('#reservation_payment').show();
                }
            } else if (section == 'payment') {
                $('#customerid').val(data.customerid);
                $('#login_pass').val(data.create_pass);
                if (data.reservation_type == 'perfexp') {
                    window.location.href = data.custsite + 'perfexp_confirm.cfm?confcode=' + data.confcode;
                } else if (data.reservation_type == 'joyride') {
                    window.location.href = data.custsite + 'joyride_confirm.cfm?confcode=' + data.confcode;
                } else if (data.reservation_type == 'rental') {
                    window.location.href = data.custsite + 'reserve_confirm.cfm?confcode=' + data.confcode;
                } else if (data.reservation_type == 'gift') {
                    window.location.href = 'gift.cfm?tag=' + data.tag;
                }
            }
        } else {
            $('.' + section + ' .btn').prop('disabled', false);
            $('#reservation_' + section + '_error .alert-message').html(data.error);
            $('#reservation_' + section + '_error').show();
            for (var field in data.fieldErrors) {
                $('#' + field.toLowerCase()).addClass('field-error').select();
            }
        }
    }, 'json')
    .fail(function() {
        var error = 'There was an error communicating with our system. Please try again.';
        $('#reserve-' + section + '-btn').prop('disabled', false);
        $('#reservation_' + section + '_error .alert-message').html(error);
        $('#reservation_' + section + '_error').show();
    });
};

var sendResetPassword = function() {
    var params = {
        component: 'porknbeans',
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


$('document').ready(function() {

    (function() {
        if (!navigator.userAgent.match(/(iPhone|iPod|iPad|Android)/i)&&!$("body").hasClass("sticky_persist")) {
            var c = $("section.lower"), b = c.offset().top, a, body = $(".l-content");
            $(window).scroll(function() {
                var d = $(this).scrollTop();
                if (d < b && a) {
                    c.removeClass("fixed");
                    body.removeClass("fixed");
                    a = false 
                } else {
                    if (d > b&&!a) {
                        c.addClass("fixed");
                        body.addClass("fixed");
                        a = true
                    }
                }
            })
        }
    })();

    // Date pickers
    $('#dateout').datepicker({});
    $('#dateback').datepicker({});
    $('#reqdate').datepicker({});
    $('#bupdate').datepicker({});

    // Tooltips
    $('.tooltip').tooltip();
    $('.delivery-pricing').tooltip({
        content: function() {
            return $('#delivery_pricing').html();
        },
    });

    // Reset Password dialog
    $('.forgot-password').click(function() {
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

    // Enforce formatting for phone numbers
    $('.phone').on('keyup change', function() {
        $(this).val(formatPhone($(this).val()));
    });

    // Credit card input processing
    $('input#ccnum').payment('formatCardNumber');
    $('input#cccvv').payment('formatCardCVC');
    $('input#ccnum').trigger($.Event( 'keyup', {which:$.ui.keyCode.SPACE, keyCode:$.ui.keyCode.SPACE}));

    $('.reserve-rental-identity-btn').click(function() {
        reserveValidateForm('validateRentalIdentity', 'identity');
    });
    $('.reserve-joyperf-identity-btn').click(function() {
        reserveValidateForm('validateJoyPerfIdentity', 'identity');
    });
    $('.reserve-createpass-btn').click(function() {
        reserveValidateForm('validatePassword', 'password');
    });
    $('.reserve-login-btn').click(function() {
        reserveValidateForm('validateLogin', 'password');
    });
    $('.reserve-rental-complete-btn').click(function() {
        reserveValidateForm('validateRentalPayment', 'payment');
    });
    $('.reserve-joyperf-complete-btn').click(function() {
        reserveValidateForm('validateJoyPerfPayment', 'payment');
    });
    $('.reserve-gift-complete-btn').click(function() {
        reserveValidateForm('buyGiftCert', 'payment');
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
    $('.vehicle-picker-pick').click(function() {
        pickVehicle($(this).attr('vehicleid'));
    });

    $('#reservation_payment').hide();
    $('.inline-password').hide();
    $('.vehicle-pick-buttons').show();
    $('.vehicle-choice').hide();
    $('.reserve-identity-btn').show();

});


/* From non-secure */

var offerOpen = false;

function startCar() {
    var carIndex = Math.floor( (Math.random() * $('.fleet-container .car').length) + 1 );
    var car = $('.fleet-container .car:nth-child(' + carIndex + ')');
//    console.log(car);
    if (car.hasClass('animating')) {
        setTimeout('startCar()', 100);
        return;
    }

    var origWidth = car.attr('origWidth');
    var width = Math.floor(Math.random() * 300) + 400;
//    var width = Math.floor(Math.random() * 300);
    car.width(width);
console.log(width);
console.log(origWidth);
    var distOffset = (1 - (width / origWidth)) * 400 - 200;
console.log(distOffset);
    car.css('bottom', distOffset);
    car.show();

    var finishPoint = Math.floor(Math.random() * ($('.fleet-container').width() - width)) + width;

    if (car.hasClass('right')) {
console.log('right');
        car.addClass('animating').css('right', -width)
        .animate({
            right: finishPoint,
        }, 2000, function() {
            $(this).animate({
                right: 2000,
            }, 2000, function() {
                $(this).removeClass('animating');
            });
        });
    } else {
console.log('left');
        car.addClass('animating').css('left', -width)
        .animate({
            left: finishPoint,
        }, 2000, function() {
            $(this).animate({
                left: 2000,
            }, 2000, function() {
                $(this).removeClass('animating');
            });
        });
    }

    setTimeout('startCar()', Math.random() * 3000);
}

var switchVideo = function(vvidsid) {
    var videoPlayer = videojs('vehicle_video');
    videoPlayer.src([
        { type: "video/mp4", src: 'vids/PRI-' + vvidsid + '.mp4' },
        { type: "video/webm", src: 'vids/PRI-' + vvidsid + '.webm' },
    ]);
    videoPlayer.poster('vids/PRI-' + vvidsid + '.jpg');
    $('.vvid-blurb-caption').html($('.vvid-thumbnail[vvidsid=' + vvidsid + '] p.vvid-blurb').html());
};


$(document).ready(function() {

    (function() {
        if (!navigator.userAgent.match(/(iPhone|iPod|iPad|Android)/i)&&!$("body").hasClass("sticky_persist")) {
            var c = $("section.lower"), b = c.offset().top, a, body = $(".l-content");
            $(window).scroll(function() {
                var d = $(this).scrollTop();
                if (d < b && a) {
                    c.removeClass("fixed");
                    body.removeClass("fixed");
                    a = false
                } else {
                    if (d > b&&!a) {
                        c.addClass("fixed");
                        body.addClass("fixed");
                        a = true
                    }
                }
            })
        }
    })();


//console.log(jQCloud);
//console.log(words);
//    $('.the-numbers').jQCloud(words);

    $('.bxslider').bxSlider({
//            auto: true,
            preloadImages: 'all',
            nextSelector: '#bxslider_right',
            prevSelector: '#bxslider_left',
            nextText: '',
            prevText: '',
            onSliderLoad: function() {
//                if (sliderId == 'health') {
//                    showSubpage(sliderId,false);
//                }
            },
    });


    $('.flexslider').hover(function() {
        $(this).find('.left').animate({
            left: 10,
            opacity: 1
        });
        $(this).find('.right').animate({
            right: 10,
            opacity: 1
        });
    },function() {
        $(this).find('.left').animate({
            left: -40,
            opacity: 0
        });
        $(this).find('.right').animate({
            right: -40,
            opacity: 0
        });
    });

//    startCar();

    $('.offer-thumb').hover(function() {
        if (!offerOpen) {
            var offer = $(this).attr('offer');
            $('.offer-descr-' + offer).show().addClass('open');
            $('.offer-' + offer).addClass('open');
            $('.offer-thumb').not('.offer-' + offer).addClass('offer-hidden').addClass('hidden-' + offer);
            offerOpen = true;
        }
    }, function() {
    });

    $('.offers').mouseleave(function() {
        $('.offer-thumb').removeClass('open');
        $('.offer-thumb').removeClass('offer-hidden');
        $('.offer-thumb').removeClass('hidden-1');
        $('.offer-thumb').removeClass('hidden-2');
        $('.offer-thumb').removeClass('hidden-3');
        $('.offer-thumb').removeClass('hidden-4');
        $('.offer-descr').removeClass('open');
        offerOpen = false;
    });

    $('.vvid-thumbnail').click(function() {
        switchVideo($(this).attr('vvidsid'));
    });

});