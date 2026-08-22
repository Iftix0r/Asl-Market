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

    // Fragment instance'lar bir marta yaratiladi, qayta ishlatiladi
    private val menuFragment     by lazy { MenuFragment() }
    private val cartFragment     by lazy { CartFragment() }
    private val trackerFragment  by lazy { TrackerFragment() }
    private val kitchenFragment  by lazy { KitchenFragment() }

    private var activeFragment: Fragment = menuFragment

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupFragments(savedInstanceState)
        setupBottomNavigation()
        observeCartBadge()
    }

    private fun setupFragments(savedInstanceState: Bundle?) {
        if (savedInstanceState == null) {
            // Barcha fragmentlarni qo'sh, faqat menu ko'rinsin
            supportFragmentManager.beginTransaction()
                .add(R.id.fragmentContainer, kitchenFragment,  TAG_KITCHEN).hide(kitchenFragment)
                .add(R.id.fragmentContainer, trackerFragment,  TAG_TRACKER).hide(trackerFragment)
                .add(R.id.fragmentContainer, cartFragment,     TAG_CART).hide(cartFragment)
                .add(R.id.fragmentContainer, menuFragment,     TAG_MENU)
                .commit()
            activeFragment = menuFragment
        } else {
            // Konfiguratsiya o'zgarganda (rotation) fragmentlarni topib olish
            activeFragment = supportFragmentManager.findFragmentByTag(TAG_MENU)
                ?: menuFragment
        }
    }

    private fun setupBottomNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { menuItem ->
            val target = when (menuItem.itemId) {
                R.id.nav_menu    -> menuFragment
                R.id.nav_cart    -> cartFragment
                R.id.nav_tracker -> trackerFragment
                R.id.nav_kitchen -> kitchenFragment
                else             -> return@setOnItemSelectedListener false
            }
            showFragment(target)
            true
        }
    }

    private fun showFragment(target: Fragment) {
        if (target == activeFragment) return
        supportFragmentManager.beginTransaction()
            .hide(activeFragment)
            .show(target)
            .commit()
        activeFragment = target
    }

    private fun observeCartBadge() {
        viewModel.cartCount.observe(this) { count ->
            if (count > 0) {
                binding.tvCartBadge.visibility = android.view.View.VISIBLE
                binding.tvCartBadge.text = count.toString()
            } else {
                binding.tvCartBadge.visibility = android.view.View.GONE
            }
        }
    }

    companion object {
        private const val TAG_MENU    = "tag_menu"
        private const val TAG_CART    = "tag_cart"
        private const val TAG_TRACKER = "tag_tracker"
        private const val TAG_KITCHEN = "tag_kitchen"
    }
}
