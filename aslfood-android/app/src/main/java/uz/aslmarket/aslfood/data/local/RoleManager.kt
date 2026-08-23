package uz.aslmarket.aslfood.data.local

import android.content.Context
import uz.aslmarket.aslfood.data.model.AppRole

/**
 * Xodimlar plansheti va PIN kod sozlamalarini saqlash.
 * Ilova faqat Fast-Food xodimlari / oshxona terminali uchun mo'ljallangan.
 */
object RoleManager {

    private const val PREFS_NAME   = "aslfood_prefs"
    private const val KEY_ROLE     = "device_role"
    private const val KEY_PIN      = "kitchen_pin"
    private const val DEFAULT_PIN  = "1234"

    // ─── Rol ─────────────────────────────────────────────────────────────────

    fun getRole(ctx: Context): AppRole? {
        val prefs = ctx.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val roleStr = prefs.getString(KEY_ROLE, null)
        return if (roleStr != null) AppRole.fromString(roleStr) else AppRole.KITCHEN
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

    // ─── PIN (Xodimlar kirishi uchun) ──────────────────────────────────────────

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
