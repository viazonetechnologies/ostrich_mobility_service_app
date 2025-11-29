import 'dart:async';

import 'package:flutter/services.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/utils/helpers/network_helper/network_helper/network_helper.dart';

class NetworkHelperNativeImplementation implements NetworkHelper {
  StreamSubscription<dynamic>? _streamSubscription;

  bool _hasInternet = false;

  @override
  Future<bool> get hasInternetAccess async {
    try {
      final result = await GetIt.I<PlatformServices>().methodChannel
          .invokeMethod("hasInternetAccess");

      return result;
    } on PlatformException catch (_) {
      return false;
    }
  }

  @override
  bool get isNetworkActive => _hasInternet;

  @override
  void startListenNetworkConnectionStatus() {
    _streamSubscription = GetIt.I<PlatformServices>().eventChannel
        .receiveBroadcastStream()
        .listen((data) {
          _hasInternet = data == 'online' ? true : false;
        }, onError: (_) => _streamSubscription?.cancel());
  }

  @override
  void stopListenNetworkConnectionStatus() {
    _streamSubscription?.cancel();
  }
}
