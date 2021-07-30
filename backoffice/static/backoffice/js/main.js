var maxphonelength = 14;
var cloudmade_key = "b55e3a3af1394462b2099bc1263f1e5e";
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


var confirmDelete = function(form, type) {
    if (confirm('This ' + type + ' will be deleted. Are you sure?')) {
        form.submit();
    }
    return false;
};

var refreshSpecs = function() {
    var specsJson = $('#specs').val();
    if (specsJson) {
        try {
            $('#specs-output').html(JSON.stringify(JSON.parse(specsJson), null, 4));
        } catch(err) {
            $('#specs-output').html('Invalid JSON.');
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

var refreshMedia = function() {
    var vehicleid = $('#vehicleid').val();
    var vpicsUrl = 'ajax_vpics.cfm?vehicleid=' + vehicleid;
    var vvidsUrl = 'ajax_vvids.cfm?vehicleid=' + vehicleid;
    var showcaseUrl = 'showcase/';
    var thumbnailUrl = 'thumbnail/';
    $('#vpics').load(vpicsUrl, function() {
        $('.vpic-delete').click(function() {
            var vpicsid = $(this).attr('vpicsid');
            if (confirm('Really delete this picture?')) {
                editMedia('deleteVPic', vpicsid);
            }
        });
        $('.vpic-makefirst').click(function() {
            var vpicsid = $(this).attr('vpicsid');
            editMedia('promoteVPic', vpicsid);
        });
        $('#vpic_form').submit(function() {
            return uploadMedia('uploadVPic', vehicleid);
        });
    });
    $('#vvids').load(vvidsUrl, function() {
        $('.vvid-delete').click(function() {
            var vvidsid = $(this).attr('vvidsid');
            if (confirm('Really delete this video?')) {
                editMedia('deleteVVid', vvidsid);
            }
        });
        $('.vvid-makefirst').click(function() {
            var vvidsid = $(this).attr('vvidsid');
            editMedia('promoteVVid', vvidsid);
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
};

var editMedia = function(method, mediaid) {
    var params = {
        component: 'media',
        method: method,
        mediaid: mediaid || null,
    }
    $.post('ajax_post.cfm',params,function(data) {
console.log(data);
        if (data.success) {
            refreshMedia();
        } else {
            alert(data.error);
        }
    }, 'json');
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
    });
    return false;
}


var showSurveyDetails = function(surveyid) {
console.log(surveyid);
    $('.dialog-survey[surveyid=' + surveyid + ']').dialog({
        modal: true,
    });
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
    $.post(url, params, function(data) {
        if (data.is_sleeping && !activityTrackerExempt) {
            console.log('Sleeping; idling out');
            window.location.href = '/backoffice/';
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
        var col = $(this).attr('col');
        var defaultdir = $(this).attr('defaultdir');
        var table = $(this).closest('table');
        var page = table.attr('page');
        var sortedby = table.attr('sortedby');
        var sorteddir = table.attr('sorteddir');
        var filter = table.attr('filter') || '';
        var sortdir = '';
        if (col == sortedby) {
            sortdir = sorteddir == 'ASC' ? 'DESC' : 'ASC';
        } else {
            sortdir = defaultdir;
        }
        if (col && sortdir) {
            location = page + '?sortby=' + col + '&sortdir=' + sortdir + (filter ? '&' + filter : '');
        }
    });

    // Column sort direction switching
    var sortedby = $('table.data').attr('sortedby');
    var sorteddir = $('table.data').attr('sorteddir');
    if (sortedby && sorteddir) {
        $('th[col=' + sortedby + ']').addClass('sort_selected').addClass(sorteddir.toLowerCase());
    }

    // Autoformat JSON specs field
    refreshSpecs();
    $('#specs').keyup(function() {
        refreshSpecs();
    });

    // Enforce formatting for phone numbers
    $('.phone').on('keyup change', function() {
        $(this).val(formatPhone($(this).val()));
    });

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

    // Autocomplete for adding customers to reservations
    $('input#customername').keyup(function() {
        $('.newuserfield').val('').prop('disabled', false);
    }).autocomplete({
        source: 'cfc/customers.cfc?method=getCustomers',
        select: function(event, ui) {
            $('input#customerid').val(ui.item.customerid);
            $('input#customername').val(ui.item.label);
            $('input#fname').val(ui.item.fname).prop('disabled', true);
            $('input#lname').val(ui.item.lname).prop('disabled', true);
            $('input#email').val(ui.item.email).prop('disabled', true);
            $('input#hphone').val(ui.item.hphone).prop('disabled', true);
            $('input#wphone').val(ui.item.wphone).prop('disabled', true);
            $('input#mphone').val(ui.item.mphone).prop('disabled', true);
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
        $('#dateout').prop('disabled', true);
        $('#dateouttime').prop('disabled', true);
    }
    if ($.inArray($('#status').val(), ['3']) > -1) {
        $('#dateback').prop('disabled', true);
        $('#datebacktime').prop('disabled', true);
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

    $('tr.survey').click(function() {
        showSurveyDetails($(this).attr('itemid'));
    });
    $('tr.click-to-edit').click(function() {
        window.location = '?edit=1&' + $(this).attr('idfield') + '=' + $(this).attr('itemid');
    });

    refreshDrivers();
    refreshMedia();

    setInterval('trackActivity()', 5000);
    lastActivity = new Date();
    addEventListener('mousemove', function() {
        lastActivity = new Date();
    })
});

