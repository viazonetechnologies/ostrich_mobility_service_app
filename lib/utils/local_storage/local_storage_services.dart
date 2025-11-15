/// Abstract interface to Local storage.
abstract interface class LocalStorageServices {
  /// GET an item from the local storage.
  ///
  /// [key] Key used when storing the item on local storage.
  /// returns either [String] or [Null]
  Future<String?> getItem(String key);

  /// SET an item on local storage.
  ///
  /// [key] Name of key for storing the value.
  /// [value] Data to store on local storage.
  Future<void> setItem(String key, String value);
}
