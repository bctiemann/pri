import MySQLdb
import logging
import json
import requests
from html2bbcode import parser

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File

from marketing.models import NewsItem
from fleet.models import Vehicle, VehicleMarketing, VehiclePicture, TransmissionType, Location, get_vehicle_picture_path
from users.models import Customer, Employee, User, MusicGenre
from sales.models import Reservation
from consignment.models import Consigner
from pri.cipher import AESCipher

logger = logging.getLogger(__name__)


TRANSMISSION_TYPE_MAP = {
    1: TransmissionType.MANUAL,
    2: TransmissionType.SEMI_AUTO,
    3: TransmissionType.AUTO,
}

LOCATION_MAP = {
    1: Location.NEW_YORK,
    2: Location.TAMPA,
}

SITE_ROOT = 'http://172.16.0.5/prinew/root/'
SITE_SEC_ROOT = 'http://172.16.0.5/prinew/secure/'


class Command(BaseCommand):

    enabled = {
        # 'do_vehicles': True,
        # 'do_vehicle_pics': True,
        # 'do_customers': True,
        # 'do_reservations': True,
        # 'do_consigners': True,
        # 'do_consignmentvehicles': True,
        # 'do_admins': True,
        'do_newsitems': True,
    }

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key',)
        parser.add_argument('--clear_existing', dest='clear_existing', default=False, action='store_true',)
        parser.add_argument('--map', '--config', default=None, help='map.conf file for html2bbcode')

    def decrypt(self, value):
        return self.aes.decrypt(value) if value else ''

    def get_image_tempfile(self, url):
        r = requests.get(url)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()
        return img_temp

    def import_showcase_image(self, vehicle_marketing, vehicle_id):
        url = f'{SITE_ROOT}images/{vehicle_id}-showcase.jpg'
        image_tempfile = self.get_image_tempfile(url)
        vehicle_marketing.showcase_image.save(get_vehicle_picture_path(None, 'temp.jpg'), File(image_tempfile))
        vehicle_marketing.save()

    def import_thumbnail_image(self, vehicle_marketing, vehicle_id):
        url = f'{SITE_ROOT}images/{vehicle_id}-thumb.jpg'
        image_tempfile = self.get_image_tempfile(url)
        vehicle_marketing.thumbnail_image.save(get_vehicle_picture_path(None, 'temp.jpg'), File(image_tempfile))
        vehicle_marketing.save()

    def import_vehicle_picture_image(self, vehicle_picture, vehicle_pic_id, ext):
        url = f'{SITE_ROOT}pics/PRI-{vehicle_pic_id}.{ext}'
        image_tempfile = self.get_image_tempfile(url)
        vehicle_picture.image.save(get_vehicle_picture_path(None, f'temp.{ext}'), File(image_tempfile))
        thumb_url = f'{SITE_ROOT}pics/PRI-{vehicle_pic_id}.thumb.{ext}'
        thumb_tempfile = self.get_image_tempfile(thumb_url)
        vehicle_picture.thumbnail.save(get_vehicle_picture_path(None, f'temp.{ext}'), File(thumb_tempfile))
        vehicle_picture.save()

    def import_inspection_image(self, vehicle_marketing, vehicle_id):
        url = f'{SITE_SEC_ROOT}spork/carcheck/{vehicle_id}.png'
        image_tempfile = self.get_image_tempfile(url)
        vehicle_marketing.inspection_image.save(get_vehicle_picture_path(None, 'temp.png'), File(image_tempfile))
        vehicle_marketing.save()

    def handle(self, *args, **options):
        key = options.get('key', None)
        if not key:
            print('Missing --key <key>')
            raise SystemExit

        self.aes = AESCipher(key)

        self.bbcode_parser = parser.HTML2BBCode(options.get('map'))

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
                slug = slugify(f'{old["make"]}-{old["model"]}')
                new = Vehicle.objects.create(
                    id=old['vehicleid'],
                    make=old['make'],
                    model=old['model'],
                    year=old['year'],
                    slug=slug,
                    vehicle_type=old['type'],
                    status=0,
                    plate=old['plate'],
                    vin=old['vin'],
                    mileage=old['mileage'],
                    damage=old['damage'],
                    notes=old['notes'],
                    policy_number=self.decrypt(old['policyno']),
                    policy_company=old['policyco'],
                    weighting=old['weighting'],
                )
                try:
                    new.policy_phone = old['policytel']
                    new.save()
                except ValueError:
                    new.policy_phone = ''
                front_cursor.execute("""SELECT * FROM VehiclesFront where vehicleid=%s""", old['vehicleid'])
                old_front = front_cursor.fetchone()
                parsed_blurb = bbcode_parser.feed(old_front['blurb'])
                new_front = VehicleMarketing.objects.create(
                    id=new.id,
                    vehicle_id=new.id,
                    slug=slug,
                    weighting=old['weighting'],
                    make=old['make'],
                    model=old['model'],
                    year=old['year'],
                    vehicle_type=old['type'],
                    status=old_front['status'],
                    horsepower=old_front['hp'],
                    torque=old_front['tq'],
                    top_speed=old_front['topspeed'],
                    transmission_type=TRANSMISSION_TYPE_MAP.get(old_front['trans']),
                    gears=old_front['gears'],
                    location=LOCATION_MAP.get(old_front['location']),
                    tight_fit=old_front['tightfit'],
                    blurb=parsed_blurb,
                    specs=json.loads(old_front['specs']),
                    origin_country='GB' if old_front['origin'] == 'UK' else old_front['origin'],
                    price_per_day=old_front['price'],
                    discount_2_day=old_front['disc2day'],
                    discount_3_day=old_front['disc3day'],
                    discount_7_day=old_front['disc7day'],
                    security_deposit=old_front['deposit'],
                    miles_included=old_front['milesinc'],
                )
                new.status = old_front['status']
                new.save()
                self.import_showcase_image(new_front, old['vehicleid'])
                self.import_thumbnail_image(new_front, old['vehicleid'])
                self.import_inspection_image(new_front, old['vehicleid'])

        if 'do_vehicle_pics' in self.enabled:
            if clear_existing:
                VehiclePicture.objects.all().delete()
            front_cursor.execute("""SELECT * FROM VPics""")
            for old in front_cursor.fetchall():
                print(old)
                try:
                    vehicle = Vehicle.objects.get(id=old['vehicleid'])
                except Vehicle.DoesNotExist:
                    continue
                try:
                    vehicle_marketing = VehicleMarketing.objects.get(vehicle_id=vehicle.id)
                except VehicleMarketing.DoesNotExist:
                    continue
                print(vehicle_marketing)
                new = VehiclePicture.objects.create(
                    vehicle_marketing=vehicle_marketing,
                    is_first=old['isfirst'],
                )
                self.import_vehicle_picture_image(new, old['vpicsid'], old['fext'])

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
                    music_genre = MusicGenre.objects.filter(pk=old['musicgenre']).first()
                    new = Customer.objects.create(
                        id=old['customerid'],
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
                        discount_pct=int(old['discount']) if old['discount'].isdigit() else None,
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

        if 'do_reservations' in self.enabled:
            if clear_existing:
                Reservation.objects.all().delete()
            back_cursor.execute("""SELECT * FROM Reservations""")
            for old in back_cursor.fetchall():
                print(old['reservationid'])
                customer = Customer.objects.filter(id=old['customerid']).first()
                vehicle = Vehicle.objects.filter(id=old['vehicleid']).first()
                new = Reservation.objects.create(
                    id=old['reservationid'],
                    customer=customer,
                    vehicle=vehicle,
                    out_at=old['dateout'],
                    back_at=old['dateback'],
                    rate=old['rate'],
                    drivers=old['drivers'],
                    miles_included=old['milesinc'],
                    extra_miles=old['xtramiles'],
                    customer_notes=old['notes'],
                    coupon_code=old['coupon'],
                    status=old['status'],
                    deposit_amount=old['depamount'],
                    confirmation_code=old['confcode'],
                    delivery_required=bool(old['delivery']),
                    tax_percent=old['taxpct'],
                    delivery_zip=old['deliveryzip'],
                )
                new.reserved_at = old['reservdate']
                new.save()

        if 'do_consigners' in self.enabled:
            if clear_existing:
                Consigner.objects.all().delete()
            back_cursor.execute("""SELECT * FROM Consigners""")
            for old in back_cursor.fetchall():
                print(f"{old['fname']} {old['lname']}")
                password = self.decrypt(old['password'])
                notes = self.decrypt(old['notes'])
                account_number = self.decrypt(old['aa'])
                routing_number = self.decrypt(old['ar'])
                address = self.decrypt(old['addr'])
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
                new = Consigner.objects.create(
                    id=old['consignerid'],
                    user=user,
                    first_name=old['fname'],
                    last_name=old['lname'],
                    notes=notes,
                    account_number=account_number,
                    routing_number=routing_number,
                    address=address,
                )

        if 'do_consignmentvehicles' in self.enabled:
            back_cursor.execute("""SELECT * FROM ConsignmentVehicles""")
            for old in back_cursor.fetchall():
                print(old)
                consigner = Consigner.objects.filter(id=old['consignerid']).first()
                vehicle = Vehicle.objects.filter(id=old['vehicleid']).first()
                if vehicle and consigner:
                    vehicle.external_owner = consigner
                    vehicle.save()

        if 'do_admins' in self.enabled:
            if clear_existing:
                Employee.objects.all().delete()
            back_cursor.execute("""SELECT * FROM admin""")
            for old in back_cursor.fetchall():
                print(old)
                try:
                    password = self.decrypt(old['pass'])
                except ValueError:
                    password = old['pass']
                name_parts = old['fullname'].split(' ')
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                user = None
                if old['email']:
                    try:
                        user = User.objects.get(email=old['email'])
                    except User.DoesNotExist:
                        user = User.objects.create_user(
                            email=old['email'],
                            password=password,
                        )
                    user.id_orig = old['adminid']
                    user.notes = old['about']
                    user.created_at = old['stamp']
                    user.is_backoffice = True
                    user.is_admin = old['acclev'] == Employee.AccessLevel.ADMIN.value
                    user.save()
                    employee = Employee.objects.create(
                        user=user,
                        first_name=first_name,
                        last_name=last_name,
                        access_level=old['acclev'],
                    )
                    employee.created_at = old['stamp']
                    employee.save()

        if 'do_newsitems' in self.enabled:
            if clear_existing:
                NewsItem.objects.all().delete()
            front_cursor.execute("""SELECT * FROM News""")
            for old in front_cursor.fetchall():
                print(old)
                parsed_body = self.bbcode_parser.feed(old['thenews'])
                news_item = NewsItem.objects.create(
                    subject=old['subject'],
                    body=parsed_body,
                )
                try:
                    author = User.objects.get(id_orig=old['adminid'])
                    news_item.author_id = author.id
                except User.DoesNotExist:
                    pass
                news_item.created_at = old['stamp']
                news_item.save()
