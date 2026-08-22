package uz.aslmarket.aslfood.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import uz.aslmarket.aslfood.data.model.FoodItem
import uz.aslmarket.aslfood.databinding.ItemFoodBinding

class FoodAdapter(
    private var items: List<FoodItem>,
    private val onAddToCart: (FoodItem) -> Unit
) : RecyclerView.Adapter<FoodAdapter.FoodViewHolder>() {

    class FoodViewHolder(val binding: ItemFoodBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FoodViewHolder {
        val binding = ItemFoodBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return FoodViewHolder(binding)
    }

    override fun onBindViewHolder(holder: FoodViewHolder, position: Int) {
        val item = items[position]
        holder.binding.tvFoodName.text = item.name
        holder.binding.tvCategory.text = item.category ?: "Fast Food"
        holder.binding.tvIngredients.text = item.ingredients ?: "Yangi va tabiiy masalliqlar"
        holder.binding.tvPrice.text = "${item.price.toLong()} so'm"

        Glide.with(holder.itemView.context)
            .load(item.imageUrl)
            .placeholder(android.R.drawable.ic_menu_gallery)
            .into(holder.binding.ivFoodImage)

        holder.binding.btnAddToCart.setOnClickListener {
            onAddToCart(item)
        }
    }

    override fun getItemCount(): Int = items.size

    fun updateData(newItems: List<FoodItem>) {
        items = newItems
        notifyDataSetChanged()
    }
}
