package uz.aslmarket.aslfood.ui.fragment

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import uz.aslmarket.aslfood.databinding.FragmentTrackerBinding
import uz.aslmarket.aslfood.ui.viewmodel.MainViewModel

class TrackerFragment : Fragment() {

    private var _binding: FragmentTrackerBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentTrackerBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.btnTrack.setOnClickListener {
            val code = binding.etOrderCode.text.toString().trim()
            if (code.isEmpty()) {
                Toast.makeText(requireContext(), "Buyurtma kodini kiriting", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            viewModel.trackOrder(code)
        }

        // Tracker uchun alohida isTrackLoading — menyu spinneriga ta'sir qilmaydi
        viewModel.isTrackLoading.observe(viewLifecycleOwner) { loading ->
            binding.pbTrackLoading.visibility = if (loading) View.VISIBLE else View.GONE
            binding.btnTrack.isEnabled = !loading
        }

        viewModel.trackedOrder.observe(viewLifecycleOwner) { order ->
            if (order != null) {
                binding.cardOrderDetails.visibility = View.VISIBLE
                binding.tvOrderCodeTitle.text = "#${order.orderCode}"
                binding.tvStatusDisplay.text = order.statusDisplay ?: order.status
                binding.tvOrderCustomer.text = buildString {
                    append("Mijoz: ${order.customerName}")
                    append("\nTelefon: ${order.phone}")
                    append("\nSana: ${order.createdAt}")
                    order.deliveryAddress?.takeIf { it.isNotBlank() }
                        ?.let { append("\nManzil: $it") }
                }
                binding.tvOrderTotal.text = "Summa: %,d so'm".format(order.totalAmount.toLong())

                val itemsText = order.items
                    ?.joinToString("\n") { "• ${it.qty}× ${it.name}  —  ${it.total.toLong()} so'm" }
                    ?: ""
                binding.tvOrderItemsList.text = itemsText
            } else {
                binding.cardOrderDetails.visibility = View.GONE
            }
        }

        viewModel.errorMessage.observe(viewLifecycleOwner) { msg ->
            if (!msg.isNullOrEmpty()) {
                Toast.makeText(requireContext(), msg, Toast.LENGTH_SHORT).show()
                viewModel.clearError()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
