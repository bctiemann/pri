import MySQLdb
import logging
import json

import pytz
import requests
import re
from html2bbcode import parser

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File

from backoffice.models import BBSPost
from marketing.models import NewsItem, SiteContent, NewsletterSubscription, SurveyResponse
from fleet.models import (
    Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo, TransmissionType, Location, TollTag,
    get_vehicle_picture_path, get_vehicle_video_path
)
from users.models import Customer, Employee, User, MusicGenre
from sales.models import (
    Promotion, Coupon, BaseReservation, Reservation, Rental, Driver, JoyRide, PerformanceExperience, GiftCertificate,
    AdHocPayment, Charge, RedFlag, generate_code
)
from consignment.models import Consigner, ConsignmentPayment
from service.models import Damage
from sales.enums import ReservationType
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

GUIDED_DRIVE_TYPE_MAP = {
    1: ReservationType.JOY_RIDE.value,
    2: ReservationType.PERFORMANCE_EXPERIENCE.value,
}

GUIDED_DRIVE_MODEL_MAP = {
    1: JoyRide,
    2: PerformanceExperience,
}

SITE_ROOT = 'http://172.16.0.5/prinew/root/'
SITE_SEC_ROOT = 'http://172.16.0.5/prinew/secure/'


class Command(BaseCommand):

    enabled = {
        # 'do_tolltags': True,
        # 'do_vehicles': True,
        # 'do_vehicle_pics': True,
        # 'do_vehicle_vids': True,
        # 'do_customers': True,
        # 'do_reservations': True,
        # 'do_rentals': True,
        # 'do_drivers': True,
        # 'do_consigners': True,
        # 'do_consignmentvehicles': True,
        # 'do_consignmentpayments': True,
        # 'do_admins': True,
        # 'do_newsitems': True,
        # 'do_bbsposts': True,
        # 'do_sitecontent': True,
        # 'do_newslettersubscriptions': True,
        # 'do_coupons': True,
        # 'do_guideddrives': True,
        # 'do_giftcertificates': True,
        # 'do_adhocpayments': True,
        # 'do_charges': True,
        # 'do_redflags': True,
        # 'do_surveyresponses': True,
        'do_damage': True,
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

    def import_vehicle_video(self, vehicle_video, vehicle_vid_id, ext, thumb_ext):
        url = f'{SITE_ROOT}vids/PRI-{vehicle_vid_id}.{ext}'
        video_tempfile = self.get_image_tempfile(url)
        vehicle_video.video.save(get_vehicle_video_path(None, f'temp.{ext}'), File(video_tempfile))
        thumb_url = f'{SITE_ROOT}vids/PRI-{vehicle_vid_id}.thumb.{thumb_ext}'
        thumb_tempfile = self.get_image_tempfile(thumb_url)
        vehicle_video.thumbnail.save(get_vehicle_video_path(None, f'temp.{thumb_ext}'), File(thumb_tempfile))
        vehicle_video.save()

    def import_inspection_image(self, vehicle_marketing, vehicle_id):
        url = f'{SITE_SEC_ROOT}spork/carcheck/{vehicle_id}.png'
        image_tempfile = self.get_image_tempfile(url)
        vehicle_marketing.inspection_image.save(get_vehicle_picture_path(None, 'temp.png'), File(image_tempfile))
        vehicle_marketing.save()

    def import_mobile_thumb_image(self, vehicle_marketing, vehicle_id):
        url = f'{SITE_ROOT}images/{vehicle_id}-thumb-mobile.png'
        image_tempfile = self.get_image_tempfile(url)
        vehicle_marketing.mobile_thumbnail_image.save(get_vehicle_picture_path(None, 'temp.png'), File(image_tempfile))
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
            front_cursor.execute("""SELECT * FROM VehiclesFront""")
            for old_front in front_cursor.fetchall():
                back_cursor.execute("""SELECT * FROM Vehicles where vehicleid=%s""", old_front['vehicleid'])
                old = back_cursor.fetchone()
                print(old)
                if not old:
                    continue

                print(old['make'], old['model'])
                parsed_blurb = self.bbcode_parser.feed(old_front['blurb'])
                slug = slugify(f'{old["make"]}-{old["model"]}')
                new_front = VehicleMarketing.objects.create(
                    id=old_front['vehicleid'],
                    slug=slug,
                    make=old['make'],
                    model=old['model'],
                    year=old['year'],
                    vehicle_type=old_front['type'],
                    status=old_front['status'],
                    weighting=old['weighting'],
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
                self.import_showcase_image(new_front, old_front['vehicleid'])
                self.import_thumbnail_image(new_front, old_front['vehicleid'])
                self.import_inspection_image(new_front, old_front['vehicleid'])
                self.import_mobile_thumb_image(new_front, old_front['vehicleid'])

                new = Vehicle.objects.create(
                    id=old['vehicleid'],
                    vehicle_marketing_id=new_front.id,
                    make=old['make'],
                    model=old['model'],
                    year=old['year'],
                    slug=slug,
                    vehicle_type=old['type'],
                    status=old_front['status'],
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

                # new.status = old_front['status']
                # new.save()

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
                    vehicle_marketing = VehicleMarketing.objects.get(id=vehicle.vehicle_marketing_id)
                except VehicleMarketing.DoesNotExist:
                    continue
                print(vehicle_marketing)
                new = VehiclePicture.objects.create(
                    vehicle_marketing=vehicle_marketing,
                    is_first=old['isfirst'],
                )
                self.import_vehicle_picture_image(new, old['vpicsid'], old['fext'])

        if 'do_vehicle_vids' in self.enabled:
            if clear_existing:
                VehicleVideo.objects.all().delete()
            front_cursor.execute("""SELECT * FROM VVids""")
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
                new = VehicleVideo.objects.create(
                    vehicle_marketing=vehicle_marketing,
                    is_first=old['isfirst'],
                )
                self.import_vehicle_video(new, old['vvidsid'], old['fext'], old['thumbext'])

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
                        rating=old['rating'],
                        driver_skill=old['driverskill'],
                        discount_pct=int(old['discount']) if old['discount'].isdigit() else None,
                        music_genre=music_genre,
                        first_time=bool(old['firsttime']),
                        drivers_club=bool(old['DriversClub']),
                        receive_email=not bool(old['nomail']),
                        ban=bool(old['ban']),
                        survey_done=bool(old['surveydone']),
                        registration_ip=old['regip'],
                        registration_lat=old['reglat'],
                        registration_long=old['reglong'],
                        music_favorite=old['musicfav'] or '',
                    )
                    new.created_at = old['createdon']
                    new.save()
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
                    type=Reservation.ReservationType.RESERVATION,
                    customer=customer,
                    vehicle=vehicle,
                    out_at=old['dateout'],
                    back_at=old['dateback'],
                    override_subtotal=old['rate'],
                    drivers=old['drivers'],
                    miles_included=old['milesinc'],
                    extra_miles=old['xtramiles'],
                    customer_notes=old['notes'],
                    coupon_code=old['coupon'],
                    status=old['status'],
                    deposit_amount=old['depamount'],
                    confirmation_code=old['confcode'],
                    delivery_required=bool(old['delivery']),
                    app_channel=Reservation.AppChannel.MOBILE if old['iphone'] else Reservation.AppChannel.WEB,
                    # tax_percent=old['taxpct'],
                    delivery_zip=old['deliveryzip'],
                )
                new.reserved_at = old['reservdate']
                new.save()

        if 'do_rentals' in self.enabled:
            if clear_existing:
                Rental.objects.all().delete()
            back_cursor.execute("""SELECT * FROM Rentals""")
            for old in back_cursor.fetchall():
                print(old)
                customer = Customer.objects.filter(id=old['customerid']).first()
                vehicle = Vehicle.objects.filter(id=old['vehicleid']).first()
                new = Rental.objects.create(
                    id=old['rentalid'],
                    type=Rental.ReservationType.RENTAL,
                    customer=customer,
                    vehicle=vehicle,
                    out_at=old['dateout'],
                    back_at=old['dateback'],
                    override_subtotal=old['rate'],
                    drivers=old['drivers'],
                    miles_included=old['milesinc'],
                    extra_miles=old['xtramiles'],
                    customer_notes=old['notes'],
                    coupon_code=old['coupon'],
                    status=old['status'],
                    deposit_amount=old['depamount'],
                    confirmation_code=old['confcode'] or generate_code(ReservationType.RENTAL.value),
                    delivery_required=bool(old['delivery']),
                    app_channel=Reservation.AppChannel.MOBILE if old['iphone'] else Reservation.AppChannel.WEB,
                    # tax_percent=old['taxpct'],
                    delivery_zip=old['deliveryzip'] or '',

                    mileage_out=old['milesout'],
                    mileage_back=old['milesback'],
                    abuse=old['abuse'],
                    damage_out=old['damageout'],
                    damage_in=old['damagein'],
                    internal_notes=self.decrypt(old['ournotes']),
                    deposit_charged_at=old['depchargedon'],
                    deposit_refunded_at=old['deprefundon'],
                    deposit_refund_amount=old['deprefundamount'],
                    rental_discount_pct=old['discount'],
                    extended_days=old['extenddays'],
                )
                new.reserved_at = old['reservdate']
                new.save()

        if 'do_drivers' in self.enabled:
            if clear_existing:
                Driver.objects.all().delete()
            back_cursor.execute("""SELECT * FROM Drivers""")
            for old in back_cursor.fetchall():
                print(old)
                try:
                    rental = Rental.objects.get(pk=old['rentalid'])
                except Rental.DoesNotExist:
                    continue
                try:
                    customer = Customer.objects.get(pk=old['customerid'])
                except Customer.DoesNotExist:
                    continue
                new = Driver.objects.create(
                    rental=rental,
                    customer=customer,
                    is_primary=bool(old['primarydrv']),
                )

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

        if 'do_consignmentpayments' in self.enabled:
            if clear_existing:
                ConsignmentPayment.objects.all().delete()
            back_cursor.execute("""SELECT * FROM ConsignmentPayments""")
            for old in back_cursor.fetchall():
                print(old)
                try:
                    consigner = Consigner.objects.get(pk=old['consignerid'])
                except Consigner.DoesNotExist:
                    continue
                new = ConsignmentPayment.objects.create(
                    consigner=consigner,
                    paid_at=old['stamp'],
                    amount=old['amount'],
                    method=old['method'],
                )

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
                parsed_body = re.sub('[\r\n]{3,}', '\r\n\r\n', parsed_body)
                parsed_body = re.sub('\[/?p\](\r\n)?', '', parsed_body)

                news_item = NewsItem.objects.create(
                    slug=slugify(old['subject']),
                    subject=old['subject'],
                    body=parsed_body,
                )
                try:
                    author = User.objects.get(id_orig=old['adminid'])
                    news_item.author_id = author.id
                except User.DoesNotExist:
                    pass
                news_item.created_at = old['stamp'].replace(tzinfo=pytz.utc)
                news_item.save()

        if 'do_bbsposts' in self.enabled:
            # if clear_existing:
            #     BBSPost.objects.all().delete()
            back_cursor.execute("""SELECT * FROM notes""")
            for old in back_cursor.fetchall():
                print(old)

        if 'do_sitecontent' in self.enabled:
            if clear_existing:
                SiteContent.objects.all().delete()
                db_key, page_key, page_name = page
            for page in (
                    ('about', 'about', 'About the Company',),
                    ('policies', 'policies', 'Policies',),
                    ('contact', 'contact', 'Contact',),
                    ('servicescont', 'services', 'Our Services',),
                    ('reservations', 'specials', 'Specials',),
            ):
                back_cursor.execute(f"""SELECT {db_key} FROM vars""")
                old_content = back_cursor.fetchone()
                print(old_content)
                new = SiteContent.objects.create(
                    page=page_key,
                    name=page_name,
                    content=old_content[db_key],
                )

        if 'do_newslettersubscriptions' in self.enabled:
            if clear_existing:
                NewsletterSubscription.objects.all().delete()
            front_cursor.execute("""SELECT * FROM Newsletter""")
            for old in front_cursor.fetchall():
                print(old)
                new = NewsletterSubscription.objects.create(
                    email=old['email'],
                    full_name=old['name'],
                    confirmed_at=timezone.now() if old['confirmed'] else None,
                    hash=old['tkt'] or None,
                    ip=old['ip'],
                )
                new.created_at = old['stamp'] or timezone.now()
                new.save()

        if 'do_coupons' in self.enabled:
            if clear_existing:
                Coupon.objects.all().delete()
            back_cursor.execute("""SELECT * FROM discounts""")
            for old in back_cursor.fetchall():
                print(old)
                new = Coupon.objects.create(
                    code=old['code'],
                    name=old['code'],
                    percent=old['amount'],
                )

        if 'do_tolltags' in self.enabled:
            if clear_existing:
                TollTag.objects.all().delete()
            back_cursor.execute("""SELECT * FROM TollTags""")
            for old in back_cursor.fetchall():
                print(old)
                try:
                    vehicle = Vehicle.objects.get(pk=old['vehicleid'])
                except Vehicle.DoesNotExist:
                    vehicle = None
                new = TollTag.objects.create(
                    toll_account=old['tollaccount'],
                    tag_number=old['tagnumber'],
                    vehicle=vehicle,
                    alt_usage=old['altusage'] or '',
                    notes=old['notes'],
                )

        if 'do_guideddrives' in self.enabled:
            if clear_existing:
                JoyRide.objects.all().delete()
                PerformanceExperience.objects.all().delete()
            back_cursor.execute("""SELECT * FROM joyperf""")
            for old in back_cursor.fetchall():
                print(old)
                try:
                    customer = Customer.objects.get(pk=old['customerid'])
                except Customer.DoesNotExist:
                    continue
                try:
                    vehicle_choice_1 = Vehicle.objects.get(pk=old['choice1'])
                except Vehicle.DoesNotExist:
                    vehicle_choice_1 = None
                try:
                    vehicle_choice_2 = Vehicle.objects.get(pk=old['choice2'])
                except Vehicle.DoesNotExist:
                    vehicle_choice_2 = None
                try:
                    vehicle_choice_3 = Vehicle.objects.get(pk=old['choice3'])
                except Vehicle.DoesNotExist:
                    vehicle_choice_3 = None
                model = GUIDED_DRIVE_MODEL_MAP.get(old['type'])
                new = model.objects.create(
                    customer=customer,
                    vehicle_choice_1=vehicle_choice_1,
                    vehicle_choice_2=vehicle_choice_2,
                    vehicle_choice_3=vehicle_choice_3,
                    requested_date=old['reqdate'],
                    backup_date=old['bupdate'],
                    confirmation_code=old['confcode'] or generate_code(GUIDED_DRIVE_TYPE_MAP.get(old['type'])),
                    event_type=old['type'],
                    status=old['status'],
                    customer_notes=old['notes'],
                    internal_notes=self.decrypt(old['ournotes']),
                    num_passengers=old['nopax'],
                    num_minors=old['nominors'],
                    big_and_tall=old['bigtall'],
                    coupon_code=old['coupon'],
                    override_subtotal=old['rate'],
                )
                if model == PerformanceExperience:
                    new.num_drivers = old['nodrv']
                    new.save()

        if 'do_giftcertificates' in self.enabled:
            if clear_existing:
                GiftCertificate.objects.all().delete()
            back_cursor.execute("""SELECT * FROM GiftCerts""")
            for old in back_cursor.fetchall():
                print(old)
                new = GiftCertificate.objects.create(
                    id=old['giftcertid'],
                    tag=old['tag'],
                    issued_at=old['issued'],
                    beneficiary_name=old['usename'],
                    cc_name=old['ccname'],
                    cc_address=self.decrypt(old['ccaddr']),
                    cc_city=old['cccity'],
                    cc_state=old['ccstate'],
                    cc_zip=old['cczip'],
                    cc_number=self.decrypt(old['ccnum']),
                    cc_exp_yr=old['ccexpyr'],
                    cc_exp_mo=old['ccexpmo'],
                    cc_cvv=old['cccvv'],
                    cc_phone=old['cctel'],
                    email=old['email'],
                    phone=old['phone'],
                    is_used=old['used'],
                    used_on=old['usedon'],
                    remarks=old['remarks'] or '',
                    amount=old['amount'],
                    is_paid=old['ispaid'],
                    message=old['message'],
                    value_message=old['valuemessage'] or '',
                )
                if old['created']:
                    new.created_at = old['created']
                    new.save()

        if 'do_adhocpayments' in self.enabled:
            if clear_existing:
                AdHocPayment.objects.all().delete()
            back_cursor.execute("""SELECT * FROM subp""")
            for old in back_cursor.fetchall():
                print(old)
                new = AdHocPayment.objects.create(
                    full_name=old['fullname'],
                    email=old['email'],
                    amount=old['amount'],
                    is_paid=old['ispaid'],
                    paid_at=old['paidon'] or timezone.now() if old['ispaid'] else None,
                    item=old['item'],
                    message=old['mesg'],
                    comments=old['comments'] or '',
                    cc_number=self.decrypt(old['ccnum']),
                    cc_exp_yr=old['ccexpyr'],
                    cc_exp_mo=old['ccexpmo'],
                    cc_cvv=old['cccvv'],
                    cc_address=self.decrypt(old['addr']),
                    cc_city=old['city'],
                    cc_state=old['state'],
                    cc_zip=old['zip'],
                    phone=old['tel'],
                    foreign_region=old['ostate'] or '',
                    country=old['country'],
                    is_submitted=old['issub'],
                    submitted_at=old['paidon'] or timezone.now() if old['issub'] else None,
                )
                if old['stamp']:
                    new.created_at = old['stamp']
                    new.save()

        if 'do_charges' in self.enabled:
            if clear_existing:
                Charge.objects.all().delete()
            back_cursor.execute("""SELECT * FROM Charges""")
            for old in back_cursor.fetchall():
                print(old)
                new = Charge.objects.create(
                    id=old['chargeid'],
                    full_name=old['fullname'],
                    email=old['email'],
                    amount=old['amount'],
                    capture=old['capture'],
                    charged_at=old['chargedon'],
                    notes=old['notes'],
                    cc_number=self.decrypt(old['ccnum']),
                    cc_exp_yr=old['ccexpyr'],
                    cc_exp_mo=old['ccexpmo'],
                    cc_cvv=old['cccvv'],
                    cc_address=self.decrypt(old['addr']),
                    cc_city=old['city'],
                    cc_state=old['state'],
                    cc_zip=old['zip'],
                    phone=old['tel'],
                    foreign_region=old['ostate'] or '',
                    country=old['country'],
                    processor_charge_id=old['processorchargeid'],
                    error_code=old['errorcode'] or '',
                )
                if old['stamp']:
                    new.created_at = old['stamp']
                    new.save()

        if 'do_redflags' in self.enabled:
            if clear_existing:
                RedFlag.objects.all().delete()
            back_cursor.execute("""SELECT * FROM tards""")
            for old in back_cursor.fetchall():
                print(old)
                new = RedFlag.objects.create(
                    full_name=old['name'],
                    phone=old['tel'] or old['cel'],
                    email=old['email'],
                    address=old['address'],
                    city=old['city'],
                    state=old['state'],
                    zip=old['zip'],
                    license_number=old['licenseno'],
                    license_state=old['licensestate'],
                    ssn=old['ssn'],
                    remarks=old['remarks'],
                )
                new.created_at = old['stamp']
                new.save()

        if 'do_surveyresponses' in self.enabled:
            if clear_existing:
                SurveyResponse.objects.all().delete()
            front_cursor.execute("""SELECT * FROM surveys""")
            for old in front_cursor.fetchall():
                print(old)
                customer = Customer.objects.filter(pk=old['customerid']).first()
                new = SurveyResponse.objects.create(
                    id=old['surveyid'],
                    customer=customer,
                    ip=old['ip'],
                    heard_about=old['hearabout'],
                    general_rating=old['prirating'],
                    rental_frequency=old['howmany'],
                    vehicle_rating=old['vehiclerating'],
                    would_recommend=old['recommend'],
                    pricing=old['pricing'],
                    email_frequency=old['email'],
                    vehicle_types=old['types'],
                    new_vehicles=old['newvehicles'],
                    comments=old['comments'],
                )
                new.created_at = old['stamp']
                new.save()

        if 'do_damage' in self.enabled:
            if clear_existing:
                Damage.objects.all().delete()
            back_cursor.execute("""SELECT * FROM Damage""")
            for old in back_cursor.fetchall():
                print(old)
                vehicle = Vehicle.objects.filter(pk=old['vehicleid']).first()
                new = Damage.objects.create(
                    id=old['damageid'],
                    vehicle=vehicle,
                    title=old['title'],
                    damaged_at=old['damageon'],
                    repaired_at=old['repairedon'],
                    is_repaired=old['repaired'],
                    cost=old['cost'],
                    fault=old['fault'],
                    customer_billed_amount=old['billcustomer'],
                    customer_paid_amount=old['paidamt'],
                    is_paid=old['paid'],
                    in_house_repair=old['inhouse'],
                    notes=old['notes'] or '',
                )
