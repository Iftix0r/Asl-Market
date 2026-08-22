package uz.aslmarket.aslfood.data.local

import android.content.Context
import uz.aslmarket.aslfood.data.model.AppRole

/**
 * Qurilmadagi rol va oshxona PIN ni SharedPreferences da saqlaydi.
 *
 * Har bir planshetda bir marta sozlanadi — keyingi ishga tushishlarda
 * rol tanlash ekrani ko'rsatilmaydi, to'g'ridan-to'g'ri tegishli rejimga o'tiladi.
 */
object RoleManager {

    private const val PREFS_NAME   = "aslfood_prefs"
    private const val KEY_ROLE     = "device_role"
    private const val KEY_PIN      = "kitchen_pin"
    private const val DEFAULT_PIN  = "1234"

    // ─── Rol ─────────────────────────────────────────────────────────────────

    fun getRole(ctx: Context): AppRole? {
        val prefs = ctx.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return AppRole.fromString(prefs.getString(KEY_ROLE, null))
    }

    fun setRole(ctx: Context, role: AppRole) {
        ctx.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_ROLE, role.name)
            .apply()
    }

    fun clearRole(ctx: Context) {
        ctx.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .remove(KEY_ROLE)
            .apply()
    }

    fun isRoleSet(ctx: Context): Boolean = getRole(ctx) != null

    // ─── PIN (Oshxona uchun) ──────────────────────────────────────────────────

    fun getPin(ctx: Context): String {
        return ctx.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getString(KEY_PIN, DEFAULT_PIN) ?: DEFAULT_PIN
    }

    fun setPin(ctx: Context, pin: String) {
        require(pin.length == 4 && pin.all { it.isDigit() }) {
            "PIN 4 ta raqamdan iborat bo'lishi kerak"
        }
        ctx.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_PIN, pin)
            .apply()
    }

    fun checkPin(ctx: Context, input: String): Boolean = input == getPin(ctx)
}
