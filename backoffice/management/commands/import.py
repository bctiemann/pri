import MySQLdb
import logging
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus, TransmissionType, Location
from users.models import Customer, User, MusicGenre
from pri.cipher import AESCipher

logger = logging.getLogger(__name__)

VEHICLE_TYPE_MAP = {
    1: VehicleType.CAR,
    2: VehicleType.BIKE,
    3: VehicleType.TRACK,
}

TRANSMISSION_TYPE_MAP = {
    1: TransmissionType.MANUAL,
    2: TransmissionType.SEMI_AUTO,
    3: TransmissionType.AUTO,
}

LOCATION_MAP = {
    1: Location.NEW_YORK,
    2: Location.TAMPA,
}


class Command(BaseCommand):

    enabled = {
        # 'do_vehicles': True,
        'do_customers': True,
    }

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key',)
        parser.add_argument('--clear_existing', dest='clear_existing', default=False, action='store_true',)

    def decrypt(self, value):
        return self.aes.decrypt(value) if value else ''

    def handle(self, *args, **options):
        key = options.get('key', None)
        if not key:
            print('Missing --key <key>')
            raise SystemExit

        self.aes = AESCipher(key)

        legacy_db = settings.DATABASES['default_legacy']
        legacy_front_db = settings.DATABASES['front_legacy']
        db = MySQLdb.connect(
            passwd=legacy_db['PASSWORD'],
            db=legacy_db['NAME'],
            host=legacy_db['HOST'],
            user=legacy_db['USER'],
            charset=legacy_db['OPTIONS']['charset'],
        )
        back_cursor = db.cursor(MySQLdb.cursors.DictCursor)
        front_db = MySQLdb.connect(
            passwd=legacy_front_db['PASSWORD'],
            db=legacy_front_db['NAME'],
            host=legacy_front_db['HOST'],
            user=legacy_front_db['USER'],
            charset=legacy_front_db['OPTIONS']['charset'],
        )
        front_cursor = front_db.cursor(MySQLdb.cursors.DictCursor)

        clear_existing = options.get('clear_existing')

        if 'do_vehicles' in self.enabled:
            if clear_existing:
                Vehicle.objects.all().delete()
                VehicleMarketing.objects.all().delete()
            back_cursor.execute("""SELECT * FROM Vehicles""")
            for old in back_cursor.fetchall():
                print(old['make'], old['model'])
                new = Vehicle.objects.create(
                    make=old['make'],
                    model=old['model'],
                    year=old['year'],
                    vehicle_type=VEHICLE_TYPE_MAP.get(old['type']),
                    status=0,
                    plate=old['plate'],
                    vin=old['vin'],
                    mileage=old['mileage'],
                    damage=old['damage'],
                    notes=old['notes'],
                    policy_number=self.decrypt(old['policyno']),
                    policy_company=old['policyco'],
                    policy_phone=old['policytel'],
                    weighting=old['weighting'],
                )
                front_cursor.execute("""SELECT * FROM VehiclesFront where vehicleid=%s""", old['vehicleid'])
                old_front = front_cursor.fetchone()
                new_front = VehicleMarketing.objects.create(
                    vehicle_id=new.id,
                    make=old['make'],
                    model=old['model'],
                    year=old['year'],
                    vehicle_type=VEHICLE_TYPE_MAP.get(old['type']),
                    status=old_front['status'],
                    horsepower=old_front['hp'],
                    torque=old_front['tq'],
                    top_speed=old_front['topspeed'],
                    transmission_type=TRANSMISSION_TYPE_MAP.get(old_front['trans']),
                    gears=old_front['gears'],
                    location=LOCATION_MAP.get(old_front['location']),
                    tight_fit=old_front['tightfit'],
                    blurb=old_front['blurb'],
                    specs=json.loads(old_front['specs']),
                    origin_country='GB' if old_front['origin'] == 'UK' else old_front['origin'],
                    price_per_day=old_front['price'],
                    discount_2_day=old_front['disc2day'],
                    discount_3_day=old_front['disc3day'],
                    discount_7_day=old_front['disc7day'],
                    deposit=old_front['deposit'],
                    miles_included=old_front['milesinc'],
                )
                new.status = old_front['status']
                new.save()

        if 'do_customers' in self.enabled:
            if clear_existing:
                for customer in Customer.objects.all():
                    if customer.user and not customer.user.is_admin:
                        customer.user.delete()
                    customer.delete()
            back_cursor.execute("""SELECT * FROM Customers""")
            for old in back_cursor.fetchall():
                print(old['fname'], old['lname'])
                front_cursor.execute("""SELECT * FROM CustFront where email=%s""", old['email'])
                old_front = front_cursor.fetchone()
                password = self.decrypt(old_front['password'])
                user = None
                if old['email']:
                    try:
                        user = User.objects.get(email=old['email'])
                    except User.DoesNotExist:
                        user = User.objects.create_user(
                            email=old['email'],
                            password=password,
                        )
                    user.save()
                try:
                    customer = Customer.objects.get(user__isnull=False, user=user)
                except Customer.DoesNotExist:
                    try:
                        music_genre = MusicGenre.objects.get(pk=old['musicgenre'])
                    except MusicGenre.DoesNotExist:
                        music_genre = None
                    new = Customer.objects.create(
                        user=user,
                        first_name=old['fname'],
                        last_name=old['lname'],
                        address_line_1=self.decrypt(old['addr']),
                        address_line_2='',
                        city=old['city'],
                        state=old['state'],
                        zip=old['zip'],
                        date_of_birth=old['dob'],
                        license_number=old['licenseno'] or '',
                        license_state=old['licensestate'] or '',
                        license_history=old['licensehist'] or '',
                        insurance_company=old['insco'] or '',
                        insurance_policy_number=old['inspolnum'] or '',
                        coverage_verified=bool(old['coverage']),
                        cc_number=self.decrypt(old['ccnum']),
                        cc_exp_yr=old['ccexpyr'] or '',
                        cc_exp_mo=old['ccexpmo'] or '',
                        cc_cvv=old['cccvv'] or '',
                        cc2_number=self.decrypt(old['cc2num']),
                        cc2_exp_yr=old['cc2expyr'] or '',
                        cc2_exp_mo=old['cc2expmo'] or '',
                        cc2_cvv=old['cc2cvv'] or '',
                        rentals_count=old['rentednum'],
                        remarks=self.decrypt(old['remarks']),
                        driver_skill=old['driverskill'],
                        discount=int(old['discount']) if old['discount'].isdigit() else None,
                        music_genre=music_genre,
                        first_time=bool(old['firsttime']),
                        drivers_club=bool(old['DriversClub']),
                        no_email=bool(old['nomail']),
                        ban=bool(old['ban']),
                        survey_done=bool(old['surveydone']),
                        registration_ip=old['regip'],
                        registration_lat=old['reglat'],
                        registration_long=old['reglong'],
                    )
                    try:
                        new.home_phone = old['hphone']
                        new.save()
                    except ValueError:
                        pass
                    try:
                        new.mobile_phone = old['mphone']
                        new.save()
                    except ValueError:
                        pass
                    try:
                        new.work_phone = old['wphone']
                        new.save()
                    except ValueError:
                        pass
                    try:
                        new.fax = old['fax']
                        new.save()
                    except ValueError:
                        pass
                    try:
                        new.insurance_company_phone = old['inscotel'] or ''
                        new.save()
                    except ValueError:
                        pass
                    try:
                        new.cc_phone = old['cctel'] or ''
                        new.save()
                    except ValueError:
                        pass
                    try:
                        new.cc2_phone = old['cc2tel'] or ''
                        new.save()
                    except ValueError:
                        pass
