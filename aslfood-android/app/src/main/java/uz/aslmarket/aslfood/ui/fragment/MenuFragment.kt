package uz.aslmarket.aslfood.ui.fragment

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import uz.aslmarket.aslfood.databinding.FragmentMenuBinding
import uz.aslmarket.aslfood.ui.adapter.CategoryAdapter
import uz.aslmarket.aslfood.ui.adapter.FoodAdapter
import uz.aslmarket.aslfood.ui.viewmodel.MainViewModel

class MenuFragment : Fragment() {

    private var _binding: FragmentMenuBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    private lateinit var foodAdapter: FoodAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentMenuBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        foodAdapter = FoodAdapter(emptyList()) { foodItem ->
            viewModel.addToCart(foodItem)
            Toast.makeText(requireContext(), "${foodItem.name} savatga qo'shildi!", Toast.LENGTH_SHORT).show()
        }

        binding.rvFoodMenu.layoutManager = GridLayoutManager(requireContext(), 2)
        binding.rvFoodMenu.adapter = foodAdapter

        binding.rvCategories.layoutManager = LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)

        viewModel.categories.observe(viewLifecycleOwner) { categories ->
            binding.rvCategories.adapter = CategoryAdapter(categories) { selectedCat ->
                viewModel.fetchMenu(selectedCat?.slug)
            }
        }

        viewModel.menuItems.observe(viewLifecycleOwner) { items ->
            foodAdapter.updateData(items)
        }

        viewModel.isLoading.observe(viewLifecycleOwner) { loading ->
            binding.progressBar.visibility = if (loading) View.VISIBLE else View.GONE
        }

        binding.etSearch.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                viewModel.fetchMenu(query = s.toString())
            }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        })
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
