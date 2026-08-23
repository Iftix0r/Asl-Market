package uz.aslmarket.aslfood.data.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import uz.aslmarket.aslfood.BuildConfig
import java.util.concurrent.TimeUnit

object RetrofitClient {

    private var BASE_URL = "https://aslmarket.uz/"

    private val okHttpClient: OkHttpClient by lazy {
        val builder = OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .writeTimeout(15, TimeUnit.SECONDS)

        // Logging faqat debug build da — release da tarmoq trafigi loglarga chiqmaydi
        if (BuildConfig.DEBUG) {
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            builder.addInterceptor(logging)
        }

        builder.build()
    }

    val apiService: ApiService
        get() = buildApiService()

    private fun buildApiService(): ApiService =
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)

    fun setBaseUrl(url: String) {
        if (url.isNotBlank()) {
            BASE_URL = if (url.endsWith("/")) url else "$url/"
        }
    }

    fun getBaseUrl(): String = BASE_URL
}
