import pytest

from django.test import TestCase

from fleet.models import Vehicle, VehicleMarketing
from users.models import Customer
from sales.models import TaxRate, Coupon
from sales.utils import RentalPriceCalculator


# vehicle_1 = VehicleMarketing.objects.create(
#     price_per_day=500,
#     discount_2_day=10,
#     discount_3_day=20,
#     discount_7_day=40,
#     security_deposit=5000.00,
# )


@pytest.fixture
def vehicle_mock_1(mocker):
    vehicle_1 = mocker.MagicMock(spec=VehicleMarketing)
    vehicle_1.price_per_day = 950
    vehicle_1.discount_2_day = 10
    vehicle_1.discount_3_day = 20
    vehicle_1.discount_7_day = 40
    # vehicle_1.return_value = mocker.MagicMock()
    return vehicle_1


@pytest.fixture
def tax_rate_1(mocker):
    tax_rate_1 = mocker.MagicMock(spec=TaxRate)
    tax_rate_1.total_rate = 0.06625
    tax_rate_1.return_value = mocker.MagicMock(), True
    return tax_rate_1


@pytest.fixture
def coupon_mock_1(mocker):
    # mocker.patch('sales.models.Coupon.get_discount_value', 15.00)
    coupon_1 = mocker.MagicMock(spec=Coupon)
    coupon_1.amount = 15.00
    # coupon_1.get_discount_value = mocker.MagicMock()
    coupon_1.get_discount_value.return_value = 15.00
    return coupon_1


@pytest.fixture
def customer_1(mocker):
    customer_1 = mocker.MagicMock(spec=Customer)
    customer_1.discount_pct = 10
    return customer_1


@pytest.fixture(autouse=True)
def _mock_db_connection(mocker, tax_rate_1, coupon_mock_1, customer_1):
    mocker.patch('sales.models.TaxRate.objects.get_or_create', tax_rate_1)
    mocker.patch('sales.models.Coupon.objects.get', coupon_mock_1)
    mocker.patch('users.models.Customer.objects.get', customer_1)


@pytest.fixture
def num_days():
    return 2


@pytest.fixture
def email():
    return 'btman@mac.com'


@pytest.fixture
def extra_miles():
    return 200


@pytest.fixture
def tax_zip():
    return '07430'


# class RentalPriceCalculatorTestCase(TestCase):
# @pytest.mark.django_db
class TestRentalPriceCalculatorTestCase:

    databases = ('default', 'front',)

    def setUp(self) -> None:
        self.vehicle_1 = VehicleMarketing.objects.create(
            price_per_day=500,
            discount_2_day=10,
            discount_3_day=20,
            discount_7_day=40,
            security_deposit=5000.00,
        )
        self.tax_rate_1 = TaxRate.objects.create(
            postal_code='07430',
            total_rate=0.06625,
        )
        self.customer_1 = Customer.objects.create(
            discount_pct=10,
        )
        self.coupon_1 = Coupon.objects.create(
            amount=15.00,
        )

    # @pytest.mark.parametrize(
    #     'vehicle, num_days, coupon_code, email, extra_miles, tax_zip',
    #     [
    #         (
    #             vehicle_mock_1,
    #             2,
    #             None,
    #             None,
    #             200,
    #             '07430',
    #         ),
    #     ],
    # )
    def test_get_rental_price_data(self, vehicle_mock_1, num_days, coupon_mock_1, email, extra_miles, tax_zip):
        num_days = 2
        rental_price_calculator = RentalPriceCalculator(
            vehicle_mock_1,
            num_days,
            coupon_mock_1,
            email,
            extra_miles,
            tax_zip,
        )
        price_data = rental_price_calculator.get_price_data()
        print(price_data)
        assert None == None

