package com.example.ostrich_service.services

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities

/**
 * @return Boolean, indicates whether app has an active network connection or not!.
 *
 * ```
 * val isNetworkConnected = hasInternetAccess(context) // true If connected, else false.
 * ```
 * */
fun hasInternetAccess(context: Context): Boolean {
    val connectivityManager =
        context.getSystemService(ConnectivityManager::class.java)
                as ConnectivityManager

    val capabilities = connectivityManager.getNetworkCapabilities(connectivityManager.activeNetwork)

    return capabilities?.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) ?: false
}