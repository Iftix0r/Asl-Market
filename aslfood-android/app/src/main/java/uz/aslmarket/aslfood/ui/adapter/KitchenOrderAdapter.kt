package uz.aslmarket.aslfood.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.RecyclerView
import uz.aslmarket.aslfood.R
import uz.aslmarket.aslfood.data.model.FoodOrder
import uz.aslmarket.aslfood.databinding.ItemKitchenOrderBinding

class KitchenOrderAdapter(
    private var orders: List<FoodOrder>,
    private val onUpdateStatus: (Long, String) -> Unit
) : RecyclerView.Adapter<KitchenOrderAdapter.KitchenViewHolder>() {

    class KitchenViewHolder(val binding: ItemKitchenOrderBinding) :
        RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): KitchenViewHolder {
        val binding = ItemKitchenOrderBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return KitchenViewHolder(binding)
    }

    override fun onBindViewHolder(holder: KitchenViewHolder, position: Int) {
        val order = orders[position]
        val ctx = holder.itemView.context

        with(holder.binding) {
            tvKitchenCode.text = "#${order.orderCode}"
            tvKitchenCustomer.text = buildString {
                append(order.customerName)
                append(" · ")
                append(order.phone)
                append("\nJami: %,d so'm".format(order.totalAmount.toLong()))
                order.deliveryAddress?.takeIf { it.isNotBlank() }?.let {
                    append("\n📍 $it")
                }
            }

            // Status matni + rangi
            val statusText = order.statusDisplay ?: statusLabel(order.status)
            tvKitchenStatus.text = statusText
            tvKitchenStatus.setBackgroundResource(statusBadgeDrawable(order.status))
            tvKitchenStatus.setTextColor(
                ContextCompat.getColor(ctx, R.color.white)
            )

            // Keyingi qadam tugmasi
            val (btnText, nextStatus) = nextAction(order.status)
            btnNextStatus.text = btnText
            btnNextStatus.isEnabled = nextStatus.isNotEmpty()
            btnNextStatus.alpha = if (nextStatus.isNotEmpty()) 1f else 0.45f
            btnNextStatus.setOnClickListener {
                if (nextStatus.isNotEmpty()) onUpdateStatus(order.id, nextStatus)
            }
        }
    }

    override fun getItemCount(): Int = orders.size

    fun updateData(newOrders: List<FoodOrder>) {
        val diff = DiffUtil.calculateDiff(OrderDiffCallback(orders, newOrders))
        orders = newOrders
        diff.dispatchUpdatesTo(this)
    }

    // ─── Yordamchi funksiyalar ────────────────────────────────────────────────

    private fun statusLabel(status: String): String = when (status) {
        "new"        -> "🆕 Yangi"
        "preparing"  -> "🍳 Tayyorlanmoqda"
        "delivering" -> "🛵 Yetkazilmoqda"
        "completed"  -> "✅ Yakunlangan"
        "cancelled"  -> "❌ Bekor qilindi"
        else         -> status
    }

    private fun statusColor(status: String): Int = when (status) {
        "new"        -> R.color.status_new
        "preparing"  -> R.color.status_preparing
        "delivering" -> R.color.status_delivering
        "completed"  -> R.color.status_completed
        else         -> R.color.text_muted
    }

    private fun statusBadgeDrawable(status: String): Int = when (status) {
        "new"        -> R.drawable.status_badge_new
        "preparing"  -> R.drawable.status_badge_preparing
        "delivering" -> R.drawable.status_badge_delivering
        "completed"  -> R.drawable.status_badge_completed
        else         -> R.drawable.badge_bg
    }

    private fun nextAction(status: String): Pair<String, String> = when (status) {
        "new"        -> "🍳 Tayyorlashga olish"  to "preparing"
        "preparing"  -> "🛵 Kuryerga / Berish"   to "delivering"
        "delivering" -> "✅ Topshirish (Yakunlash)" to "completed"
        else         -> "✅ Yakunlangan"           to ""
    }

    // ─── DiffUtil ─────────────────────────────────────────────────────────────

    private class OrderDiffCallback(
        private val old: List<FoodOrder>,
        private val new: List<FoodOrder>
    ) : DiffUtil.Callback() {
        override fun getOldListSize(): Int = old.size
        override fun getNewListSize(): Int = new.size
        override fun areItemsTheSame(o: Int, n: Int): Boolean = old[o].id == new[n].id
        override fun areContentsTheSame(o: Int, n: Int): Boolean =
            old[o].status == new[n].status && old[o].totalAmount == new[n].totalAmount
    }
}
