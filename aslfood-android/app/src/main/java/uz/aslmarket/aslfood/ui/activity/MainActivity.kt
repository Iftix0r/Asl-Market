package uz.aslmarket.aslfood.ui.activity

import android.os.Bundle
import android.view.View
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import uz.aslmarket.aslfood.R
import uz.aslmarket.aslfood.data.local.RoleManager
import uz.aslmarket.aslfood.data.model.AppRole
import uz.aslmarket.aslfood.databinding.ActivityMainBinding
import uz.aslmarket.aslfood.ui.fragment.CartFragment
import uz.aslmarket.aslfood.ui.fragment.KitchenFragment
import uz.aslmarket.aslfood.ui.fragment.MenuFragment
import uz.aslmarket.aslfood.ui.fragment.TrackerFragment
import uz.aslmarket.aslfood.ui.viewmodel.MainViewModel

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    private val menuFragment    by lazy { MenuFragment() }
    private val cartFragment    by lazy { CartFragment() }
    private val trackerFragment by lazy { TrackerFragment() }
    private val kitchenFragment by lazy { KitchenFragment() }

    private lateinit var role: AppRole
    private lateinit var activeFragment: Fragment

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Ilova faqat Xodimlar uchun — default AppRole.KITCHEN
        role = RoleManager.getRole(this) ?: AppRole.KITCHEN

        setupNav()
        setupFragments(savedInstanceState)
        setupBottomNavigation()
        observeCartBadge()
    }

    // ─── Nav visibility ────────────────────────────────────────────────────────

    private fun setupNav() {
        val menu = binding.bottomNavigation.menu
        // Xodimlar uchun barcha 4 ta bo'lim ochiq: Oshxona Kanban, Taomlar, Kassa va Tarix
        menu.findItem(R.id.nav_kitchen).isVisible = true
        menu.findItem(R.id.nav_menu).isVisible    = true
        menu.findItem(R.id.nav_cart).isVisible    = true
        menu.findItem(R.id.nav_tracker).isVisible = true

        binding.bottomNavigation.selectedItemId = R.id.nav_kitchen
        binding.tvCartBadge.visibility = View.GONE
    }

    // ─── Fragment setup ────────────────────────────────────────────────────────

    private fun setupFragments(savedInstanceState: Bundle?) {
        if (savedInstanceState != null) {
            activeFragment = supportFragmentManager.findFragmentByTag(TAG_KITCHEN) ?: kitchenFragment
            return
        }

        val tx = supportFragmentManager.beginTransaction()
        tx.add(R.id.fragmentContainer, trackerFragment, TAG_TRACKER).hide(trackerFragment)
          .add(R.id.fragmentContainer, cartFragment,    TAG_CART).hide(cartFragment)
          .add(R.id.fragmentContainer, menuFragment,    TAG_MENU).hide(menuFragment)
          .add(R.id.fragmentContainer, kitchenFragment, TAG_KITCHEN)
        activeFragment = kitchenFragment
        tx.commit()
    }

    // ─── Bottom nav ────────────────────────────────────────────────────────────

    private fun setupBottomNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            val target: Fragment = when (item.itemId) {
                R.id.nav_kitchen -> kitchenFragment
                R.id.nav_menu    -> menuFragment
                R.id.nav_cart    -> cartFragment
                R.id.nav_tracker -> trackerFragment
                else             -> return@setOnItemSelectedListener false
            }
            showFragment(target)
            true
        }
    }

    private fun showFragment(target: Fragment) {
        if (target == activeFragment) return
        if (!target.isAdded) {
            supportFragmentManager.beginTransaction()
                .hide(activeFragment)
                .add(R.id.fragmentContainer, target)
                .commit()
        } else {
            supportFragmentManager.beginTransaction()
                .hide(activeFragment)
                .show(target)
                .commit()
        }
        activeFragment = target
    }

    private fun observeCartBadge() {
        viewModel.cartCount.observe(this) { count ->
            binding.tvCartBadge.visibility = if (count > 0) View.VISIBLE else View.GONE
            binding.tvCartBadge.text = count.toString()
        }
    }

    companion object {
        private const val TAG_KITCHEN = "tag_kitchen"
        private const val TAG_MENU    = "tag_menu"
        private const val TAG_CART    = "tag_cart"
        private const val TAG_TRACKER = "tag_tracker"
    }
}
