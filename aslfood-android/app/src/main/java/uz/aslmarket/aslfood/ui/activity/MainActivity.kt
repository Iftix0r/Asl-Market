package uz.aslmarket.aslfood.ui.activity

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import uz.aslmarket.aslfood.R
import uz.aslmarket.aslfood.databinding.ActivityMainBinding
import uz.aslmarket.aslfood.ui.fragment.CartFragment
import uz.aslmarket.aslfood.ui.fragment.KitchenFragment
import uz.aslmarket.aslfood.ui.fragment.MenuFragment
import uz.aslmarket.aslfood.ui.fragment.TrackerFragment
import uz.aslmarket.aslfood.ui.viewmodel.MainViewModel

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Observe Cart Badge
        viewModel.cartCount.observe(this) { count ->
            binding.tvCartBadge.text = "Savat: $count"
        }

        // Set default fragment
        if (savedInstanceState == null) {
            loadFragment(MenuFragment())
        }

        binding.bottomNavigation.setOnItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_menu -> loadFragment(MenuFragment())
                R.id.nav_cart -> loadFragment(CartFragment())
                R.id.nav_tracker -> loadFragment(TrackerFragment())
                R.id.nav_kitchen -> loadFragment(KitchenFragment())
                else -> false
            }
        }
    }

    private fun loadFragment(fragment: Fragment): Boolean {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragmentContainer, fragment)
            .commit()
        return true
    }
}
