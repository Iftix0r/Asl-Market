package uz.aslmarket.aslfood.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
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
        holder.binding.tvCartFoodName.text = item.foodItem.name
        holder.binding.tvCartUnitPrice.text = "${item.foodItem.price.toLong()} so'm"
        holder.binding.tvQty.text = item.quantity.toString()
        holder.binding.tvSubtotal.text = "${item.subtotal.toLong()} so'm"

        holder.binding.btnMinus.setOnClickListener {
            onQuantityChange(item.foodItem.id, -1)
        }
        holder.binding.btnPlus.setOnClickListener {
            onQuantityChange(item.foodItem.id, 1)
        }
    }

    override fun getItemCount(): Int = items.size

    fun updateData(newItems: List<CartItem>) {
        items = newItems
        notifyDataSetChanged()
    }
}
