# Generated by Django 4.0.3 on 2023-08-21 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LegacyAdHocPayment',
            fields=[
                ('subpid', models.IntegerField(primary_key=True, serialize=False)),
                ('fullname', models.CharField(blank=True, max_length=100)),
                ('email', models.CharField(blank=True, max_length=150)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('ispaid', models.BooleanField(default=False)),
                ('stamp', models.DateTimeField(auto_now_add=True)),
                ('issub', models.BooleanField(default=False)),
                ('paidon', models.DateTimeField(blank=True, null=True)),
                ('item', models.CharField(blank=True, max_length=255)),
                ('mesg', models.TextField(blank=True)),
                ('comments', models.TextField(blank=True)),
                ('ccnum', models.CharField(max_length=255, verbose_name='CC number')),
                ('ccexpyr', models.CharField(max_length=4, verbose_name='CC exp year')),
                ('ccexpmo', models.CharField(max_length=2, verbose_name='CC exp month')),
                ('cccvv', models.CharField(max_length=6, verbose_name='CC CVV')),
                ('addr', models.CharField(max_length=255, null=True)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=4, null=True)),
                ('zip', models.CharField(max_length=10, null=True)),
                ('tel', models.CharField(max_length=20, verbose_name='CC contact phone')),
                ('ostate', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=2)),
            ],
            options={
                'db_table': 'subp',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyAdmin',
            fields=[
                ('adminid', models.IntegerField(primary_key=True, serialize=False)),
                ('user', models.CharField(blank=True, max_length=100)),
                ('password', models.CharField(blank=True, db_column='pass', max_length=255)),
                ('createdbyadminid', models.IntegerField(blank=True, null=True)),
                ('authority', models.BooleanField(default=False)),
                ('founder', models.BooleanField(default=False)),
                ('fullname', models.CharField(blank=True, max_length=150)),
                ('email', models.CharField(blank=True, max_length=150)),
                ('about', models.TextField(blank=True)),
                ('acclev', models.IntegerField(blank=True, null=True)),
                ('sleeping', models.BooleanField(default=False)),
                ('stamp', models.DateTimeField(blank=True, null=True)),
                ('picfname', models.CharField(blank=True, max_length=255)),
                ('cell', models.CharField(blank=True, max_length=20)),
                ('twofac', models.IntegerField(blank=True, null=True)),
                ('enable', models.BooleanField(default=False)),
                ('picext', models.CharField(blank=True, max_length=4)),
                ('checkout', models.BooleanField(default=False)),
                ('signoff', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'admin',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyBBSPost',
            fields=[
                ('notesid', models.IntegerField(primary_key=True, serialize=False)),
                ('replytonotesid', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('adminid', models.IntegerField(blank=True, null=True)),
                ('administrator', models.CharField(blank=True, max_length=150)),
                ('stamp', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'notes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyCharge',
            fields=[
                ('chargeid', models.IntegerField(primary_key=True, serialize=False)),
                ('uuid', models.CharField(blank=True, max_length=35)),
                ('fullname', models.CharField(blank=True, max_length=100)),
                ('email', models.CharField(blank=True, max_length=150)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('capture', models.BooleanField(default=False)),
                ('stamp', models.DateTimeField(auto_now_add=True)),
                ('chargedon', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('ccnum', models.CharField(blank=True, max_length=255, verbose_name='CC number')),
                ('ccexpyr', models.CharField(blank=True, max_length=4, verbose_name='CC exp year')),
                ('ccexpmo', models.CharField(blank=True, max_length=2, verbose_name='CC exp month')),
                ('cccvv', models.CharField(blank=True, max_length=6, verbose_name='CC CVV')),
                ('addr', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255)),
                ('state', models.CharField(blank=True, max_length=4, null=True)),
                ('zip', models.CharField(blank=True, max_length=10, null=True)),
                ('tel', models.CharField(blank=True, max_length=20, verbose_name='CC contact phone')),
                ('ostate', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=2)),
                ('processorchargeid', models.CharField(blank=True, max_length=50)),
                ('errorcode', models.CharField(blank=True, max_length=30)),
            ],
            options={
                'db_table': 'Charges',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyConsigner',
            fields=[
                ('consignerid', models.IntegerField(primary_key=True, serialize=False)),
                ('email', models.CharField(blank=True, max_length=255)),
                ('fname', models.CharField(blank=True, max_length=255)),
                ('lname', models.CharField(blank=True, max_length=255)),
                ('password', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'Consigners',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyConsignmentPayment',
            fields=[
                ('paymentid', models.IntegerField(primary_key=True, serialize=False)),
                ('consignerid', models.IntegerField(blank=True, null=True)),
                ('stamp', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('method', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'db_table': 'ConsignmentPayments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyConsignmentVehicle',
            fields=[
                ('vehicleid', models.IntegerField(primary_key=True, serialize=False)),
                ('consignerid', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ConsignmentVehicles',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyCoupon',
            fields=[
                ('discountid', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(db_index=True, max_length=50, unique=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
            ],
            options={
                'db_table': 'discounts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyCustFront',
            fields=[
                ('customerid', models.IntegerField(primary_key=True, serialize=False)),
                ('email', models.CharField(blank=True, max_length=255)),
                ('password', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'CustFront',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyCustomer',
            fields=[
                ('customerid', models.IntegerField(primary_key=True, serialize=False)),
                ('createdon', models.DateTimeField(auto_now_add=True)),
                ('fname', models.CharField(max_length=255)),
                ('lname', models.CharField(max_length=255)),
                ('addr', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=255)),
                ('state', models.CharField(blank=True, max_length=4)),
                ('zip', models.CharField(blank=True, max_length=10)),
                ('hphone', models.CharField(blank=True, max_length=20)),
                ('wphone', models.CharField(blank=True, max_length=20)),
                ('mphone', models.CharField(blank=True, max_length=20)),
                ('fax', models.CharField(blank=True, max_length=20)),
                ('dob', models.DateTimeField(blank=True, null=True)),
                ('email', models.CharField(blank=True, max_length=255)),
                ('licenseno', models.CharField(blank=True, max_length=30)),
                ('licensestate', models.CharField(blank=True, max_length=4)),
                ('licensehist', models.TextField(blank=True)),
                ('insco', models.CharField(blank=True, max_length=255)),
                ('inspolnum', models.CharField(blank=True, max_length=255)),
                ('inscotel', models.CharField(blank=True, max_length=20)),
                ('coverage', models.BooleanField(default=False)),
                ('rentednum', models.IntegerField(blank=True, null=True)),
                ('ccnum', models.CharField(blank=True, max_length=255, verbose_name='CC1 number')),
                ('ccexpyr', models.CharField(blank=True, max_length=4, verbose_name='CC1 exp year')),
                ('ccexpmo', models.CharField(blank=True, max_length=2, verbose_name='CC1 exp month')),
                ('cccvv', models.CharField(blank=True, max_length=6, verbose_name='CC1 CVV')),
                ('cctel', models.CharField(blank=True, max_length=20, verbose_name='CC1 contact phone')),
                ('cc2num', models.CharField(blank=True, max_length=255, verbose_name='CC1 number')),
                ('cc2expyr', models.CharField(blank=True, max_length=4, verbose_name='CC1 exp year')),
                ('cc2expmo', models.CharField(blank=True, max_length=2, verbose_name='CC1 exp month')),
                ('cc2cvv', models.CharField(blank=True, max_length=6, verbose_name='CC1 CVV')),
                ('cc2tel', models.CharField(blank=True, max_length=20, verbose_name='CC1 contact phone')),
                ('remarks', models.TextField(blank=True)),
                ('rating', models.IntegerField(blank=True, null=True)),
                ('driverskill', models.IntegerField(blank=True, null=True)),
                ('discount', models.CharField(blank=True, max_length=2)),
                ('musicgenre', models.IntegerField(blank=True, null=True)),
                ('musicfav', models.CharField(blank=True, max_length=255)),
                ('firsttime', models.BooleanField(default=True)),
                ('DriversClub', models.IntegerField(blank=True, null=True)),
                ('nomail', models.BooleanField(default=False)),
                ('ban', models.BooleanField(default=False)),
                ('surveydone', models.BooleanField(default=False)),
                ('regip', models.CharField(blank=True, max_length=30, verbose_name='Registration IP')),
                ('reglong', models.FloatField(blank=True, null=True, verbose_name='Registration longitude')),
                ('reglat', models.FloatField(blank=True, null=True, verbose_name='Registration latitude')),
            ],
            options={
                'db_table': 'Customers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyDamage',
            fields=[
                ('damageid', models.IntegerField(primary_key=True, serialize=False)),
                ('vehicleid', models.IntegerField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('damageon', models.DateTimeField(blank=True, null=True)),
                ('repairedon', models.DateTimeField(blank=True, null=True)),
                ('repaired', models.BooleanField(default=False)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('fault', models.IntegerField(blank=True, null=True)),
                ('billcustomer', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('paidamt', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('inhouse', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'Damage',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyDriver',
            fields=[
                ('driverid', models.IntegerField(primary_key=True, serialize=False)),
                ('rentalid', models.IntegerField(blank=True, null=True)),
                ('customerid', models.IntegerField(blank=True, null=True)),
                ('primarydrv', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Drivers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyEmailImage',
            fields=[
                ('emailpicid', models.IntegerField(primary_key=True, serialize=False)),
                ('ext', models.CharField(blank=True, max_length=4)),
            ],
            options={
                'db_table': 'EmailPics',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyGiftCertificate',
            fields=[
                ('giftcertid', models.IntegerField(primary_key=True, serialize=False)),
                ('tag', models.CharField(blank=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('issued', models.DateTimeField(blank=True, null=True)),
                ('usename', models.CharField(blank=True, max_length=255)),
                ('ccname', models.CharField(max_length=255, null=True)),
                ('ccaddr', models.CharField(max_length=255, null=True)),
                ('cccity', models.CharField(max_length=255)),
                ('ccstate', models.CharField(max_length=4, null=True)),
                ('cczip', models.CharField(max_length=10, null=True)),
                ('ccnum', models.CharField(blank=True, max_length=255, verbose_name='CC number')),
                ('ccexpyr', models.CharField(blank=True, max_length=4, verbose_name='CC exp year')),
                ('ccexpmo', models.CharField(blank=True, max_length=2, verbose_name='CC exp month')),
                ('cccvv', models.CharField(blank=True, max_length=6, verbose_name='CC CVV')),
                ('cctel', models.CharField(blank=True, max_length=10, verbose_name='CC contact phone')),
                ('email', models.CharField(max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('used', models.BooleanField(default=False)),
                ('usedon', models.DateField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('ispaid', models.BooleanField(default=False)),
                ('message', models.CharField(blank=True, max_length=200)),
                ('valuemessage', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'GiftCerts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyGuidedDrive',
            fields=[
                ('joyperfid', models.IntegerField(primary_key=True, serialize=False)),
                ('status', models.IntegerField(blank=True, null=True)),
                ('customerid', models.IntegerField(blank=True, null=True)),
                ('nopax', models.IntegerField(blank=True, null=True)),
                ('nodrv', models.IntegerField(blank=True, null=True)),
                ('nominors', models.IntegerField(blank=True, null=True)),
                ('reqdate', models.DateTimeField(blank=True, null=True)),
                ('bupdate', models.DateTimeField(blank=True, null=True)),
                ('choice1', models.IntegerField(blank=True, null=True)),
                ('choice2', models.IntegerField(blank=True, null=True)),
                ('choice3', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('ournotes', models.TextField(blank=True)),
                ('bigtall', models.BooleanField(default=False)),
                ('coupon', models.CharField(blank=True, max_length=20)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('type', models.IntegerField(blank=True, null=True)),
                ('confcode', models.CharField(blank=True, db_index=True, max_length=10, unique=True)),
            ],
            options={
                'db_table': 'JoyPerf',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyIncidentalService',
            fields=[
                ('servicehistid', models.IntegerField(primary_key=True, serialize=False)),
                ('vehicleid', models.IntegerField(blank=True, null=True)),
                ('stamp', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('mileage', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ServiceHist',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyNewsItem',
            fields=[
                ('newsid', models.IntegerField(primary_key=True, serialize=False)),
                ('adminid', models.IntegerField(blank=True, null=True)),
                ('stamp', models.DateTimeField(auto_now_add=True)),
                ('subject', models.CharField(max_length=255)),
                ('thenews', models.TextField()),
            ],
            options={
                'db_table': 'News',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyNewsletterSubscription',
            fields=[
                ('newsletterid', models.IntegerField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('confirmed', models.BooleanField(default=False)),
                ('tkt', models.CharField(blank=True, max_length=30)),
                ('ip', models.CharField(blank=True, max_length=30)),
                ('stamp', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Newsletter',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyRedFlag',
            fields=[
                ('tardid', models.IntegerField(primary_key=True, serialize=False)),
                ('stamp', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('tel', models.CharField(blank=True, max_length=20)),
                ('cel', models.CharField(blank=True, max_length=20)),
                ('addr', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255)),
                ('state', models.CharField(blank=True, max_length=4)),
                ('zip', models.CharField(blank=True, max_length=10)),
                ('email', models.CharField(blank=True, max_length=255)),
                ('licenseno', models.CharField(blank=True, max_length=30)),
                ('licensestate', models.CharField(blank=True, max_length=4)),
                ('ssn', models.CharField(blank=True, max_length=12)),
                ('remarks', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'tards',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyRental',
            fields=[
                ('rentalid', models.IntegerField(primary_key=True, serialize=False)),
                ('customerid', models.IntegerField(blank=True, null=True)),
                ('vehicleid', models.IntegerField(blank=True, null=True)),
                ('reservdate', models.DateTimeField(auto_now_add=True)),
                ('confirm', models.BooleanField(default=False)),
                ('numdays', models.IntegerField(blank=True, null=True)),
                ('dateout', models.DateTimeField(blank=True, null=True)),
                ('dateback', models.DateTimeField(blank=True, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('drivers', models.IntegerField(blank=True, null=True)),
                ('milesinc', models.IntegerField(blank=True, null=True)),
                ('xtramiles', models.IntegerField(blank=True, null=True)),
                ('milesout', models.IntegerField(blank=True, null=True)),
                ('milesback', models.IntegerField(blank=True, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
                ('abuse', models.TextField(blank=True)),
                ('damageout', models.TextField(blank=True)),
                ('damagein', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('coupon', models.CharField(blank=True, max_length=30)),
                ('bgcheck', models.BooleanField(default=False)),
                ('ournotes', models.TextField(blank=True)),
                ('couponisgood', models.BooleanField(default=False)),
                ('depchargedon', models.DateTimeField(blank=True, null=True)),
                ('depamount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('deprefundon', models.DateTimeField(blank=True, null=True)),
                ('deprefundamount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('discount', models.IntegerField(blank=True, null=True)),
                ('extenddays', models.IntegerField(blank=True, null=True)),
                ('confcode', models.CharField(blank=True, db_index=True, max_length=10, unique=True)),
                ('reglat', models.FloatField(blank=True, null=True)),
                ('reglong', models.FloatField(blank=True, null=True)),
                ('iphone', models.BooleanField(default=False)),
                ('markid', models.IntegerField(blank=True, null=True)),
                ('delivery', models.BooleanField(default=False)),
                ('taxpct', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('deliveryzip', models.CharField(blank=True, max_length=10)),
            ],
            options={
                'db_table': 'Rentals',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyReservation',
            fields=[
                ('reservationid', models.IntegerField(primary_key=True, serialize=False)),
                ('customerid', models.IntegerField(blank=True, null=True)),
                ('vehicleid', models.IntegerField(blank=True, null=True)),
                ('reservdate', models.DateTimeField(auto_now_add=True)),
                ('numdays', models.IntegerField(blank=True, null=True)),
                ('dateout', models.DateTimeField(blank=True, null=True)),
                ('dateback', models.DateTimeField(blank=True, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('drivers', models.IntegerField(blank=True, null=True)),
                ('milesinc', models.IntegerField(blank=True, null=True)),
                ('xtramiles', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('coupon', models.CharField(blank=True, max_length=30)),
                ('status', models.IntegerField(blank=True, null=True)),
                ('depamount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('confcode', models.CharField(blank=True, db_index=True, max_length=10, unique=True)),
                ('iphone', models.BooleanField(default=False)),
                ('markid', models.IntegerField(blank=True, null=True)),
                ('delivery', models.BooleanField(default=False)),
                ('taxpct', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('deliveryzip', models.CharField(blank=True, max_length=10)),
            ],
            options={
                'db_table': 'Reservations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyScheduledService',
            fields=[
                ('serviceid', models.IntegerField(primary_key=True, serialize=False)),
                ('vehicleid', models.IntegerField(blank=True, null=True)),
                ('serviceitemid', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('donestamp', models.DateTimeField(blank=True, null=True)),
                ('donemiles', models.IntegerField(blank=True, null=True)),
                ('nextstamp', models.DateTimeField(blank=True, null=True)),
                ('nextmiles', models.IntegerField(blank=True, null=True)),
                ('due', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'Service',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyServiceItem',
            fields=[
                ('serviceitemid', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'ServiceItems',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacySiteContent',
            fields=[
                ('adminid', models.IntegerField(primary_key=True, serialize=False)),
                ('about', models.TextField(blank=True)),
                ('policies', models.TextField(blank=True)),
                ('contact', models.TextField(blank=True)),
                ('servicescont', models.TextField(blank=True)),
                ('reservations', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'vars',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacySurveyResponse',
            fields=[
                ('surveyid', models.IntegerField(primary_key=True, serialize=False)),
                ('customerid', models.IntegerField(blank=True, null=True)),
                ('stamp', models.DateTimeField(auto_now_add=True)),
                ('ip', models.CharField(blank=True, max_length=20)),
                ('hearabout', models.TextField(blank=True)),
                ('prirating', models.IntegerField(blank=True, null=True)),
                ('vehiclerating', models.IntegerField(blank=True, null=True)),
                ('howmany', models.IntegerField(blank=True, null=True)),
                ('recommend', models.IntegerField(blank=True, null=True)),
                ('pricing', models.IntegerField(blank=True, null=True)),
                ('email', models.IntegerField(blank=True, null=True)),
                ('types', models.IntegerField(blank=True, null=True)),
                ('newvehicles', models.TextField(blank=True)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'surveys',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyTollTag',
            fields=[
                ('tolltagid', models.IntegerField(primary_key=True, serialize=False)),
                ('tollaccount', models.IntegerField(blank=True, null=True)),
                ('tagnumber', models.CharField(blank=True, max_length=32)),
                ('vehicleid', models.IntegerField(blank=True, null=True)),
                ('altusage', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'TollTags',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyTweet',
            fields=[
                ('id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('stamp', models.DateTimeField(blank=True, null=True)),
                ('username', models.CharField(blank=True, max_length=16)),
                ('text', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'tweets',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyVehicle',
            fields=[
                ('vehicleid', models.IntegerField(primary_key=True, serialize=False)),
                ('make', models.CharField(blank=True, max_length=255)),
                ('model', models.CharField(blank=True, max_length=255)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('type', models.IntegerField(blank=True, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
                ('plate', models.CharField(blank=True, max_length=10)),
                ('vin', models.CharField(blank=True, max_length=50)),
                ('mileage', models.IntegerField(blank=True, null=True)),
                ('damage', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('policyno', models.CharField(blank=True, max_length=255)),
                ('policyco', models.CharField(blank=True, max_length=255)),
                ('policytel', models.CharField(blank=True, max_length=30)),
                ('weighting', models.IntegerField(blank=True, null=True)),
                ('redirect', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Vehicles',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyVehicleFront',
            fields=[
                ('vehicleid', models.IntegerField(primary_key=True, serialize=False)),
                ('type', models.IntegerField(blank=True, null=True)),
                ('status', models.IntegerField(null=True)),
                ('hp', models.IntegerField(blank=True, null=True)),
                ('tq', models.IntegerField(blank=True, null=True)),
                ('topspeed', models.IntegerField(blank=True, null=True)),
                ('trans', models.IntegerField(blank=True, null=True)),
                ('gears', models.IntegerField(blank=True, null=True)),
                ('location', models.IntegerField(blank=True, null=True)),
                ('tightfit', models.BooleanField(default=False)),
                ('blurb', models.TextField(blank=True)),
                ('specs', models.TextField(blank=True)),
                ('origin', models.CharField(blank=True, max_length=2)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('disc2day', models.IntegerField(blank=True, help_text='Percent', null=True, verbose_name='2-day discount')),
                ('disc3day', models.IntegerField(blank=True, help_text='Percent', null=True, verbose_name='3-day discount')),
                ('disc7day', models.IntegerField(blank=True, help_text='Percent', null=True, verbose_name='7-day discount')),
                ('deposit', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('milesinc', models.IntegerField(blank=True, help_text='Per day', null=True)),
            ],
            options={
                'db_table': 'VehiclesFront',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyVehiclePic',
            fields=[
                ('vpicsid', models.IntegerField(primary_key=True, serialize=False)),
                ('vehicleid', models.IntegerField(blank=True, null=True)),
                ('fext', models.CharField(blank=True, max_length=4)),
                ('isfirst', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'VPics',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LegacyVehicleVid',
            fields=[
                ('vvidsid', models.IntegerField(primary_key=True, serialize=False)),
                ('vehicleid', models.IntegerField(blank=True, null=True)),
                ('fext', models.CharField(blank=True, max_length=4)),
                ('length', models.CharField(blank=True, max_length=10)),
                ('blurb', models.TextField(blank=True)),
                ('isfirst', models.BooleanField(default=False)),
                ('thumbext', models.CharField(blank=True, max_length=4)),
            ],
            options={
                'db_table': 'VVids',
                'managed': False,
            },
        ),
    ]