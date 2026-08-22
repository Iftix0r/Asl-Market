package uz.aslmarket.aslfood.ui.adapter

import android.content.Context
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import uz.aslmarket.aslfood.R
import uz.aslmarket.aslfood.data.model.FoodCategory
import uz.aslmarket.aslfood.databinding.ItemCategoryBinding

class CategoryAdapter(
    private val categories: List<FoodCategory>,
    private val onCategoryClick: (FoodCategory?) -> Unit
) : RecyclerView.Adapter<CategoryAdapter.CategoryViewHolder>() {

    // 0 = "Barchasi", 1..n = real kategoriyalar (index + 1)
    private var selectedPosition: Int = 0

    class CategoryViewHolder(val binding: ItemCategoryBinding) :
        RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CategoryViewHolder {
        val binding = ItemCategoryBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return CategoryViewHolder(binding)
    }

    override fun onBindViewHolder(holder: CategoryViewHolder, position: Int) {
        val ctx: Context = holder.itemView.context
        val isSelected = position == selectedPosition

        if (position == 0) {
            holder.binding.tvCategoryName.text = ctx.getString(R.string.all_categories)
            holder.binding.root.setOnClickListener {
                val pos = holder.adapterPosition
                if (pos == RecyclerView.NO_POSITION) return@setOnClickListener
                updateSelection(pos)
                onCategoryClick(null)
            }
        } else {
            val cat = categories[position - 1]
            holder.binding.tvCategoryName.text = cat.name
            holder.binding.root.setOnClickListener {
                val pos = holder.adapterPosition
                if (pos == RecyclerView.NO_POSITION) return@setOnClickListener
                updateSelection(pos)
                onCategoryClick(cat)
            }
        }

        // Tanlangan chip — to'q rang; tanlalmagan — ochiq rang
        if (isSelected) {
            holder.binding.tvCategoryName.setBackgroundResource(R.drawable.badge_bg)
            holder.binding.tvCategoryName.setTextColor(
                ContextCompat.getColor(ctx, R.color.white)
            )
        } else {
            holder.binding.tvCategoryName.setBackgroundResource(R.drawable.chip_unselected)
            holder.binding.tvCategoryName.setTextColor(
                ContextCompat.getColor(ctx, R.color.amber_700)
            )
        }
    }

    override fun getItemCount(): Int = categories.size + 1

    private fun updateSelection(newPosition: Int) {
        val prev = selectedPosition
        selectedPosition = newPosition
        notifyItemChanged(prev)
        notifyItemChanged(newPosition)
    }
}
