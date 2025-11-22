package com.example.vehicle_management.components

import android.content.Context
import android.widget.Toast

/**
 * Shows a Toast, with message.
 *
 * @param text The message to show on the UI.
 * */
fun showToast(context: Context, text: String?) {
    val duration = Toast.LENGTH_SHORT;
    val toast = Toast.makeText(context, text, duration)
    toast.show()
}