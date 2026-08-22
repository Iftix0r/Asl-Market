package uz.aslmarket.aslfood.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import uz.aslmarket.aslfood.data.model.FoodCategory
import uz.aslmarket.aslfood.databinding.ItemCategoryBinding

class CategoryAdapter(
    private val categories: List<FoodCategory>,
    private val onCategoryClick: (FoodCategory?) -> Unit
) : RecyclerView.Adapter<CategoryAdapter.CategoryViewHolder>() {

    class CategoryViewHolder(val binding: ItemCategoryBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CategoryViewHolder {
        val binding = ItemCategoryBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return CategoryViewHolder(binding)
    }

    override fun onBindViewHolder(holder: CategoryViewHolder, position: Int) {
        if (position == 0) {
            holder.binding.tvCategoryName.text = "Barchasi"
            holder.binding.root.setOnClickListener { onCategoryClick(null) }
        } else {
            val cat = categories[position - 1]
            holder.binding.tvCategoryName.text = cat.name
            holder.binding.root.setOnClickListener { onCategoryClick(cat) }
        }
    }

    override fun getItemCount(): Int = categories.size + 1
}
