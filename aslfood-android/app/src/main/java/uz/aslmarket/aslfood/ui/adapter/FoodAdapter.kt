package uz.aslmarket.aslfood.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
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
        val binding = ItemFoodBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return FoodViewHolder(binding)
    }

    override fun onBindViewHolder(holder: FoodViewHolder, position: Int) {
        val item = items[position]
        with(holder.binding) {
            tvFoodName.text    = item.name
            tvCategory.text    = item.category ?: "Fast Food"
            tvIngredients.text = item.ingredients ?: "Yangi va tabiiy masalliqlar"
            tvPrice.text       = "%,d so'm".format(item.price.toLong())

            Glide.with(holder.itemView.context)
                .load(item.imageUrl)
                .placeholder(android.R.drawable.ic_menu_gallery)
                .into(ivFoodImage)

            btnAddToCart.setOnClickListener { onAddToCart(item) }
        }
    }

    override fun getItemCount(): Int = items.size

    /**
     * DiffUtil bilan yangilash — faqat o'zgargan elementlar qayta chiziladi,
     * butun ro'yxat emas. RecyclerView animatsiyalari ham ishlaydi.
     */
    fun updateData(newItems: List<FoodItem>) {
        val diff = DiffUtil.calculateDiff(FoodDiffCallback(items, newItems))
        items = newItems
        diff.dispatchUpdatesTo(this)
    }

    // ─── DiffUtil Callback ────────────────────────────────────────────────────

    private class FoodDiffCallback(
        private val old: List<FoodItem>,
        private val new: List<FoodItem>
    ) : DiffUtil.Callback() {

        override fun getOldListSize(): Int = old.size
        override fun getNewListSize(): Int = new.size

        override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean =
            old[oldPos].id == new[newPos].id

        override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean =
            old[oldPos] == new[newPos]
    }
}
