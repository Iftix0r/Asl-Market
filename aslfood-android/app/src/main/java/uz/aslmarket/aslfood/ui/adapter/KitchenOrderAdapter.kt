package uz.aslmarket.aslfood.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import uz.aslmarket.aslfood.data.model.FoodOrder
import uz.aslmarket.aslfood.databinding.ItemKitchenOrderBinding

class KitchenOrderAdapter(
    private var orders: List<FoodOrder>,
    private val onUpdateStatus: (Long, String) -> Unit
) : RecyclerView.Adapter<KitchenOrderAdapter.KitchenViewHolder>() {

    class KitchenViewHolder(val binding: ItemKitchenOrderBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): KitchenViewHolder {
        val binding = ItemKitchenOrderBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return KitchenViewHolder(binding)
    }

    override fun onBindViewHolder(holder: KitchenViewHolder, position: Int) {
        val order = orders[position]
        holder.binding.tvKitchenCode.text = "#${order.orderCode}"
        holder.binding.tvKitchenStatus.text = order.statusDisplay ?: order.status
        holder.binding.tvKitchenCustomer.text = "${order.customerName} (${order.phone})\nJami: ${order.totalAmount.toLong()} so'm"

        val (btnText, nextStatus) = when (order.status) {
            "new" -> "🍳 Tayyorlashga Olish" to "preparing"
            "preparing" -> "🛵 Kuryerga / Berish" to "delivering"
            "delivering" -> "✅ Topshirish (Yakunlash)" to "completed"
            else -> "✅ Yakunlangan" to ""
        }

        holder.binding.btnNextStatus.text = btnText
        holder.binding.btnNextStatus.isEnabled = nextStatus.isNotEmpty()
        holder.binding.btnNextStatus.setOnClickListener {
            if (nextStatus.isNotEmpty()) {
                onUpdateStatus(order.id, nextStatus)
            }
        }
    }

    override fun getItemCount(): Int = orders.size

    fun updateData(newOrders: List<FoodOrder>) {
        orders = newOrders
        notifyDataSetChanged()
    }
}
