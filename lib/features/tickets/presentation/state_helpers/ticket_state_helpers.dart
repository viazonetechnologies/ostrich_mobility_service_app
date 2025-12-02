import 'package:ostrich_service/features/tickets/presentation/enums/tickets_filter_enum.dart';

class TicketStateHelpers {
  static const ticketFilters = [
    {'title': 'All', 'value': 'all', 'enum': TicketsFilterEnum.all},
    {
      'title': 'High Priority',
      'value': 'highPriority',
      'enum': TicketsFilterEnum.highPriority,
    },
    {'title': 'Nearby', 'value': 'nearBy', 'enum': TicketsFilterEnum.nearBy},
    {'title': 'Today', 'value': 'today', 'enum': TicketsFilterEnum.today},
  ];
}
