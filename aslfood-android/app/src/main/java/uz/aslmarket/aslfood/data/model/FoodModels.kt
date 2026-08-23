package uz.aslmarket.aslfood.data.model

import com.google.gson.annotations.SerializedName

// Food Menu Item Model
data class FoodItem(
    val id: Long,
    val name: String,
    val category: String?,
    @SerializedName("category_slug") val categorySlug: String?,
    val price: Double,
    @SerializedName("prep_time") val prepTime: Int = 15,
    @SerializedName("image_url") val imageUrl: String?,
    val ingredients: String?,
    @SerializedName("is_available") var isAvailable: Boolean = true
)

// Category Model
data class FoodCategory(
    val id: Long,
    val name: String,
    val slug: String
)

// Cart Item Model for local state
data class CartItem(
    val foodItem: FoodItem,
    var quantity: Int = 1
) {
    val subtotal: Double
        get() = foodItem.price * quantity
}

// Order Creation Payload Request
data class PlaceOrderRequest(
    @SerializedName("customer_name") val customerName: String,
    val phone: String,
    @SerializedName("delivery_address") val deliveryAddress: String?,
    @SerializedName("order_type") val orderType: String = "delivery",
    @SerializedName("payment_method") val paymentMethod: String = "naqd",
    val items: List<OrderItemPayload>
)

data class OrderItemPayload(
    val id: Long,
    val qty: Int
)

// API Response Models
data class MenuResponse(
    val success: Boolean,
    val count: Int,
    val menu: List<FoodItem>,
    val error: String?
)

data class CategoriesResponse(
    val success: Boolean,
    val categories: List<FoodCategory>,
    val error: String?
)

data class PlaceOrderResponse(
    val success: Boolean,
    @SerializedName("order_code") val orderCode: String?,
    @SerializedName("total_amount") val totalAmount: Double?,
    val message: String?,
    val error: String?
)

data class OrderDetailResponse(
    val success: Boolean,
    val order: FoodOrder?,
    val error: String?
)

data class OrdersListResponse(
    val success: Boolean,
    val orders: List<FoodOrder>,
    val error: String?
)

data class UpdateStatusRequest(
    @SerializedName("order_id") val orderId: Long,
    @SerializedName("new_status") val newStatus: String
)

data class UpdateStatusResponse(
    val success: Boolean,
    @SerializedName("new_status") val newStatus: String?,
    val error: String?
)

// Food Order Model
data class FoodOrder(
    val id: Long,
    @SerializedName("order_code") val orderCode: String,
    @SerializedName("customer_name") val customerName: String,
    val phone: String,
    @SerializedName("delivery_address") val deliveryAddress: String?,
    @SerializedName("total_amount") val totalAmount: Double,
    val status: String,
    @SerializedName("status_display") val statusDisplay: String?,
    @SerializedName("created_at") val createdAt: String,
    val items: List<FoodOrderItemDetail>? = null
)

data class FoodOrderItemDetail(
    val name: String,
    val qty: Int,
    val price: Double,
    val total: Double
)
