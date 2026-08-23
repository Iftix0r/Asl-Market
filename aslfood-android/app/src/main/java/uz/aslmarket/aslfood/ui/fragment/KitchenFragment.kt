package uz.aslmarket.aslfood.ui.fragment

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import uz.aslmarket.aslfood.R

    private fun setupRecyclerView() {
        kitchenAdapter = KitchenOrderAdapter(emptyList()) { orderId, newStatus ->
            viewModel.updateOrderStatus(orderId, newStatus)
        }
        val screenWidthDp = resources.configuration.screenWidthDp
        val spanCount = when {
            screenWidthDp >= 900 -> 3
            screenWidthDp >= 550 -> 2
            else                 -> 1
        }
        if (spanCount > 1) {
            binding.rvKitchenOrders.layoutManager = GridLayoutManager(requireContext(), spanCount)
        } else {
            binding.rvKitchenOrders.layoutManager = LinearLayoutManager(requireContext())
        }
        binding.rvKitchenOrders.adapter = kitchenAdapter
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefresh.setColorSchemeResources(R.color.amber_600, R.color.emerald_600)
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.fetchKitchenOrders(selectedStatus)
        }
    }

    private fun setupStatusFilter() {
        val chips = listOf(
            binding.chipAll       to null,
            binding.chipNew       to "new",
            binding.chipPreparing to "preparing",
            binding.chipDelivering to "delivering",
            binding.chipCompleted to "completed"
        )

        chips.forEach { (chip, status) ->
            chip.setOnClickListener {
                selectedStatus = status
                updateChipSelection(chip)
                viewModel.fetchKitchenOrders(selectedStatus)
            }
        }

        // Boshlang'ich holat: "Barchasi" tanlangan
        updateChipSelection(binding.chipAll)
    }

    private fun updateChipSelection(selected: TextView) {
        val allChips = listOf(
            binding.chipAll,
            binding.chipNew,
            binding.chipPreparing,
            binding.chipDelivering,
            binding.chipCompleted
        )
        allChips.forEach { chip ->
            if (chip == selected) {
                chip.setBackgroundResource(R.drawable.badge_bg)
                chip.setTextColor(ContextCompat.getColor(requireContext(), R.color.white))
            } else {
                chip.setBackgroundResource(R.drawable.chip_unselected)
                chip.setTextColor(ContextCompat.getColor(requireContext(), R.color.amber_700))
            }
        }
    }

    private fun observeViewModel() {
        viewModel.kitchenOrders.observe(viewLifecycleOwner) { orders ->
            kitchenAdapter.updateData(orders)
            binding.swipeRefresh.isRefreshing = false

            val isEmpty = orders.isEmpty()
            binding.layoutKitchenEmpty.visibility = if (isEmpty) View.VISIBLE else View.GONE
            binding.rvKitchenOrders.visibility    = if (isEmpty) View.GONE  else View.VISIBLE
        }

        viewModel.isKitchenLoading.observe(viewLifecycleOwner) { loading ->
            binding.pbKitchenLoading.visibility = if (loading) View.VISIBLE else View.GONE
            if (!loading) binding.swipeRefresh.isRefreshing = false
        }

        viewModel.errorMessage.observe(viewLifecycleOwner) { msg ->
            if (!msg.isNullOrEmpty()) {
                binding.swipeRefresh.isRefreshing = false
                Toast.makeText(requireContext(), msg, Toast.LENGTH_SHORT).show()
                viewModel.clearError()
            }
        }
    }

    private fun startAutoRefresh() {
        refreshHandler.postDelayed(autoRefreshRunnable, autoRefreshInterval)
        updateRefreshStatus()
    }

    private fun updateRefreshStatus() {
        binding.tvRefreshStatus.text =
            getString(R.string.kitchen_refresh_auto, autoRefreshInterval.toInt() / 1000)
    }

    override fun onResume() {
        super.onResume()
        // Fragment ekranga qaytganda ham yangilash
        viewModel.fetchKitchenOrders(selectedStatus)
        refreshHandler.removeCallbacks(autoRefreshRunnable)
        refreshHandler.postDelayed(autoRefreshRunnable, autoRefreshInterval)
    }

    override fun onPause() {
        super.onPause()
        // Fon rejimda timer to'xtatish — batareya tejash
        refreshHandler.removeCallbacks(autoRefreshRunnable)
    }

    override fun onDestroyView() {
        refreshHandler.removeCallbacks(autoRefreshRunnable)
        super.onDestroyView()
        _binding = null
    }
}
