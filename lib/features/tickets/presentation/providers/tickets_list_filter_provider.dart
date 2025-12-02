import 'package:flutter/foundation.dart';
import 'package:ostrich_service/features/tickets/presentation/enums/tickets_filter_enum.dart';

class TicketsListFilterProvider with ChangeNotifier {
  String _filter = 'all';

  /// Returns the selected filter. Defaults to **all**.
  String get filter => _filter;

  void changeFilter(TicketsFilterEnum filter) {
    switch (filter) {
      case TicketsFilterEnum.all:
        _filter = 'all';
        break;
      case TicketsFilterEnum.highPriority:
        _filter = 'highPriority';
        break;
      case TicketsFilterEnum.nearBy:
        _filter = 'nearBy';
        break;
      case TicketsFilterEnum.today:
        _filter = 'today';
        break;
    }
    notifyListeners();
  }
}
