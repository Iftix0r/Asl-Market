package uz.aslmarket.aslfood.ui.fragment

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import uz.aslmarket.aslfood.databinding.FragmentCartBinding
import uz.aslmarket.aslfood.ui.adapter.CartAdapter
import uz.aslmarket.aslfood.ui.viewmodel.MainViewModel

class CartFragment : Fragment() {

    private var _binding: FragmentCartBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    private lateinit var cartAdapter: CartAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentCartBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        cartAdapter = CartAdapter(emptyList()) { foodId, delta ->
            viewModel.updateCartQuantity(foodId, delta)
        }

        binding.rvCartItems.layoutManager = LinearLayoutManager(requireContext())
        binding.rvCartItems.adapter = cartAdapter

        viewModel.cartItems.observe(viewLifecycleOwner) { items ->
            cartAdapter.updateData(items)
        }

        viewModel.cartTotal.observe(viewLifecycleOwner) { total ->
            binding.tvTotalAmount.text = "Jami: ${total.toLong()} so'm"
        }

        viewModel.placedOrderResult.observe(viewLifecycleOwner) { result ->
            result?.let {
                Toast.makeText(requireContext(), "Buyurtma qabul qilindi! Kodi: #${it.orderCode}", Toast.LENGTH_LONG).show()
                viewModel.resetPlacedOrderResult()
            }
        }

        binding.btnSubmitOrder.setOnClickListener {
            val name = binding.etCustomerName.text.toString().trim()
            val phone = binding.etPhone.text.toString().trim()
            val address = binding.etAddress.text.toString().trim()

            if (name.isEmpty() || phone.isEmpty()) {
                Toast.makeText(requireContext(), "Ism va telefon raqamingizni kiriting", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            viewModel.placeOrder(name, phone, address, "delivery", "naqd")
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
