package uz.aslmarket.aslfood.ui.activity

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import uz.aslmarket.aslfood.data.local.RoleManager
import uz.aslmarket.aslfood.data.model.AppRole
import uz.aslmarket.aslfood.databinding.ActivityRoleSelectBinding

class RoleSelectActivity : AppCompatActivity() {

    private lateinit var binding: ActivityRoleSelectBinding
    private val pin = StringBuilder()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Agar xodim roli allaqachon biriktirilgan bo'lsa — to'g'ridan-to'g'ri asosiy terminalga o'tiladi
        if (RoleManager.getRole(this) != null) {
            openMain()
            return
        }

        binding = ActivityRoleSelectBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Mijoz kartasini yashirish — ilova faqat xodimlar uchun!
        binding.cardCustomer.visibility = View.GONE
        binding.cardPin.visibility = View.VISIBLE
        binding.tvPinError.visibility = View.GONE

        setupPinKeyboard()
    }

    private fun setupPinKeyboard() {
        val digitButtons = mapOf(
            0 to binding.btn0, 1 to binding.btn1, 2 to binding.btn2,
            3 to binding.btn3, 4 to binding.btn4, 5 to binding.btn5,
            6 to binding.btn6, 7 to binding.btn7, 8 to binding.btn8,
            9 to binding.btn9
        )
        digitButtons.forEach { (digit, button) ->
            button.setOnClickListener {
                if (pin.length < 4) pin.append(digit)
                updatePinDots()
                if (pin.length == 4) confirmKitchenPin()
            }
        }
        binding.btnPinClear.setOnClickListener {
            if (pin.isNotEmpty()) pin.deleteCharAt(pin.lastIndex)
            binding.tvPinError.visibility = View.GONE
            updatePinDots()
        }
    }

    private fun confirmKitchenPin() {
        if (RoleManager.checkPin(this, pin.toString())) {
            RoleManager.setRole(this, AppRole.KITCHEN)
            openMain()
        } else {
            binding.tvPinError.visibility = View.VISIBLE
            pin.clear()
            updatePinDots()
        }
    }

    private fun updatePinDots() {
        val dots = listOf(binding.dot1, binding.dot2, binding.dot3, binding.dot4)
        dots.forEachIndexed { index, dot ->
            dot.isSelected = index < pin.length
        }
    }

    private fun openMain() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}