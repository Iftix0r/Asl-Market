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

    // Menu State
    private val _menuItems = MutableLiveData<List<FoodItem>>()
    val menuItems: LiveData<List<FoodItem>> = _menuItems

    private val _categories = MutableLiveData<List<FoodCategory>>()
    val categories: LiveData<List<FoodCategory>> = _categories

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    // Cart State
    private val _cartItems = MutableLiveData<MutableList<CartItem>>(mutableListOf())
    val cartItems: LiveData<MutableList<CartItem>> = _cartItems

    private val _cartTotal = MutableLiveData<Double>(0.0)
    val cartTotal: LiveData<Double> = _cartTotal

    private val _cartCount = MutableLiveData<Int>(0)
    val cartCount: LiveData<Int> = _cartCount

    // Tracked Order State
    private val _trackedOrder = MutableLiveData<FoodOrder?>()
    val trackedOrder: LiveData<FoodOrder?> = _trackedOrder

    // Kitchen Orders State
    private val _kitchenOrders = MutableLiveData<List<FoodOrder>>()
    val kitchenOrders: LiveData<List<FoodOrder>> = _kitchenOrders

    // Placed Order Result State
    private val _placedOrderResult = MutableLiveData<PlaceOrderResponse?>()
    val placedOrderResult: LiveData<PlaceOrderResponse?> = _placedOrderResult

    init {
        fetchCategories()
        fetchMenu()
    }

    fun fetchCategories() {
        viewModelScope.launch {
            repository.getCategories()
                .onSuccess { _categories.value = it }
                .onFailure { _errorMessage.value = it.message }
        }
    }

    fun fetchMenu(categorySlug: String? = null, query: String? = null) {
        viewModelScope.launch {
            _isLoading.value = true
            repository.getMenu(categorySlug, query)
                .onSuccess {
                    _menuItems.value = it
                    _isLoading.value = false
                }
                .onFailure {
                    _errorMessage.value = it.message
                    _isLoading.value = false
                }
        }
    }

    // Cart Functions
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

    // Place Order Function
    fun placeOrder(customerName: String, phone: String, address: String, orderType: String, paymentMethod: String) {
        val items = _cartItems.value ?: return
        if (items.isEmpty()) return

        val payloadItems = items.map { OrderItemPayload(it.foodItem.id, it.quantity) }
        val request = PlaceOrderRequest(customerName, phone, address, orderType, paymentMethod, payloadItems)

        viewModelScope.launch {
            _isLoading.value = true
            repository.placeOrder(request)
                .onSuccess {
                    _placedOrderResult.value = it
                    clearCart()
                    _isLoading.value = false
                }
                .onFailure {
                    _errorMessage.value = it.message
                    _isLoading.value = false
                }
        }
    }

    fun resetPlacedOrderResult() {
        _placedOrderResult.value = null
    }

    // Track Order
    fun trackOrder(code: String) {
        viewModelScope.launch {
            _isLoading.value = true
            repository.trackOrder(code)
                .onSuccess {
                    _trackedOrder.value = it
                    _isLoading.value = false
                }
                .onFailure {
                    _errorMessage.value = it.message
                    _trackedOrder.value = null
                    _isLoading.value = false
                }
        }
    }

    // Kitchen Orders
    fun fetchKitchenOrders(status: String? = null) {
        viewModelScope.launch {
            repository.getOrders(status)
                .onSuccess { _kitchenOrders.value = it }
                .onFailure { _errorMessage.value = it.message }
        }
    }

    fun updateOrderStatus(orderId: Long, newStatus: String) {
        viewModelScope.launch {
            repository.updateOrderStatus(orderId, newStatus)
                .onSuccess { fetchKitchenOrders() }
                .onFailure { _errorMessage.value = it.message }
        }
    }
}
