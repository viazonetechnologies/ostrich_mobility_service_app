package com.example.ostrich_service

import com.example.ostrich_service.services.NetworkConnectionListener
import com.example.ostrich_service.services.hasInternetAccess
import com.example.vehicle_management.components.showToast
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.EventChannel
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val methodChannelName = "ostrich_service"
    private val networkEventChannelName = "ostrich_service/network_status"
    private lateinit var networkConnectionListener: NetworkConnectionListener

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        networkConnectionListener = NetworkConnectionListener(this)

        // Event Channel to listen for network connection state
        EventChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            networkEventChannelName
        ).setStreamHandler(object : EventChannel.StreamHandler {
            override fun onListen(
                arguments: Any?,
                events: EventChannel.EventSink?
            ) {
                networkConnectionListener.setEventSink(events)
            }

            override fun onCancel(arguments: Any?) {
                networkConnectionListener.setEventSink(null)
            }
        })

        // Method Channel to access platform api's as one time
        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            methodChannelName
        ).setMethodCallHandler { call, result ->
            if (call.method == "hasInternetAccess") {
                val hasNetworkAccess = hasInternetAccess(this)
                result.success(hasNetworkAccess)
            } else if (call.method == "toast") {
                val toastMessage = call.argument<String>("message")
                showToast(this, toastMessage)
            }
        }
    }
}
