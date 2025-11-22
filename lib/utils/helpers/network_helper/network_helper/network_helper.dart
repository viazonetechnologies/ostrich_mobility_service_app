/// Abstract interface to the Network.
abstract interface class NetworkHelper {
  /// Whether the device has an active network or not.
  ///
  /// **Note**: By default is **false**. call the
  /// **startListenNetworkConnectionStatus** method to get the realtime result.
  ///
  bool get isNetworkActive;

  /// Returns internet connection active or not.
  Future<bool> get hasInternetAccess;

  /// Start to listen on the network connection status.
  void startListenNetworkConnectionStatus();

  /// Stop that listens on the network connection status.
  void stopListenNetworkConnectionStatus();
}
