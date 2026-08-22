package uz.aslmarket.aslfood.ui.fragment

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import uz.aslmarket.aslfood.databinding.FragmentKitchenBinding
import uz.aslmarket.aslfood.ui.adapter.KitchenOrderAdapter
import uz.aslmarket.aslfood.ui.viewmodel.MainViewModel

class KitchenFragment : Fragment() {

    private var _binding: FragmentKitchenBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    private lateinit var kitchenAdapter: KitchenOrderAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentKitchenBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        kitchenAdapter = KitchenOrderAdapter(emptyList()) { orderId, newStatus ->
            viewModel.updateOrderStatus(orderId, newStatus)
        }

        binding.rvKitchenOrders.layoutManager = LinearLayoutManager(requireContext())
        binding.rvKitchenOrders.adapter = kitchenAdapter

        viewModel.kitchenOrders.observe(viewLifecycleOwner) { orders ->
            kitchenAdapter.updateData(orders)
        }

        viewModel.fetchKitchenOrders()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
