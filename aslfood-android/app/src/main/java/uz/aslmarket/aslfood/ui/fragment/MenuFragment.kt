package uz.aslmarket.aslfood.ui.fragment

import android.os.Bundle
import android.os.Handler
import android.os.Looper
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
    private lateinit var categoryAdapter: CategoryAdapter

    // Debounce: foydalanuvchi yozishni to'xtatganidan 350ms keyin API call
    private val searchHandler = Handler(Looper.getMainLooper())
    private var searchRunnable: Runnable? = null
    private var currentCategorySlug: String? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMenuBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupAdapters()
        setupSearch()
        observeViewModel()
        viewModel.fetchCategories()
        viewModel.fetchMenu()
    }

    private fun setupAdapters() {
        foodAdapter = FoodAdapter(emptyList()) { foodItem ->
            viewModel.addToCart(foodItem)
            Toast.makeText(
                requireContext(),
                "${foodItem.name} savatga qo'shildi!",
                Toast.LENGTH_SHORT
            ).show()
        }

        binding.rvFoodMenu.layoutManager = GridLayoutManager(requireContext(), 2)
        binding.rvFoodMenu.adapter = foodAdapter

        binding.rvCategories.layoutManager =
            LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
    }

    private fun setupSearch() {
        binding.etSearch.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                // Avvalgi pending callni bekor qilish
                searchRunnable?.let { searchHandler.removeCallbacks(it) }

                val query = s?.toString()?.trim() ?: ""
                searchRunnable = Runnable {
                    // Bo'sh qidiruvda kategoriya filterini saqlab qolish
                    viewModel.fetchMenu(
                        categorySlug = currentCategorySlug,
                        query = query.ifEmpty { null }
                    )
                }
                searchHandler.postDelayed(searchRunnable!!, 350L)
            }

            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        })
    }

    private fun observeViewModel() {
        viewModel.categories.observe(viewLifecycleOwner) { categories ->
            categoryAdapter = CategoryAdapter(categories) { selectedCat ->
                currentCategorySlug = selectedCat?.slug
                // Qidiruv matni bilan birga kategoriya filteri
                val query = binding.etSearch.text?.toString()?.trim()
                viewModel.fetchMenu(
                    categorySlug = currentCategorySlug,
                    query = query?.ifEmpty { null }
                )
            }
            binding.rvCategories.adapter = categoryAdapter
        }

        viewModel.menuItems.observe(viewLifecycleOwner) { items ->
            foodAdapter.updateData(items)
            binding.tvMenuEmpty.visibility =
                if (items.isEmpty()) View.VISIBLE else View.GONE
        }

        // Faqat menyu loading observer — boshqa fragmentlarga ta'sir qilmaydi
        viewModel.isMenuLoading.observe(viewLifecycleOwner) { loading ->
            binding.progressBar.visibility = if (loading) View.VISIBLE else View.GONE
        }

        viewModel.errorMessage.observe(viewLifecycleOwner) { msg ->
            if (!msg.isNullOrEmpty()) {
                Toast.makeText(requireContext(), msg, Toast.LENGTH_SHORT).show()
                viewModel.clearError()
            }
        }
    }

    override fun onDestroyView() {
        searchRunnable?.let { searchHandler.removeCallbacks(it) }
        super.onDestroyView()
        _binding = null
    }
}
