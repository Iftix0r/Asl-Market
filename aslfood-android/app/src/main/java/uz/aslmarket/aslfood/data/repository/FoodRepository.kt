package uz.aslmarket.aslfood.data.repository

import uz.aslmarket.aslfood.data.model.*
import uz.aslmarket.aslfood.data.network.RetrofitClient

class FoodRepository {

    private val api = RetrofitClient.apiService

    suspend fun getMenu(categorySlug: String? = null, query: String? = null): Result<List<FoodItem>> {
        return try {
            val response = api.getMenu(categorySlug, query)
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()?.menu ?: emptyList())
            } else {
                Result.failure(Exception(response.body()?.error ?: "Server xatosi: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getCategories(): Result<List<FoodCategory>> {
        return try {
            val response = api.getCategories()
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()?.categories ?: emptyList())
            } else {
                Result.failure(Exception(response.body()?.error ?: "Kategoriyalar yuklanmadi"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun placeOrder(request: PlaceOrderRequest): Result<PlaceOrderResponse> {
        return try {
            val response = api.placeOrder(request)
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.body()?.error ?: "Buyurtma berishda xatolik"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun trackOrder(code: String): Result<FoodOrder> {
        return try {
            val response = api.trackOrder(code)
            if (response.isSuccessful && response.body()?.success == true && response.body()?.order != null) {
                Result.success(response.body()!!.order!!)
            } else {
                Result.failure(Exception(response.body()?.error ?: "Buyurtma topilmadi"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getOrders(status: String? = null): Result<List<FoodOrder>> {
        return try {
            val response = api.getOrders(status)
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()?.orders ?: emptyList())
            } else {
                Result.failure(Exception(response.body()?.error ?: "Buyurtmalar yuklanmadi"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateOrderStatus(orderId: Long, newStatus: String): Result<Boolean> {
        return try {
            val payload = mapOf<String, Any>("order_id" to orderId, "new_status" to newStatus)
            val response = api.updateOrderStatus(payload)
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(true)
            } else {
                Result.failure(Exception(response.body()?.error ?: "Status o'zgarmadi"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
