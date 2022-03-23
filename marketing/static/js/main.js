var maxphonelength = 14;

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

var reserveValidateForm = function(reservationType, section) {
    var params = {};
    var formArray = $('#reservation_form').serializeArray();
    for (var elem in formArray) {
        params[formArray[elem].name] = formArray[elem].value;
    }
    method = reservationType;
    params.component = 'porknbeans';
    params.method = method;
    console.log(params);

//    $('.' + section + ' .btn').prop('disabled', true);
//     $('#reservation_' + section + '_error').hide();
    $('.exception').hide();
//    $.post('ajax_post.cfm',params,function(data) {
    console.log(method);
    console.log(section);
    $('#reservation_payment').hide();
    $('#reservation_login').hide();
    // $('#reservation_existing_user').hide();
    $.post(`/api/validate/${reservationType}/${section}/`, params, function(data) {
        console.log(data);
        $('.' + section + ' .field-error').removeClass('field-error');
        if (data.success) {
            if (section === 'details') {
                if (reservationType === 'rental') {
                    $('.price-numdays').html(data.price_data.num_days + ' day' + (data.price_data.num_days !== 1 ? 's' : ''));
                    $('.price-rental-total').html(data.price_data.base_price.toFixed(2));
                    $('.price-multi-day-discount').html(data.price_data.multi_day_discount.toFixed(2));
                    $('.price-multi-day-discount-pct').html(data.price_data.multi_day_discount_pct);
                    $('.price-specific-discount').html(data.price_data.specific_discount.toFixed(2));
                    $('.price-specific-discount-label').html(data.price_data.specific_discount_label);
                    if (data.price_data.specific_discount) {
                        $('.specific-discount').show();
                    } else {
                        $('.specific-discount').hide();
                    }
                    $('.price-extra-miles').html(data.price_data.extra_miles);
                    $('.price-extra-miles-cost').html(data.price_data.extra_miles_cost.toFixed(2));
                    $('.price-subtotal').html(data.price_data.subtotal.toFixed(2));
                    $('.price-tax').html(data.price_data.tax_amount.toFixed(2));
                    $('.price-tax-rate').html(data.price_data.tax_rate_as_percent);
                    $('.price-total').html(data.price_data.total_with_tax.toFixed(2));
                    $('.price-reservation-deposit').html(data.price_data.reservation_deposit.toFixed(2));
                    if (data.delivery_required) {
                        $('.price-delivery-smallprint').css('visibility', 'visible');
                    } else {
                        $('.price-delivery-smallprint').css('visibility', 'hidden');
                    }
                } else if (reservationType === 'joyride' || reservationType === 'perfexp') {
                    $('.price-nodrv').html(data.price_data.num_drivers + ' driver' + (data.price_data.num_drivers !== 1 ? 's' : ''));
                    $('.price-drvcost').html(data.price_data.driver_cost.toFixed(2));
                    $('.price-nopax').html(data.price_data.num_passengers + ' passenger' + (data.price_data.num_passengers !== 1 ? 's' : ''));
                    $('.price-paxcost').html(data.price_data.passenger_cost.toFixed(2));
                    // $('.price-event-total').html(data.price_data.subtotal.toFixed(2));
                    $('.price-customer-discount').html(data.price_data.customer_discount.toFixed(2));
                    $('.price-specific-discount').html(data.price_data.specific_discount.toFixed(2));
                    if (data.price_data.specific_discount) {
                        $('.specific-discount').show();
                    } else {
                        $('.specific-discount').hide();
                    }
                    $('.price-specific-discount-label').html(data.price_data.specific_discount_label);
                    $('.price-subtotal').html(data.price_data.subtotal.toFixed(2));
                    $('.price-tax').html(data.price_data.tax_amount.toFixed(2));
                    $('.price-tax-rate').html(data.price_data.tax_rate_as_percent);
                    $('.price-total').html(data.price_data.total_with_tax.toFixed(2));
                }
                if (data.price_data.customer_discount) {
                    $('.customer-discount').show();
                } else {
                    $('.customer-discount').hide();
                }
                if (data.customer_id) {
                    $('.price-breakdown').appendTo($('#price_breakdown_existing_user')).removeClass('hidden');
                    $('#reservation_payment').hide();
                    $('#reservation_payment_error').hide();
                    $('#reservation_login').show();
                } else {
                    $('.price-breakdown').appendTo($('#price_breakdown_new_user')).removeClass('hidden');
                    $('#reservation_login').hide();
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
            } else if (section === 'payment' || section === 'login') {
                $('#customerid').val(data.customerid);
                $('#login_pass').val(data.create_pass);
                if (data.reservation_type === 'perfexp') {
                    window.location.href = data.customer_site_url;
                    // window.location.href = data.custsite + 'perfexp_confirm.cfm?confcode=' + data.confcode;
                } else if (data.reservation_type === 'joyride') {
                    window.location.href = data.customer_site_url;
                    // window.location.href = data.custsite + 'joyride_confirm.cfm?confcode=' + data.confcode;
                } else if (data.reservation_type === 'rental') {
                    window.location.href = data.customer_site_url;
                } else if (data.reservation_type == 'gift') {
                    window.location.href = data.success_url;
                    // window.location.href = 'gift.cfm?tag=' + data.tag;
                // } else if (data.reservation_type == 'subscribe') {
                //     window.location.href = 'newsletter.cfm?done=1';
                // } else if (data.reservation_type == 'unsubscribe') {
                //     window.location.href = 'unsubscribe.cfm?done=1';
                } else if (data.reservation_type == 'subpay') {
                    window.location.href = 'subpay.cfm?done=1';
                } else if (data.reservation_type == 'survey') {
                    window.location.href = 'survey.cfm?done=1';
                }
            } else if (section === 'subscribe') {
                window.location.href = data.success_url;
            } else if (section === 'unsubscribe') {

            }
        } else {
            $('.' + section + ' .btn').prop('disabled', false);
            console.log(data.errors);
           // $('#reservation_' + section + '_error .alert-message').html(data.errors_html);
            $('#reservation_' + section + '_error').show();
            $('#reservation_' + section).show();
            let selectedFirst = false;
            for (var field in data.errors) {
                const input = $('#id_' + field.toLowerCase());
                input.addClass('field-error');
                if (!selectedFirst) {
                    $('#reservation_' + section + '_error .alert-message').html(data.errors[field]);
                    input.select();
                    selectedFirst = true;
                }
            }
        }
    }, 'json')
    .fail(function(data) {
        console.log(data.responseJSON);
        var error = 'There was an error communicating with our system. Please try again.';
        $('#reserve-' + section + '-btn').prop('disabled', false);
        $('#reservation_' + section + '_error .alert-message').html(error);
        $('#reservation_' + section + '_error').show();
        $('#reservation_' + section).show();
    });
};

var sendResetPassword = function() {
    var params = {
        component: 'porknbeans',
        method: 'sendResetPassword',
        email: $('#email').val(),
    }
    $('#dialog_reset_password').dialog('close');
    // $.post('ajax_post.cfm',params,function(data) {
    $.post('/customer/recovery/password_reset/',params,function(data) {
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
    $('#id_vehicle_choice_1').val($($('.vehicle-picker-pick.picked')[0]).attr('vehicleid') || 0);
    $('#id_vehicle_choice_2').val($($('.vehicle-picker-pick.picked')[1]).attr('vehicleid') || 0);
    $('#id_vehicle_choice_3').val($($('.vehicle-picker-pick.picked')[2]).attr('vehicleid') || 0);
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
    if ($('#id_delivery_required').val() == 1) {
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
    $('#id_out_date').datepicker({});
    $('#id_back_date').datepicker({});
    $('#id_requested_date').datepicker({});
    $('#id_backup_date').datepicker({});

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
    $('input#id_cc_number').payment('formatCardNumber');
    $('input#id_cc_cvv').payment('formatCardCVC');
    $('input#id_cc_number').trigger($.Event( 'keyup', {which:$.ui.keyCode.SPACE, keyCode:$.ui.keyCode.SPACE}));

    $('.reserve-rental-details-btn').click(function() {
        reserveValidateForm('rental', 'details');
    });
    $('.reserve-joyride-details-btn').click(function() {
        reserveValidateForm('joyride', 'details');
    });
    $('.reserve-perfexp-details-btn').click(function() {
        reserveValidateForm('perfexp', 'details');
    });
    $('.reserve-createpass-btn').click(function() {
        reserveValidateForm('validatePassword', 'password');
    });
    $('.reserve-rental-login-btn').click(function() {
        reserveValidateForm('rental', 'login');
    });
    $('.reserve-joyride-login-btn').click(function() {
        reserveValidateForm('joyride', 'login');
    });
    $('.reserve-perfexp-login-btn').click(function() {
        reserveValidateForm('perfexp', 'login');
    });
    $('.reserve-rental-complete-btn').click(function() {
        reserveValidateForm('rental', 'payment');
    });
    $('.reserve-joyride-complete-btn').click(function() {
        reserveValidateForm('joyride', 'payment');
    });
    $('.reserve-perfexp-complete-btn').click(function() {
        reserveValidateForm('perfexp', 'payment');
    });
    $('.reserve-gift-complete-btn').click(function() {
        reserveValidateForm('gift', 'payment');
    });
    $('.subscribe-complete-btn').click(function() {
        reserveValidateForm('newsletter', 'subscribe');
    });
    $('.unsubscribe-complete-btn').click(function() {
        reserveValidateForm('unsubscribeNewsletter', 'payment');
    });
    $('.subpay-complete-btn').click(function() {
        reserveValidateForm('submitSubPay', 'payment');
    });
    $('.survey-complete-btn').click(function() {
        reserveValidateForm('submitSurvey', 'payment');
    });

    $('.pick-vehicles-btn').click(function() {
        var vehicle_type = $(this).attr('type');
        $('.vehicle-picker-pick').hide().removeClass('picked');
        var current_picks = [
            $('#id_vehicle_choice_1').val(),
            $('#id_vehicle_choice_2').val(),
            $('#id_vehicle_choice_3').val(),
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
    $('#id_delivery_required').change(function() {
        toggleDeliveryZip();
    });
    $('.delivery-zip').hide();
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
    videoPlayer.src(videos[vvidsid].src);
    if (videos[vvidsid].poster) {
        videoPlayer.poster(videos[vvidsid].poster);
    }
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
