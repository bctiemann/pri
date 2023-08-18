from django.db import models


class LegacyVehicleFront(models.Model):
    vehicleid = models.IntegerField(primary_key=True)
    type = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True)
    hp = models.IntegerField(null=True, blank=True)
    tq = models.IntegerField(null=True, blank=True)
    topspeed = models.IntegerField(null=True, blank=True)
    trans = models.IntegerField(null=True, blank=True)
    gears = models.IntegerField(null=True, blank=True)
    location = models.IntegerField(null=True, blank=True)
    tightfit = models.BooleanField(default=False)
    blurb = models.TextField(blank=True)
    specs = models.TextField(blank=True)
    origin = models.CharField(max_length=2, blank=True)

    # Price fields
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    disc2day = models.IntegerField(null=True, blank=True, verbose_name='2-day discount', help_text='Percent')
    disc3day = models.IntegerField(null=True, blank=True, verbose_name='3-day discount', help_text='Percent')
    disc7day = models.IntegerField(null=True, blank=True, verbose_name='7-day discount', help_text='Percent')
    deposit = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    milesinc = models.IntegerField(null=True, blank=True, help_text='Per day')

    class Meta:
        db_table = 'VehiclesFront'


class LegacyVehicle(models.Model):
    vehicleid = models.IntegerField(primary_key=True)
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    plate = models.CharField(max_length=10, blank=True)
    vin = models.CharField(max_length=50, blank=True)
    mileage = models.IntegerField(null=True, blank=True)
    damage = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    policyno = models.CharField(max_length=255, blank=True)
    policyco = models.CharField(max_length=255, blank=True)
    policytel = models.CharField(max_length=30, blank=True)
    weighting = models.IntegerField(null=True, blank=True)
    redirect = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'Vehicles'


class LegacyVehiclePic(models.Model):
    vpicsid = models.IntegerField(primary_key=True)
    vehicleid = models.IntegerField(null=True, blank=True)
    fext = models.CharField(max_length=4, blank=True)
    isfirst = models.BooleanField(default=False)

    class Meta:
        db_table = 'VPics'


class LegacyVehicleVid(models.Model):
    vvidsid = models.IntegerField(primary_key=True)
    vehicleid = models.IntegerField(null=True, blank=True)
    fext = models.CharField(max_length=4, blank=True)
    length = models.CharField(max_length=10, blank=True)
    blurb = models.TextField(blank=True)
    isfirst = models.BooleanField(default=False)
    thumbext = models.CharField(max_length=4, blank=True)

    class Meta:
        db_table = 'VVids'


class LegacyCustomer(models.Model):
    customerid = models.IntegerField(primary_key=True)
    createdon = models.DateTimeField(auto_now_add=True)
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    addr = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=4, blank=True)
    zip = models.CharField(max_length=10, blank=True)
    hphone = models.CharField(max_length=20, blank=True)
    wphone = models.CharField(max_length=20, blank=True)
    mphone = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    dob = models.DateTimeField(null=True, blank=True)
    email = models.CharField(max_length=255, blank=True)
    licenseno = models.CharField(max_length=30, blank=True)
    licensestate = models.CharField(max_length=4, blank=True)
    licensehist = models.TextField(blank=True)
    insco = models.CharField(max_length=255, blank=True)
    inspolnum = models.CharField(max_length=255, blank=True)
    inscotel = models.CharField(max_length=20, blank=True)
    coverage = models.BooleanField(default=False)
    rentednum = models.IntegerField(null=True, blank=True)
    ccnum = models.CharField(max_length=255, blank=True, verbose_name='CC1 number')
    ccexpyr = models.CharField(max_length=4, blank=True, verbose_name='CC1 exp year')
    ccexpmo = models.CharField(max_length=2, blank=True, verbose_name='CC1 exp month')
    cccvv = models.CharField(max_length=6, blank=True, verbose_name='CC1 CVV')
    cctel = models.CharField(max_length=20, blank=True, verbose_name='CC1 contact phone')
    cc2num = models.CharField(max_length=255, blank=True, verbose_name='CC1 number')
    cc2expyr = models.CharField(max_length=4, blank=True, verbose_name='CC1 exp year')
    cc2expmo = models.CharField(max_length=2, blank=True, verbose_name='CC1 exp month')
    cc2cvv = models.CharField(max_length=6, blank=True, verbose_name='CC1 CVV')
    cc2tel = models.CharField(max_length=20, blank=True, verbose_name='CC1 contact phone')
    remarks = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True)
    driverskill = models.IntegerField(null=True, blank=True)
    discount = models.CharField(max_length=2, blank=True)
    musicgenre = models.IntegerField(null=True, blank=True)
    musicfav = models.CharField(max_length=255, blank=True)
    firsttime = models.BooleanField(default=True)
    DriversClub = models.IntegerField(null=True, blank=True)
    nomail = models.BooleanField(default=False)
    ban = models.BooleanField(default=False)
    surveydone = models.BooleanField(default=False)
    regip = models.CharField(max_length=30, blank=True, verbose_name='Registration IP')
    reglong = models.FloatField(null=True, blank=True, verbose_name='Registration longitude')
    reglat = models.FloatField(null=True, blank=True, verbose_name='Registration latitude')

    class Meta:
        db_table = 'Customers'


class LegacyCustFront(models.Model):
    customerid = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'CustFront'


class LegacyReservation(models.Model):
    reservationid = models.IntegerField(primary_key=True)
    customerid = models.IntegerField(null=True, blank=True)
    vehicleid = models.IntegerField(null=True, blank=True)
    reservdate = models.DateTimeField(auto_now_add=True)
    numdays = models.IntegerField(null=True, blank=True)
    dateout = models.DateTimeField(null=True, blank=True)
    dateback = models.DateTimeField(null=True, blank=True)
    rate = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    drivers = models.IntegerField(null=True, blank=True)
    milesinc = models.IntegerField(null=True, blank=True)
    xtramiles = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    coupon = models.CharField(max_length=30, blank=True)
    status = models.IntegerField(null=True, blank=True)
    depamount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    confcode = models.CharField(max_length=10, blank=True, unique=True, db_index=True)
    iphone = models.BooleanField(default=False)
    markid = models.IntegerField(null=True, blank=True)
    delivery = models.BooleanField(default=False)
    taxpct = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    deliveryzip = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'Reservations'


class LegacyRental(models.Model):
    rentalid = models.IntegerField(primary_key=True)
    customerid = models.IntegerField(null=True, blank=True)
    vehicleid = models.IntegerField(null=True, blank=True)
    reservdate = models.DateTimeField(auto_now_add=True)
    confirm = models.BooleanField(default=False)
    numdays = models.IntegerField(null=True, blank=True)
    dateout = models.DateTimeField(null=True, blank=True)
    dateback = models.DateTimeField(null=True, blank=True)
    rate = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    drivers = models.IntegerField(null=True, blank=True)
    milesinc = models.IntegerField(null=True, blank=True)
    xtramiles = models.IntegerField(null=True, blank=True)
    milesout = models.IntegerField(null=True, blank=True)
    milesback = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    abuse = models.TextField(blank=True)
    damageout = models.TextField(blank=True)
    damagein = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    coupon = models.CharField(max_length=30, blank=True)
    bgcheck = models.BooleanField(default=False)
    ournotes = models.TextField(blank=True)
    couponisgood = models.BooleanField(default=False)
    depchargedon = models.DateTimeField(null=True, blank=True)
    depamount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    deprefundon = models.DateTimeField(null=True, blank=True)
    deprefundamount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    extenddays = models.IntegerField(null=True, blank=True)
    confcode = models.CharField(max_length=10, blank=True, unique=True, db_index=True)
    reglat = models.FloatField(null=True, blank=True)
    reglong = models.FloatField(null=True, blank=True)
    iphone = models.BooleanField(default=False)
    markid = models.IntegerField(null=True, blank=True)
    delivery = models.BooleanField(default=False)
    taxpct = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    deliveryzip = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'Rentals'


class LegacyDriver(models.Model):
    driverid = models.IntegerField(primary_key=True)
    rentalid = models.IntegerField(null=True, blank=True)
    customerid = models.IntegerField(null=True, blank=True)
    primarydrv = models.BooleanField(default=False)

    class Meta:
        db_table = 'Drivers'


class LegacyConsigner(models.Model):
    consignerid = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=255, blank=True)
    fname = models.CharField(max_length=255, blank=True)
    lname = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    # ar = models.CharField(max_length=255, blank=True)
    # aa = models.CharField(max_length=255, blank=True)
    # addr = models.TextField(blank=True)

    class Meta:
        db_table = 'Consigners'


class LegacyConsignmentVehicle(models.Model):
    vehicleid = models.IntegerField(primary_key=True)
    consignerid = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ConsignmentVehicles'


class LegacyConsignmentPayment(models.Model):
    paymentid = models.IntegerField(primary_key=True)
    consignerid = models.IntegerField(null=True, blank=True)
    stamp = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    method = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'ConsignmentPayments'


class LegacyAdmin(models.Model):
    adminid = models.IntegerField(primary_key=True)
    user = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=255, blank=True, db_column='pass')
    createdbyadminid = models.IntegerField(null=True, blank=True)
    authority = models.BooleanField(default=False)
    founder = models.BooleanField(default=False)
    fullname = models.CharField(max_length=150, blank=True)
    email = models.CharField(max_length=150, blank=True)
    about = models.TextField(blank=True)
    acclev = models.IntegerField(null=True, blank=True)
    sleeping = models.BooleanField(default=False)
    stamp = models.DateTimeField(null=True, blank=True)
    picfname = models.CharField(max_length=255, blank=True)
    cell = models.CharField(max_length=20, blank=True)
    twofac = models.IntegerField(null=True, blank=True)
    enable = models.BooleanField(default=False)
    picext = models.CharField(max_length=4, blank=True)
    checkout = models.BooleanField(default=False)
    signoff = models.BooleanField(default=False)

    class Meta:
        db_table = 'admin'


class LegacyNewsItem(models.Model):
    newsid = models.IntegerField(primary_key=True)
    adminid = models.IntegerField(null=True, blank=True)
    stamp = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=255)
    thenews = models.TextField()

    class Meta:
        db_table = 'News'


class LegacyBBSPost(models.Model):
    notesid = models.IntegerField(primary_key=True)
    replytonotesid = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    adminid = models.IntegerField(null=True, blank=True)
    administrator = models.CharField(max_length=150, blank=True)
    stamp = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'notes'


class LegacySiteContent(models.Model):
    adminid = models.IntegerField(primary_key=True)
    about = models.TextField(blank=True)
    policies = models.TextField(blank=True)
    contact = models.TextField(blank=True)
    servicescont = models.TextField(blank=True)
    reservations = models.TextField(blank=True)

    class Meta:
        db_table = 'vars'


class LegacyNewsletterSubscription(models.Model):
    newsletterid = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    confirmed = models.BooleanField(default=False)
    tkt = models.CharField(max_length=30, blank=True)
    ip = models.CharField(max_length=30, blank=True)
    stamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Newsletter'


class LegacyCoupon(models.Model):
    discountid = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'discounts'


class LegacyTollTag(models.Model):
    tolltagid = models.IntegerField(primary_key=True)
    tollaccount = models.IntegerField(null=True, blank=True)
    tagnumber = models.CharField(max_length=32, blank=True)
    vehicleid = models.IntegerField(null=True, blank=True)
    altusage = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'TollTags'


class LegacyGuidedDrive(models.Model):
    joyperfid = models.IntegerField(primary_key=True)
    status = models.IntegerField(null=True, blank=True)
    customerid = models.IntegerField(null=True, blank=True)
    nopax = models.IntegerField(null=True, blank=True)
    nodrv = models.IntegerField(null=True, blank=True)
    nominors = models.IntegerField(null=True, blank=True)
    reqdate = models.DateTimeField(null=True, blank=True)
    bupdate = models.DateTimeField(null=True, blank=True)
    choice1 = models.IntegerField(null=True, blank=True)
    choice2 = models.IntegerField(null=True, blank=True)
    choice3 = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    ournotes = models.TextField(blank=True)
    bigtall = models.BooleanField(default=False)
    coupon = models.CharField(max_length=20, blank=True)
    rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    confcode = models.CharField(max_length=10, blank=True, unique=True, db_index=True)

    class Meta:
        db_table = 'JoyPerf'


class LegacyGiftCertificate(models.Model):
    giftcertid = models.IntegerField(primary_key=True)
    tag = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    issued = models.DateTimeField(null=True, blank=True)
    usename = models.CharField(max_length=255, blank=True)
    ccname = models.CharField(max_length=255, null=True)
    ccaddr = models.CharField(max_length=255, null=True)
    cccity = models.CharField(max_length=255)
    ccstate = models.CharField(max_length=4, null=True)
    cczip = models.CharField(max_length=10, null=True)
    ccnum = models.CharField(max_length=255, blank=True, verbose_name='CC number')
    ccexpyr = models.CharField(max_length=4, blank=True, verbose_name='CC exp year')
    ccexpmo = models.CharField(max_length=2, blank=True, verbose_name='CC exp month')
    cccvv = models.CharField(max_length=6, blank=True, verbose_name='CC CVV')
    cctel = models.CharField(max_length=10, blank=True, verbose_name='CC contact phone')
    email = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=20, blank=True)
    used = models.BooleanField(default=False)
    usedon = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ispaid = models.BooleanField(default=False)
    message = models.CharField(max_length=200, blank=True)
    valuemessage = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'GiftCerts'


class LegacyAdHocPayment(models.Model):
    subpid = models.IntegerField(primary_key=True)
    fullname = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=150, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    ispaid = models.BooleanField(default=False)
    stamp = models.DateTimeField(auto_now_add=True)
    issub = models.BooleanField(default=False)
    paidon = models.DateTimeField(null=True, blank=True)
    item = models.CharField(max_length=255, blank=True)
    mesg = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    ccnum = models.CharField(max_length=255, verbose_name='CC number')
    ccexpyr = models.CharField(max_length=4, verbose_name='CC exp year')
    ccexpmo = models.CharField(max_length=2, verbose_name='CC exp month')
    cccvv = models.CharField(max_length=6, verbose_name='CC CVV')
    addr = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=4, null=True)
    zip = models.CharField(max_length=10, null=True)
    tel = models.CharField(max_length=20, verbose_name='CC contact phone')
    ostate = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, blank=True)

    class Meta:
        db_table = 'subp'


class LegacyCharge(models.Model):
    chargeid = models.IntegerField(primary_key=True)
    uuid = models.CharField(max_length=35, blank=True)
    fullname = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=150, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    capture = models.BooleanField(default=False)
    stamp = models.DateTimeField(auto_now_add=True)
    chargedon = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    ccnum = models.CharField(max_length=255, blank=True, verbose_name='CC number')
    ccexpyr = models.CharField(max_length=4, blank=True, verbose_name='CC exp year')
    ccexpmo = models.CharField(max_length=2, blank=True, verbose_name='CC exp month')
    cccvv = models.CharField(max_length=6, blank=True, verbose_name='CC CVV')
    addr = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=4, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    tel = models.CharField(max_length=20, blank=True, verbose_name='CC contact phone')
    ostate = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, blank=True)
    processorchargeid = models.CharField(max_length=50, blank=True)
    errorcode = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = 'Charges'


class LegacyRedFlag(models.Model):
    tardid = models.IntegerField(primary_key=True)
    stamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    tel = models.CharField(max_length=20, blank=True)
    cel = models.CharField(max_length=20, blank=True)
    addr = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=4, blank=True)
    zip = models.CharField(max_length=10, blank=True)
    email = models.CharField(max_length=255, blank=True)
    licenseno = models.CharField(max_length=30, blank=True)
    licensestate = models.CharField(max_length=4, blank=True)
    ssn = models.CharField(max_length=12, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'tards'


class LegacySurveyResponse(models.Model):
    surveyid = models.IntegerField(primary_key=True)
    customerid = models.IntegerField(null=True, blank=True)
    stamp = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=20, blank=True)
    hearabout = models.TextField(blank=True)
    prirating = models.IntegerField(null=True, blank=True)
    vehiclerating = models.IntegerField(null=True, blank=True)
    howmany = models.IntegerField(null=True, blank=True)
    recommend = models.IntegerField(null=True, blank=True)
    pricing = models.IntegerField(null=True, blank=True)
    email = models.IntegerField(null=True, blank=True)
    types = models.IntegerField(null=True, blank=True)
    newvehicles = models.TextField(blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        db_table = 'surveys'


class LegacyDamage(models.Model):
    damageid = models.IntegerField(primary_key=True)
    vehicleid = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    damageon = models.DateTimeField(null=True, blank=True)
    repairedon = models.DateTimeField(null=True, blank=True)
    repaired = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fault = models.IntegerField(null=True, blank=True)
    billcustomer = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    paidamt = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    paid = models.BooleanField(default=False)
    inhouse = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'Damage'


class LegacyServiceItem(models.Model):
    serviceitemid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'ServiceItems'


class LegacyScheduledService(models.Model):
    serviceid = models.IntegerField(primary_key=True)
    vehicleid = models.IntegerField(null=True, blank=True)
    serviceitemid = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    donestamp = models.DateTimeField(null=True, blank=True)
    donemiles = models.IntegerField(null=True, blank=True)
    nextstamp = models.DateTimeField(null=True, blank=True)
    nextmiles = models.IntegerField(null=True, blank=True)
    due = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'Service'


class LegacyIncidentalService(models.Model):
    servicehistid = models.IntegerField(primary_key=True)
    vehicleid = models.IntegerField(null=True, blank=True)
    stamp = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    mileage = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ServiceHist'


class LegacyEmailImage(models.Model):
    emailpicid = models.IntegerField(primary_key=True)
    ext = models.CharField(max_length=4, blank=True)

    class Meta:
        db_table = 'EmailPics'


class LegacyTweet(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    stamp = models.DateTimeField(null=True, blank=True)
    username = models.CharField(max_length=16, blank=True)
    text = models.TextField(blank=True)
