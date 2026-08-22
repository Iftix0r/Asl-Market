package uz.aslmarket.aslfood.data.model

enum class AppRole {
    CUSTOMER,   // Mijoz planshet — Menyu, Savat, Kuzatish
    KITCHEN;    // Oshxona planshet — Buyurtmalar terminali

    companion object {
        fun fromString(value: String?): AppRole? = when (value) {
            CUSTOMER.name -> CUSTOMER
            KITCHEN.name  -> KITCHEN
            else          -> null
        }
    }
}
