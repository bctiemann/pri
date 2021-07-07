import MySQLdb
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from backoffice.models import Vehicle
from fleet.models import VehicleMarketing
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
        legacy_backoffice_db = settings.DATABASES['backoffice_legacy']
        db = MySQLdb.connect(
            passwd=legacy_db['PASSWORD'],
            db=legacy_db['NAME'],
            host=legacy_db['HOST'],
            user=legacy_db['USER'],
            charset=legacy_db['OPTIONS']['charset'],
        )
        front_cursor = db.cursor(MySQLdb.cursors.DictCursor)
        backoffice_db = MySQLdb.connect(
            passwd=legacy_backoffice_db['PASSWORD'],
            db=legacy_backoffice_db['NAME'],
            host=legacy_backoffice_db['HOST'],
            user=legacy_backoffice_db['USER'],
            charset=legacy_backoffice_db['OPTIONS']['charset'],
        )
        back_cursor = backoffice_db.cursor(MySQLdb.cursors.DictCursor)

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
                old = front_cursor.fetchone()
                print(old)
                new_front = VehicleMarketing.objects.create(
                    vehicle_id=new.id,
                )
