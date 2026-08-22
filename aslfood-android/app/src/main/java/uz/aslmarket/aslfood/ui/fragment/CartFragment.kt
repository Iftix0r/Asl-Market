package uz.aslmarket.aslfood.ui.fragment

import android.app.Dialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.Window
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import uz.aslmarket.aslfood.R
import uz.aslmarket.aslfood.databinding.FragmentCartBinding
import uz.aslmarket.aslfood.ui.adapter.CartAdapter
import uz.aslmarket.aslfood.ui.viewmodel.MainViewModel

class CartFragment : Fragment() {

    private var _binding: FragmentCartBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    private lateinit var cartAdapter: CartAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCartBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupSubmitButton()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        cartAdapter = CartAdapter(emptyList()) { foodId, delta ->
            viewModel.updateCartQuantity(foodId, delta)
        }
        binding.rvCartItems.layoutManager = LinearLayoutManager(requireContext())
        binding.rvCartItems.adapter = cartAdapter
    }

    private fun setupSubmitButton() {
        binding.btnSubmitOrder.setOnClickListener {
            val name = binding.etCustomerName.text.toString().trim()
            val phone = binding.etPhone.text.toString().trim()
            val address = binding.etAddress.text.toString().trim()

            when {
                name.isEmpty() -> {
                    binding.etCustomerName.error = "Ismingizni kiriting"
                    binding.etCustomerName.requestFocus()
                }
                phone.isEmpty() -> {
                    binding.etPhone.error = "Telefon raqamingizni kiriting"
                    binding.etPhone.requestFocus()
                }
                else -> {
                    viewModel.placeOrder(name, phone, address, "delivery", "naqd")
                }
            }
        }
    }

    private fun observeViewModel() {
        // Savat elementlari — bo'sh/to'liq holatni boshqarish
        viewModel.cartItems.observe(viewLifecycleOwner) { items ->
            cartAdapter.updateData(items)
            val isEmpty = items.isEmpty()
            binding.layoutEmptyCart.visibility = if (isEmpty) View.VISIBLE else View.GONE
            binding.rvCartItems.visibility    = if (isEmpty) View.GONE  else View.VISIBLE
            binding.cardCheckout.visibility   = if (isEmpty) View.GONE  else View.VISIBLE
        }

        // Jami summa
        viewModel.cartTotal.observe(viewLifecycleOwner) { total ->
            binding.tvTotalAmount.text = "Jami: %,d so'm".format(total.toLong())
        }

        // Buyurtma berish loading
        viewModel.isOrderLoading.observe(viewLifecycleOwner) { loading ->
            binding.btnSubmitOrder.isEnabled = !loading
            binding.pbOrderLoading.visibility = if (loading) View.VISIBLE else View.GONE
            if (loading) {
                binding.btnSubmitOrder.text = ""
            } else {
                binding.btnSubmitOrder.text = getString(R.string.checkout)
            }
        }

        // Buyurtma muvaffaqiyatli berildi
        viewModel.placedOrderResult.observe(viewLifecycleOwner) { result ->
            result ?: return@observe
            showOrderSuccessDialog(result.orderCode ?: "—")
            viewModel.resetPlacedOrderResult()
        }

        // Xato xabari
        viewModel.errorMessage.observe(viewLifecycleOwner) { msg ->
            if (!msg.isNullOrEmpty()) {
                Toast.makeText(requireContext(), msg, Toast.LENGTH_LONG).show()
                viewModel.clearError()
            }
        }
    }

    /**
     * Buyurtma muvaffaqiyatli qabul qilinganda chiroyli dialog ko'rsatadi.
     * Foydalanuvchi buyurtma kodini dialog ichida ko'radi.
     */
    private fun showOrderSuccessDialog(orderCode: String) {
        val ctx = context ?: return
        val dialog = Dialog(ctx)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_order_success)

        // Rounded corners uchun window transparent bo'lishi shart
        dialog.window?.apply {
            setBackgroundDrawableResource(android.R.color.transparent)
            // Ekran kengligining 88% — kichik va katta ekranlarda mos ko'rinadi
            val width = (ctx.resources.displayMetrics.widthPixels * 0.88).toInt()
            setLayout(width, ViewGroup.LayoutParams.WRAP_CONTENT)
        }
        dialog.setCancelable(false)

        dialog.findViewById<TextView>(R.id.tvSuccessOrderCode).text = "#$orderCode"
        dialog.findViewById<Button>(R.id.btnSuccessOk).setOnClickListener {
            dialog.dismiss()
            binding.etCustomerName.text?.clear()
            binding.etPhone.text?.clear()
            binding.etAddress.text?.clear()
        }

        dialog.show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
