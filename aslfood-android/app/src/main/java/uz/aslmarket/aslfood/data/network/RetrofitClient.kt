package uz.aslmarket.aslfood.data.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    private var BASE_URL = "https://aslmarket.uz/"

    // OkHttpClient bir marta quriladi (qayta ishlatiladi)
    private val okHttpClient: OkHttpClient by lazy {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .writeTimeout(15, TimeUnit.SECONDS)
            .build()
    }

    // apiService — har safar BASE_URL o'zgarganda yangi instance qaytaradi
    // Muammo: lazy val o'zgaruvchi BASE_URL ni birinchi qo'ng'iroqda "yopib oladi".
    // Yechim: fun sifatida ishlash — DI yoki setBaseUrl dan keyin to'g'ri URL ga ega bo'ladi.
    val apiService: ApiService
        get() = buildApiService()

    private fun buildApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }

    fun setBaseUrl(url: String) {
        if (url.isNotBlank()) {
            BASE_URL = if (url.endsWith("/")) url else "$url/"
        }
    }

    fun getBaseUrl(): String = BASE_URL
}
