import MySQLdb
import logging
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from fleet.models import Vehicle, VehicleMarketing
from pri.cipher import AESCipher

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    enabled = {
        'do_vehicles': True,
    }

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key',)
        parser.add_argument('--clear_existing', dest='clear_existing', default=False, action='store_true',)

    def handle(self, *args, **options):
        key = options.get('key', None)
        if not key:
            print('Missing --key <key>')
            raise SystemExit

        aes = AESCipher(key)

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
                policy_number = aes.decrypt(old['policyno']) if old['policyno'] else ''
                new = Vehicle.objects.create(
                    make=old['make'],
                    model=old['model'],
                    year=old['year'],
                    vehicle_type=old['type'],
                    status=0,
                    plate=old['plate'],
                    vin=old['vin'],
                    mileage=old['mileage'],
                    damage=old['damage'],
                    notes=old['notes'],
                    policy_number=policy_number,
                    policy_company=old['policyco'],
                    policy_phone=old['policytel'],
                    weighting=old['weighting'],
                )
                front_cursor.execute("""SELECT * FROM VehiclesFront where vehicleid=%s""", old['vehicleid'])
                old_front = front_cursor.fetchone()
                print(old_front)
                new_front = VehicleMarketing.objects.create(
                    vehicle_id=new.id,
                    make=old['make'],
                    model=old['model'],
                    year=old['year'],
                    vehicle_type=old['type'],
                    status=old_front['status'],
                    horsepower=old_front['hp'],
                    torque=old_front['tq'],
                    top_speed=old_front['topspeed'],
                    transmission_type=old_front['trans'],
                    gears=old_front['gears'],
                    location=old_front['location'],
                    tight_fit=old_front['tightfit'],
                    blurb=old_front['blurb'],
                    specs=json.loads(old_front['specs']),
                    origin_country=old_front['origin'],
                    price_per_day=old_front['price'],
                    discount_2_day=old_front['disc2day'],
                    discount_3_day=old_front['disc3day'],
                    discount_7_day=old_front['disc7day'],
                    deposit=old_front['deposit'],
                    miles_included=old_front['milesinc'],
                )
                new.status = old_front['status']
                new.save()
