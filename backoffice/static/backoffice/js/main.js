var maxphonelength = 14;
var cloudmade_key = "b55e3a3af1394462b2099bc1263f1e5e";
var blurTimeout = null;
let lastActivity = null;
const idleTimeoutSecs = 1500;
let activityTrackerExempt = false;

var map;
var geocoder;
var lat_start = 40.755;             // New York NY
var long_start = -73.954;


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

function checkType() {
    var tmin = $('#admin').val();

    $.getJSON('cfc/2fac.cfc', {
        method: 'checkType',
        returnformat: 'json',
        adm: tmin,
    }, function(adata) {
        if (adata.F == 1 && adata.TF == 2) {
            $('#btn_send_key').show();
            $('#aid').val(adata.AID);
        } else {
            $('#btn_send_key').hide();
            $('#aid').val(0);
        }
    });
}

function doSend() {
    var aid = $('#aid').val();
    $.get("tkt.cfm", { aid: +aid} );
}


var changeCar = function() {
    $.post('ajax_post.cfm', {
        component: 'miles',
	method: 'getMiles',
        dateout: $('#dateout').val(),
        dateback: $('#dateback').val(),
        dateouttime: $('#dateouttime').val(),
        datebacktime: $('#datebacktime').val(),
	vehicleid: $('#vehicleid').val(),
    },
    function(data) {
console.log(data);
        $('#milesinc').val(data.milesinc);
        $('#milesout').val(data.mileage);
        $('#milesback').val(data.mileage);
        $('#depamount').val(data.deposit);
        $('#damageout').val(data.damage);
    }, 'json');
};


var confirmDelete = function(form, deleteUrl, objectName) {
    const confirmStr = `This ${objectName} will be deleted. Are you sure?`
    if (confirm(confirmStr)) {
        form.action = deleteUrl;
        form.submit();
    }
    return false;
};

var refreshSpecs = function() {
    var specsJson = $('#id_specs').val();
    if (specsJson) {
        try {
            $('#specs-output').html(JSON.stringify(JSON.parse(specsJson), null, 4));
        } catch(err) {
            $('#specs-output').html('Invalid JSON.');
            console.log(err);
        }
    }
};

var refreshSalesTaxDetail = function() {
    var detailJson = $('#detail').val();
    if (detailJson) {
        try {
            $('#salestax-output').html(JSON.stringify(JSON.parse(detailJson), null, 4));
        } catch(err) {
            $('#salestax-output').html('Invalid JSON.');
            console.log(err);
        }
    }
};

var refreshDrivers = function() {
    $('#drivers').load('ajax_drivers.cfm?rentalid=' + $('#rentalid').val(), function(html) {
        $('#do_driver_add').button({
            icons: {
                primary: 'ui-icon-plusthick',
            },
            text: false,
        }).click(function(event) {
            editDriver('addDriver', null, $('#driver_add_id').val(), $('#rentalid').val());
            event.preventDefault();
        });
        $('button.remove-driver').each(function() {
            $(this).button({
                icons: {
                    primary: 'ui-icon-trash',
                },
                text: false,
            }).click(function(event) {
                editDriver('removeDriver', $(this).attr('driverid'));
                event.preventDefault();
            });
        });
        $('button.make-primary-driver').each(function() {
            $(this).button({
                icons: {
//                    primary: 'ui-icon-arrowthickstop-1-n',
                    primary: 'ui-icon-star',
                },
                text: false,
            }).click(function(event) {
                editDriver('makePrimaryDriver', $(this).attr('driverid'));
                event.preventDefault();
            });
        });

        $('input#driver_add').autocomplete({
            source: 'cfc/customers.cfc?method=getCustomers',
            select: function(event, ui) {
                $('input#driver_add_id').val(ui.item.customerid);
                $('input#driver_add').val(ui.item.label);
                return false;
            },
            focus: function(event, ui) {
                $('input#driver_add').val(ui.item.label);
                return false;
            },
        });
    });
};

var editDriver = function(method, driverid, customerid, rentalid) {
    var params = {
        component: 'drivers',
        method: method,
        customerid: customerid || null,
        rentalid: rentalid || null,
        driverid: driverid || null,
    };
    $.post('ajax_post.cfm',params,function(data) {
console.log(data);
        if (data.success) {
            refreshDrivers();
        } else {
            alert(data.error);
        }
    }, 'json');
};

var promptCloneCustomer = function() {
    $('#dialog_clone_driver').dialog({
        modal: true,
        width: 600,
        buttons: {
            'Clone': cloneCustomer,
            'Cancel': function() {
                $(this).dialog('close');
            },
        }
    });
};

var cloneCustomer = function() {
    var rentalid = $('#rentalid').val();
    var params = {
        component: 'customers',
        method: 'cloneCustomer',
        fname: $('#clone_fname').val(),
        lname: $('#clone_lname').val(),
        email: $('#clone_email').val(),
        clone_license: $('#clone_license').prop('checked'),
        customerid: $('#clone_customerid').val(),
        rentalid: rentalid,
    };
    $.post('ajax_post.cfm',params,function(data) {
console.log(data);
        if (data.success) {
            if (rentalid) {
                editDriver('addDriver', null, data.customerid, rentalid);
            } else {
                alert('New cloned customer created successfully.');
            }
            $('#dialog_clone_driver').dialog('close');
        } else {
            alert(data.error);
        }
    });
}

var showPastRentals = function() {
    $('#dialog_past_rentals').dialog({
        modal: true,
        width: 600,
        buttons: {
            'OK': function() {
                $(this).dialog('close');
            },
        }
    });
};

var refreshMedia = function() {
    var vehicleid = $('#vehicleid').val();
    var vpicsUrl = 'pictures/';
    var vvidsUrl = 'videos/';
    var showcaseUrl = 'showcase/';
    var thumbnailUrl = 'thumbnail/';
    var inspectionUrl = 'inspection/';
    var mobilethumbUrl = 'mobile_thumb/';
    $('#vpics').load(vpicsUrl, function() {
        $('.vpic-delete').click(function() {
            var vpicsid = $(this).attr('vpicsid');
            if (confirm('Really delete this picture?')) {
                editMedia('delete', 'picture', vpicsid);
            }
        });
        $('.vpic-makefirst').click(function() {
            var vpicsid = $(this).attr('vpicsid');
            editMedia('promote', 'picture', vpicsid);
        });
        $('#vpic_form').submit(function() {
            return uploadMedia('uploadVPic', vehicleid);
        });
    });
    $('#vvids').load(vvidsUrl, function() {
        $('.vvid-delete').click(function() {
            var vvidsid = $(this).attr('vvidsid');
            if (confirm('Really delete this video?')) {
                editMedia('delete', 'video', vvidsid);
            }
        });
        $('.vvid-makefirst').click(function() {
            var vvidsid = $(this).attr('vvidsid');
            editMedia('promote', 'video', vvidsid);
        });
        $('#activate_vvid_form').click(function() {
            $('img.vvid').removeClass('selected');
            $('#mp4_status').html('');
            $('#webm_status').html('');
            $('#thumbup').val('');
            $('#length').val('');
            $('#title').val('');
            $('#blurb').val('');
            $('#vvidsid').val('');
            $('#upload_vvid').html('Upload');
            $('#vvids_upload').slideDown(200);
        });
        $('#deactivate_vvid_form').click(function() {
            $('#vvids_upload').slideUp(200);
        });
        $('#vvid_form').submit(function() {
            return uploadMedia('uploadVVid', vehicleid);
        });

        $('#length').inputmask("mask", {'mask': '99:99'});
        $('img.vvid').click(function() {
            var mediaUrl = 'ajax_post.cfm';
            var params = {
                component: 'media',
                method: 'getVVid',
                returnformat: 'json',
                mediaid: $(this).attr('vvidsid'),
            };
            $('img.vvid').removeClass('selected');
            $(this).addClass('selected');
            $.post(mediaUrl, params, function(data) {
                if (data.success) {
                    $('#mp4_status').html('');
                    $('#webm_status').html('');
                    if (!data.mp4_exists) {
                        $('#mp4_status').html(data.mp4 + ' does not exist.');
                    }
                    if (!data.webm_exists) {
                        $('#webm_status').html(data.webm + ' does not exist.');
                    }
                    $('#thumbup').val('');
                    $('#length').val(data.length);
                    $('#title').val(data.title);
                    $('#blurb').val(data.blurb);
                    $('#vvidsid').val(data.vvidsid);
                    $('#upload_vvid').html('Edit');
                    $('#vvids_upload').slideDown(200);
                } else {
                    alert(data.error);
                }
            }, 'json');
        });
    });
    $('#showcase').load(showcaseUrl, function() {
        $('#showcase_form').submit(function() {
            return uploadMedia('uploadShowcase', vehicleid);
        });
    });
    $('#thumbnail').load(thumbnailUrl, function() {
        $('#thumbnail_form').submit(function() {
            return uploadMedia('uploadThumbnail', vehicleid);
        });
    });
    $('#inspection').load(inspectionUrl, function() {
        $('#inspection_form').submit(function() {
            return uploadMedia('uploadInspection', vehicleid);
        });
    });
    $('#mobilethumb').load(mobilethumbUrl, function() {
        $('#mobilethumb_form').submit(function() {
            return uploadMedia('uploadMobileThumb', vehicleid);
        });
    });
};

var editMedia = function(method, mediaType, mediaId) {
    var params = {
        component: 'media',
        method: method,
        media_type: mediaType,
        media_id: mediaId,
    }
    let url = `${mediaType}/${mediaId}/${method}/`;
    $.post(url, params, function(data) {
console.log(data);
        if (data.success) {
            refreshMedia();
        } else {
            alert(data.error);
        }
    }, 'json')
    .fail(function() {
        alert('An error occurred. Please retry.');
    });
};


var uploadMedia = function(method, vehicleid) {
    var data = new FormData();
    $.each($('#picup')[0].files, function(i, file) {
        data.append('picup', file);
    });
    $.each($('#showcaseup')[0].files, function(i, file) {
        data.append('showcaseup', file);
    });
    $.each($('#thumbnailup')[0].files, function(i, file) {
        data.append('thumbnailup', file);
    });
    $.each($('#inspectionup')[0].files, function(i, file) {
        data.append('inspectionup', file);
    });
    $.each($('#mobilethumbup')[0].files, function(i, file) {
        data.append('mobilethumbup', file);
    });
    data.append('component', 'media');
    data.append('method', method);
    data.append('vehicleid', vehicleid);

    $('.spinner[method='+method+']').show();

    if (method == 'uploadVVid') {
        data.append('vvidsid', $('#vvidsid').val());
        data.append('length', $('#length').val());
        data.append('title', $('#title').val());
        data.append('blurb', $('#blurb').val());
        $.each($('#vidthumbup')[0].files, function(i, file) {
            data.append('vidthumbup', file);
        });
    }
    $.ajax({
        url: 'ajax_post.cfm',
        data: data,
        cache: false,
        contentType: false,
        processData: false,
        type: 'POST',
        success: function(data) {
console.log(data);
        $('.spinner[method='+method+']').hide();
            if (data.success) {
                refreshMedia();
            } else {
                alert(data.error);
            }
        },
    })
    .fail(function() {
        alert('An error occurred. Please retry.');
    });
    return false;
}

var selectVehicle = function() {
    var vehicleid = $('#vehicle_select').val();
    var baseurl = window.location.href.split('?')[0];
    var urlparams = getJsonFromUrl(true);
    urlparams.vehicleid = vehicleid;
    window.location.href = baseurl + '?' + serialize(urlparams);
};


var showSurveyDetails = function(surveyid) {
console.log(surveyid);
    $('.dialog-survey[surveyid=' + surveyid + ']').dialog({
        modal: true,
    });
};

var sendInsuranceAuthForm = function(customerid) {
    if (confirm('An insurance authorization form will be emailed to the customer. Continue?')) {
        $.post('ajax_post.cfm', {
            component: 'reservations',
            method: 'sendInsuranceAuthForm',
            customerid: customerid,
        },
        function(data) {
            if (data.success) {
                alert('Insurance form was successfully sent.');
            } else {
                alert(data.error);
            }
        }, 'json');
    }
};

var sendWelcomeEmail = function(reservationid, rentalid) {
    if (confirm('The welcome email (with a link to the customer portal/password retrieval page) will be emailed to the customer. Proceed?')) {
        $.post('ajax_post.cfm', {
            component: 'reservations',
            method: 'sendWelcomeEmail',
            reservationid: reservationid,
            rentalid: rentalid,
        },
        function(data) {
            if (data.success) {
                alert('Welcome email was successfully sent.');
            } else {
                alert(data.error);
            }
        }, 'json');
    }
};

var sendGiftCertEmail = function(giftcertid) {
    if (confirm('An email will be sent notifying the customer of the download link for the completed gift certificate. Proceed?')) {
        $.post('ajax_post.cfm', {
            component: 'giftcert',
            method: 'sendGiftCertEmail',
            giftcertid: giftcertid,
        },
        function(data) {
            if (data.success) {
                alert('Gift certificate download email was successfully sent.');
            } else {
                alert(data.error);
            }
        }, 'json');
    }
};

var getTaxRate = function() {
    var zip = $('#id_delivery_zip').val() || $('#zipcode').val() || '';
    $.post('/api/tax_rate/', {
        // component: 'reservations',
        // method: 'getSalesTax',
        zip: zip,
    },
    function(data) {
console.log(data);
        if (data.success) {
            $('#id_tax_percent').val(data.tax_rate.toFixed(3));
            // $('#totalrate').val(data.tax_rate.toFixed(3));
            // $('#detail').val(JSON.stringify(data.detail));
            refreshSalesTaxDetail();
        } else {
            alert(data.error);
        }
    }, 'json');
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

var trackActivity = function () {
    let url = '/backoffice/track_activity/';
    const params = {
        last_activity: lastActivity.toISOString(),
    };
    $.post(url, params, function (data) {
        if (data.is_sleeping && !activityTrackerExempt) {
            console.log('Sleeping; idling out');
            window.location.href = '/backoffice/';
        }
    });
};

var getJsonFromUrl = function(hashBased) {
    var query;
    if(hashBased) {
        var pos = location.href.indexOf("?");
        if(pos==-1) return [];
        query = location.href.substr(pos+1);
    } else {
        query = location.search.substr(1);
    }
    var result = {};
    query.split("&").forEach(function(part) {
        if(!part) return;
        part = part.split("+").join(" "); // replace every + with space, regexp-free version
        var eq = part.indexOf("=");
        var key = eq>-1 ? part.substr(0,eq) : part;
        var val = eq>-1 ? decodeURIComponent(part.substr(eq+1)) : "";
        var from = key.indexOf("[");
        if(from==-1) result[decodeURIComponent(key)] = val;
        else {
            var to = key.indexOf("]");
            var index = decodeURIComponent(key.substring(from+1,to));
            key = decodeURIComponent(key.substring(0,from));
            if(!result[key]) result[key] = [];
            if(!index) result[key].push(val);
            else result[key][index] = val;
        }
    });
    return result;
};

var serialize = function(obj) {
    var str = [];
    for(var p in obj)
        if (obj.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        }
    return str.join("&");
}

var stripeResponseHandler = function(status, response) {
    var $form = $('#stripe_form');
console.log(response);
    if (response.error) {
        $('#stripe_error').val(response.error.message);
        $('#stripe_error_param').val(response.error.param);
        $form.get(0).submit();
    } else {
        $('#stripe_token').val(response.id);
        $form.get(0).submit();
    }
};

var checkScheduleConflict = function() {
    var params = {
        component: 'reservations',
        method: 'checkConflict',
        dateout: $('#dateout').val(),
        dateouttime: $('#dateouttime').val(),
        dateback: $('#dateback').val(),
        datebacktime: $('#datebacktime').val(),
        vehicleid: $('#vehicleid').val(),
        reservationid: $('#reservationid').val() || null,
        rentalid: $('#rentalid').val() || null,
    }
    $.post('ajax_post.cfm',params,function(data) {
console.log(data);
        if (data.success) {
            if (data.conflicts.length > 0) {
                $('#conflict_vehicle').html(data.make + ' ' + data.model);
                $('#conflict_data tbody').empty();
                for (var c in data.conflicts) {
                    conflict = data.conflicts[c];
                    var tr = $('<tr>');
                    tr.append($('<td>', {
                        html: conflict.fname + ' ' + conflict.lname,
                    })).append($('<td>').append(
                        $('<a>', {
                            href: conflict.reservationid ? 'reservations.cfm?edit=1&reservationid=' + conflict.reservationid : 'rentals.cfm?edit=1&rentalid=' + conflict.rentalid,
                            html: conflict.type,
                            target: '_blank',
                        })
                    )).append($('<td>', {
                        html: conflict.dateout,
                    })).append($('<td>', {
                        html: conflict.dateback,
                    })).append($('<td>', {
                        html: conflict.numdays,
                    }));
                    $('#conflict_data tbody').append(tr);
                }
                $('.schedule-conflict-warning').show();
            } else {
                $('.schedule-conflict-warning').hide();
            }
        } else {
            console.log(data.error);
        }
    }, 'json');
};

var showScheduleConflicts = function() {
    $('#dialog_conflicts').dialog({
        modal: true,
        width: 1000,
        maxHeight: 700,
        buttons: {
            'OK': function() {
                $(this).dialog('close');
            },
        }
    });
};


$(document).ready(function() {

    // Navigation menus
    $('#todolistlink').click(function(event){
        $('.popupbox').not('#todolist').hide();
        $('.headermenu').not(this).removeClass('hovertab');
        $('#todolist').toggle();
        $('#todolistlink').toggleClass('hovertab');
        return false;
    });
    $('#priceslink').click(function(event){
        $('.popupbox').not('#prices').hide();
        $('.headermenu').not(this).removeClass('hovertab');
        $('#prices').toggle();
        $('#priceslink').toggleClass('hovertab');
        return false;
    });
    $('#vehiclesmenulink').click(function(event){
        $('.popupbox').not('#menu_vehicles').hide();
        $('.headermenu').not(this).removeClass('hovertab');
        $('#menu_vehicles').toggle();
        $('#vehiclesmenulink').toggleClass('hovertab');
        return false;
    });
    $('#opsmenulink').click(function(event){
        $('.popupbox').not('#menu_ops').hide();
        $('.headermenu').not(this).removeClass('hovertab');
        $('#menu_ops').toggle();
        $('#opsmenulink').toggleClass('hovertab');
        return false;
    });
    $('#adminmenulink').click(function(event){
        $('.popupbox').not('#menu_admin').hide();
        $('.headermenu').not(this).removeClass('hovertab');
        $('#menu_admin').toggle();
        $('#adminmenulink').toggleClass('hovertab');
        return false;
    });

    $("html").click(function(event){
        $('.popupbox').hide();
        $('.headermenu').removeClass('hovertab');
    });

    // Geolocation map
    if ($('#map').length) {
        // Google (iffy because site is not publicly visible; geocoding requires an accompanying map)
        geocoder = new google.maps.Geocoder();
        var address = $('#addr').val() + ", " + $('#zip').val();
        geocoder.geocode( { 'address': address}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                var mapOptions = {
                    zoom: 14,
                    center: results[0].geometry.location,
                    mapTypeId: google.maps.MapTypeId.HYBRID
                }
                map = new google.maps.Map(document.getElementById("map"), mapOptions);
                var marker = new google.maps.Marker({
                    map: map,
                    position: results[0].geometry.location
                });
                $('#maplink').html("<a target='_blank' href='http://maps.google.com/maps?q="+address+"&z=16'>view full-size</a>");
            } else {
                $('#map').html("<p>No map available</p>");
            }
        });
    }

    // Table sorting by column headers
    $('table.data th').click(function() {
        let col = $(this).attr('col');
        let defaultSort = $(this).attr('default-sort');
        let table = $(this).closest('table');
        let sortedBy = table.attr('sortedby');
        let sortBy = '';
        let sortColumn = sortedBy.replace('-', '');
        if (col === sortColumn) {
            sortBy = sortedBy[0] === '-' ? sortColumn : `-${sortColumn}`;
        } else {
            sortBy = defaultSort === 'desc' ? `-${col}` : col;
        }
        if (sortBy) {
            location.href = `?sortby=${sortBy}`;
        }
    });

    // Column sort direction switching
    let sortedBy = $('table.data').attr('sortedby') || '';
    let sortColumn = sortedBy.replace('-', '');
    let sortDirClass = sortedBy[0] === '-' ? 'desc' : 'asc';
    if (sortedBy) {
        $('th[col=' + sortColumn + ']').addClass('sort_selected').addClass(sortDirClass);
    }

    // Autoformat JSON specs field
    refreshSpecs();
    $('#id_specs').keyup(function() {
        refreshSpecs();
    });

    // Autoformat sales tax details JSON field
    refreshSalesTaxDetail();
    $('#detail').keyup(function() {
        refreshSalesTaxDetail();
    });

    // Enforce formatting for phone numbers
    $('.phone').on('keyup change', function() {
        $(this).val(formatPhone($(this).val()));
    });

    // Enforce formatting for SSN (on subpay)
//    $('.currency').inputmask({'alias': 'currency'});
    $('.ssn').inputmask("mask", {'mask': '999-99-9999'});

    // Date pickers
    $('.dob').datepicker({
        changeMonth: true,
        changeYear: true,
        yearRange: '1940:2000',
        defaultDate: '01/01/1970',
    });
    $('#dateout').datepicker({});
    $('#dateback').datepicker({});
    $('#depchargedon').datepicker({});
    $('#deprefundon').datepicker({});
    $('#reqdate').datepicker({});
    $('#bupdate').datepicker({});
    $('#donestamp').datepicker({});
    $('#nextstamp').datepicker({});
    $('#stamp').datepicker({});
    $('#damageon').datepicker({});
    $('#repairedon').datepicker({});

    // Tooltip for vehicle specs model
    $('.specs-model').tooltip({
        content: function() {
            return $('#specs_model').html();
        },
        tooltipClass: 'pre',
    });

    // Credit card field processing
    $('input#ccnum').payment('formatCardNumber');
    $('input#cc2num').payment('formatCardNumber');
    $('input#cccvv').payment('formatCardCVC');
    $('input#cc2cvv').payment('formatCardCVC');
    $('input#ccnum').trigger($.Event( 'keyup', {which:$.ui.keyCode.SPACE, keyCode:$.ui.keyCode.SPACE}));
    $('input#cc2num').trigger($.Event( 'keyup', {which:$.ui.keyCode.SPACE, keyCode:$.ui.keyCode.SPACE}));

    // Add CC classes to credit card field upon load
    $('div.card-number').each(function() {
        $(this).parent().addClass($.payment.cardType($(this).html()));
    });

    // Autocomplete for adding customers to reservations
    $('input#customername').keyup(function() {
        $('.newuserfield').val('').removeClass('dont-edit');
        $('.matched-customer').hide();
    }).autocomplete({
        // source: 'cfc/customers.cfc?method=getCustomers',
        source: '/api/customers/search/',
        select: function(event, ui) {
            $('input#id_customer').val(ui.item.id);
            $('input#customername').val(ui.item.label);

            $('input#id_first_name').val(ui.item.first_name).addClass('dont-edit');
            $('input#id_last_name').val(ui.item.last_name).addClass('dont-edit');
            $('input#id_email').val(ui.item.email).addClass('dont-edit');
            $('input#id_home_phone').val(ui.item.home_phone).addClass('dont-edit');
            $('input#id_work_phone').val(ui.item.work_phone).addClass('dont-edit');
            $('input#id_mobile_phone').val(ui.item.mobile_phone).addClass('dont-edit');
            $('.matched-customer').attr('customerid', ui.item.id).show();

            $('#doemail').val(0);
            return false;
        },
        focus: function(event, ui) {
            $('input#customername').val(ui.item.label);
            return false;
        },
    });

    // Reset customerid if you start manually entering a name
    $('.newuserfield,#customername').keyup(function() {
        $('#customerid').val('');
    });

    // Disable out/in date pickers depending on status of rental
    if ($.inArray($('#status').val(), ['2','3']) > -1) {
        $('#dateout').addClass('dont-edit');
        $('#dateouttime').addClass('dont-edit');
    }
    if ($.inArray($('#status').val(), ['3']) > -1) {
        $('#dateback').addClass('dont-edit');
        $('#datebacktime').addClass('dont-edit');
    }

    // Set default driver and passenger numbers when switching JoyPerf type
    $('table.joyperf #type').change(function() {
        var eventType = $(this).val();
        if (eventType == 2) {
            $('#nodrv').val(1);
            $('#nopax').val(0);
        } else if (eventType == 1) {
            $('#nodrv').val(0);
            $('#nopax').val(1);
        }
    });

    // Stripe payment form
    $('#stripe_form').submit(function(event) {
        var $form = $(this);
        // Disable the submit button to prevent repeated clicks
        $form.find('button').prop('disabled', true);
        var addr = $('#addr').val().split('\n');
        Stripe.card.createToken({
            name: $('#ccname').val(),
            number: $('#ccnum').val(),
            cvc: $('#cccvv').val(),
            exp_month: $('#ccexpmo').val(),
            exp_year: $('#ccexpyr').val(),
            address_line1: addr[0],
            address_line2: addr[1],
            address_city: $('#city').val(),
            address_state: $('#state').val(),
            address_zip: $('#zip').val(),
        }, stripeResponseHandler);
        return false;
    });

    // Survey details diaog
    $('tr.survey').click(function() {
        showSurveyDetails($(this).attr('itemid'));
    });
    $('tr.click-to-edit').click(function() {
        window.location.href = $(this).attr('destination');
    });

    // Schedule conflict checking in reservation / rental pages
    $('.check-conflict').blur(function() {
        clearTimeout(blurTimeout);
        blurTimeout = setTimeout('checkScheduleConflict()', 1000);
    });
    if ($('.check-conflict').length) {
        checkScheduleConflict();
    }

    // Buttonize the "Number of Rentals" number
    $('.past-rentals').button().click(function() {
        showPastRentals();
    });

    // Icon link to customer page on reservation / rental pages
    if ($('#customerid').val() == 0) {
        $('.matched-customer').hide();
    }
    $('.matched-customer').click(function() {
        window.open('customers.cfm?edit=1&customerid=' + $(this).attr('customerid'));
    });

    refreshDrivers();
    refreshMedia();

    setInterval('trackActivity()', 5000);
    lastActivity = new Date();
    addEventListener('mousemove', function() {
        lastActivity = new Date();
    })
});

