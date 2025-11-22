package com.example.ostrich_service.services

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.os.Handler
import android.os.Looper
import io.flutter.plugin.common.EventChannel

class NetworkConnectionListener(context: Context) {
    private var eventSink: EventChannel.EventSink? = null
    private val connectivityManager =
        context.getSystemService(ConnectivityManager::class.java) as ConnectivityManager
    private val handler = Handler(Looper.getMainLooper())

    private val networkRequest = NetworkRequest.Builder()
        .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
        .addTransportType(NetworkCapabilities.TRANSPORT_CELLULAR)
        .build()

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            super.onAvailable(network)
            handler.post {
                eventSink?.success("online")
            }
        }

        override fun onCapabilitiesChanged(
            network: Network,
            networkCapabilities: NetworkCapabilities
        ) {
            super.onCapabilitiesChanged(network, networkCapabilities)
            val unmetered =
                networkCapabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_NOT_METERED)
            val isInternet =
                networkCapabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)

            if (isInternet) {
                handler.post {
                    eventSink?.success("online")
                }
            } else {
                handler.post {
                    eventSink?.success("offline")
                }
            }
        }

        override fun onLost(network: Network) {
            super.onLost(network)
            handler.post {
                eventSink?.success("offline")
            }
        }
    }

    fun setEventSink(sink: EventChannel.EventSink?) {
        this.eventSink = sink
        if (sink != null) {
            connectivityManager.requestNetwork(networkRequest, networkCallback)
        } else {
            connectivityManager.unregisterNetworkCallback(networkCallback)
        }
    }
}