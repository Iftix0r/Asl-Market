from django.test import TestCase, Client
from django.urls import reverse
import json
from store.models import FoodCategory, FoodItem, FoodOrder, FoodOrderItem

class AslFoodTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = FoodCategory.objects.create(
            name="Lavash",
            slug="lavash"
        )
        self.food_item = FoodItem.objects.create(
            category=self.category,
            name="Mol go'shtli lavash",
            price=32000,
            preparation_time_mins=15,
            is_available=True
        )

    def test_storefront_view(self):
        response = self.client.get(reverse('storefront'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AslFood")
        self.assertContains(response, "Mol go")

    def test_place_order_api(self):
        payload = {
            "customer_name": "Ali Valiyev",
            "phone": "+998901234567",
            "delivery_address": "Toshkent sh., Yunusobod 4",
            "order_type": "delivery",
            "payment_method": "naqd",
            "items": [
                {"id": self.food_item.id, "qty": 2}
            ]
        }
        response = self.client.post(
            reverse('aslfood_order_api'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total_amount"], 64000)

        # DB verification
        order = FoodOrder.objects.get(order_code=data["order_code"])
        self.assertEqual(order.customer_name, "Ali Valiyev")
        self.assertEqual(order.total_amount, 64000)
        self.assertEqual(order.items.count(), 1)

    def test_update_status_api(self):
        order = FoodOrder.objects.create(
            order_code="1001",
            customer_name="Test User",
            phone="+998900000000",
            total_amount=32000,
            status="new"
        )
        payload = {
            "order_id": order.id,
            "new_status": "preparing"
        }
        response = self.client.post(
            reverse('aslfood_update_status_api'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        order.refresh_from_db()
        self.assertEqual(order.status, "preparing")
