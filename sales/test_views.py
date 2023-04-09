import pytest
from django.test.client import Client
from django.urls import reverse

from fleet.models import Vehicle, VehicleMarketing


@pytest.fixture
def vehicle_mock_1(mocker):
    vehicle_1 = mocker.MagicMock(
        spec=VehicleMarketing,
        id=1,
        slug='test-vehicle',
        price_per_day=950,
        discount_2_day=10,
        discount_3_day=20,
        discount_7_day=40,
    )
    return vehicle_1


@pytest.mark.django_db(databases=['default', 'front'])
@pytest.mark.parametrize(
    'post_data, expected', [
        pytest.param(
            dict(
                vehicle_marketing=1,
                vehicle_slug='test_vehicle',
                out_date='',
                out_time='07:00',
                back_date='',
                back_time='07:00',
                drivers='1',
                delivery_required='0',
                delivery_zip='',
                extra_miles='0',
                email='',
                coupon_code='',
                is_military=False,
                customer_notes='',
            ),
            {},
            id='defaults',
        ),
    ]
)
def test_rental_details(mocker, post_data, expected):
    mocker.patch('pri.middleware.RemoteHostMiddleware.visited_within_hour', mocker.MagicMock(return_value=True))
    mocker.patch('fleet.models.VehicleMarketing.objects.filter', vehicle_mock_1)
    client = Client()
    url = reverse('validate-rental-details')
    response = client.post(url, post_data)
    print(response)
