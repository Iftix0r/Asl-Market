package uz.aslmarket.aslfood.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.RecyclerView
import uz.aslmarket.aslfood.data.model.CartItem
import uz.aslmarket.aslfood.databinding.ItemCartBinding

class CartAdapter(
    private var items: List<CartItem>,
    private val onQuantityChange: (Long, Int) -> Unit
) : RecyclerView.Adapter<CartAdapter.CartViewHolder>() {

    class CartViewHolder(val binding: ItemCartBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CartViewHolder {
        val binding = ItemCartBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return CartViewHolder(binding)
    }

    override fun onBindViewHolder(holder: CartViewHolder, position: Int) {
        val item = items[position]
        with(holder.binding) {
            tvCartFoodName.text  = item.foodItem.name
            tvCartUnitPrice.text = "%,d so'm".format(item.foodItem.price.toLong())
            tvQty.text           = item.quantity.toString()
            tvSubtotal.text      = "%,d so'm".format(item.subtotal.toLong())

            btnMinus.setOnClickListener {
                val pos = holder.adapterPosition
                if (pos != RecyclerView.NO_POSITION) onQuantityChange(items[pos].foodItem.id, -1)
            }
            btnPlus.setOnClickListener {
                val pos = holder.adapterPosition
                if (pos != RecyclerView.NO_POSITION) onQuantityChange(items[pos].foodItem.id, 1)
            }
        }
    }

    override fun getItemCount(): Int = items.size

    fun updateData(newItems: List<CartItem>) {
        val diff = DiffUtil.calculateDiff(CartDiffCallback(items, newItems))
        items = newItems
        diff.dispatchUpdatesTo(this)
    }

    private class CartDiffCallback(
        private val old: List<CartItem>,
        private val new: List<CartItem>
    ) : DiffUtil.Callback() {
        override fun getOldListSize() = old.size
        override fun getNewListSize() = new.size
        override fun areItemsTheSame(o: Int, n: Int) = old[o].foodItem.id == new[n].foodItem.id
        override fun areContentsTheSame(o: Int, n: Int) =
            old[o].quantity == new[n].quantity && old[o].subtotal == new[n].subtotal
    }
}
