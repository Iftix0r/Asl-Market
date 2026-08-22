package uz.aslmarket.aslfood.ui.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import uz.aslmarket.aslfood.data.model.*
import uz.aslmarket.aslfood.data.repository.FoodRepository
import kotlinx.coroutines.launch

class MainViewModel : ViewModel() {

    private val repository = FoodRepository()

    // ─── Menu State ───────────────────────────────────────────────────────────

    private val _menuItems = MutableLiveData<List<FoodItem>>()
    val menuItems: LiveData<List<FoodItem>> = _menuItems

    private val _categories = MutableLiveData<List<FoodCategory>>()
    val categories: LiveData<List<FoodCategory>> = _categories

    /** Faqat menyu/kategoriya yuklanishida ishlatiladi */
    private val _isMenuLoading = MutableLiveData<Boolean>(false)
    val isMenuLoading: LiveData<Boolean> = _isMenuLoading

    // ─── Error (umumiy) ───────────────────────────────────────────────────────

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    // ─── Cart State ───────────────────────────────────────────────────────────

    private val _cartItems = MutableLiveData<MutableList<CartItem>>(mutableListOf())
    val cartItems: LiveData<MutableList<CartItem>> = _cartItems

    private val _cartTotal = MutableLiveData<Double>(0.0)
    val cartTotal: LiveData<Double> = _cartTotal

    private val _cartCount = MutableLiveData<Int>(0)
    val cartCount: LiveData<Int> = _cartCount

    /** Buyurtma berilganda spinner */
    private val _isOrderLoading = MutableLiveData<Boolean>(false)
    val isOrderLoading: LiveData<Boolean> = _isOrderLoading

    // ─── Order Result ─────────────────────────────────────────────────────────

    private val _placedOrderResult = MutableLiveData<PlaceOrderResponse?>()
    val placedOrderResult: LiveData<PlaceOrderResponse?> = _placedOrderResult

    // ─── Tracker State ────────────────────────────────────────────────────────

    private val _trackedOrder = MutableLiveData<FoodOrder?>()
    val trackedOrder: LiveData<FoodOrder?> = _trackedOrder

    /** Faqat tracker qidiruvida ishlatiladi */
    private val _isTrackLoading = MutableLiveData<Boolean>(false)
    val isTrackLoading: LiveData<Boolean> = _isTrackLoading

    // ─── Kitchen State ────────────────────────────────────────────────────────

    private val _kitchenOrders = MutableLiveData<List<FoodOrder>>()
    val kitchenOrders: LiveData<List<FoodOrder>> = _kitchenOrders

    /** Faqat kitchen yuklanishida ishlatiladi */
    private val _isKitchenLoading = MutableLiveData<Boolean>(false)
    val isKitchenLoading: LiveData<Boolean> = _isKitchenLoading

    // ─── Init ─────────────────────────────────────────────────────────────────

    // ─── Menu Functions ───────────────────────────────────────────────────────

    fun fetchCategories() {
        viewModelScope.launch {
            repository.getCategories()
                .onSuccess { _categories.value = it }
                .onFailure { _errorMessage.value = it.message }
        }
    }

    fun fetchMenu(categorySlug: String? = null, query: String? = null) {
        viewModelScope.launch {
            _isMenuLoading.value = true
            repository.getMenu(categorySlug, query)
                .onSuccess {
                    _menuItems.value = it
                    _isMenuLoading.value = false
                }
                .onFailure {
                    _errorMessage.value = it.message
                    _isMenuLoading.value = false
                }
        }
    }

    // ─── Cart Functions ───────────────────────────────────────────────────────

    fun addToCart(foodItem: FoodItem) {
        val currentList = _cartItems.value ?: mutableListOf()
        val existing = currentList.find { it.foodItem.id == foodItem.id }
        if (existing != null) {
            existing.quantity += 1
        } else {
            currentList.add(CartItem(foodItem, 1))
        }
        _cartItems.value = currentList
        recalculateCart()
    }

    fun updateCartQuantity(foodId: Long, delta: Int) {
        val currentList = _cartItems.value ?: return
        val item = currentList.find { it.foodItem.id == foodId } ?: return
        item.quantity += delta
        if (item.quantity <= 0) {
            currentList.remove(item)
        }
        _cartItems.value = currentList
        recalculateCart()
    }

    fun clearCart() {
        _cartItems.value = mutableListOf()
        recalculateCart()
    }

    private fun recalculateCart() {
        val items = _cartItems.value ?: mutableListOf()
        _cartCount.value = items.sumOf { it.quantity }
        _cartTotal.value = items.sumOf { it.subtotal }
    }

    // ─── Order Functions ──────────────────────────────────────────────────────

    fun placeOrder(
        customerName: String,
        phone: String,
        address: String,
        orderType: String,
        paymentMethod: String
    ) {
        val items = _cartItems.value ?: return
        if (items.isEmpty()) return

        val payloadItems = items.map { OrderItemPayload(it.foodItem.id, it.quantity) }
        val request = PlaceOrderRequest(customerName, phone, address, orderType, paymentMethod, payloadItems)

        viewModelScope.launch {
            _isOrderLoading.value = true
            repository.placeOrder(request)
                .onSuccess {
                    _placedOrderResult.value = it
                    clearCart()
                    _isOrderLoading.value = false
                }
                .onFailure {
                    _errorMessage.value = it.message
                    _isOrderLoading.value = false
                }
        }
    }

    fun resetPlacedOrderResult() {
        _placedOrderResult.value = null
    }

    // ─── Tracker Functions ────────────────────────────────────────────────────

    fun trackOrder(code: String) {
        viewModelScope.launch {
            _isTrackLoading.value = true
            repository.trackOrder(code)
                .onSuccess {
                    _trackedOrder.value = it
                    _isTrackLoading.value = false
                }
                .onFailure {
                    _errorMessage.value = it.message
                    _trackedOrder.value = null
                    _isTrackLoading.value = false
                }
        }
    }

    fun clearTrackedOrder() {
        _trackedOrder.value = null
    }

    // ─── Kitchen Functions ────────────────────────────────────────────────────

    fun fetchKitchenOrders(status: String? = null) {
        viewModelScope.launch {
            _isKitchenLoading.value = true
            repository.getOrders(status)
                .onSuccess {
                    _kitchenOrders.value = it
                    _isKitchenLoading.value = false
                }
                .onFailure {
                    _errorMessage.value = it.message
                    _isKitchenLoading.value = false
                }
        }
    }

    fun updateOrderStatus(orderId: Long, newStatus: String) {
        viewModelScope.launch {
            repository.updateOrderStatus(orderId, newStatus)
                .onSuccess { fetchKitchenOrders() }
                .onFailure { _errorMessage.value = it.message }
        }
    }

    fun clearError() {
        _errorMessage.value = null
    }
}
