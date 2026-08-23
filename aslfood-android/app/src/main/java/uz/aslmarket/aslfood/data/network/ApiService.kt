package uz.aslmarket.aslfood.data.network

import uz.aslmarket.aslfood.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    @GET("api/food/menu/")
    suspend fun getMenu(
        @Query("category") categorySlug: String? = null,
        @Query("q") query: String? = null
    ): Response<MenuResponse>

    @GET("api/food/categories/")
    suspend fun getCategories(): Response<CategoriesResponse>

    @POST("api/food/orders/place/")
    suspend fun placeOrder(
        @Body request: PlaceOrderRequest
    ): Response<PlaceOrderResponse>

    @GET("api/food/orders/track/{code}/")
    suspend fun trackOrder(
        @Path("code") code: String
    ): Response<OrderDetailResponse>

    @GET("api/food/orders/")
    suspend fun getOrders(
        @Query("status") status: String? = null
    ): Response<OrdersListResponse>

    @POST("api/food/orders/status/")
    suspend fun updateOrderStatus(
        @Body request: UpdateStatusRequest
    ): Response<UpdateStatusResponse>
}
