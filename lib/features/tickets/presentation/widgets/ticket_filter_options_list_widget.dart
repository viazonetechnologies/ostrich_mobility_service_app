import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/features/tickets/presentation/enums/tickets_filter_enum.dart';
import 'package:ostrich_service/features/tickets/presentation/providers/tickets_list_filter_provider.dart';
import 'package:ostrich_service/features/tickets/presentation/state_helpers/ticket_state_helpers.dart';
import 'package:provider/provider.dart';

class TicketFilterOptionsListWidget extends StatefulWidget {
  const TicketFilterOptionsListWidget({super.key});

  @override
  State<TicketFilterOptionsListWidget> createState() =>
      _TicketFilterOptionsListWidgetState();
}

class _TicketFilterOptionsListWidgetState
    extends State<TicketFilterOptionsListWidget> {
  late List<Map<String, dynamic>> _filters;

  @override
  void initState() {
    super.initState();
    _filters = TicketStateHelpers.ticketFilters;
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      spacing: 5.0,
      children: _filters.map((item) {
        return Expanded(
          flex: item['value'] == 'highPriority' ? 3 : 2,
          child: Consumer<TicketsListFilterProvider>(
            builder: (context, state, _) {
              return MaterialButton(
                color: state.filter == item['value']
                    ? AppColors.primaryColor
                    : Colors.white,
                elevation: 0.0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(50.0),
                  side: BorderSide(color: Colors.grey[300]!),
                ),
                textColor: state.filter == item['value'] ? Colors.white : null,
                onPressed: () {
                  Provider.of<TicketsListFilterProvider>(
                    context,
                    listen: false,
                  ).changeFilter(item['enum'] as TicketsFilterEnum);
                },
                child: FittedBox(
                  child: Text(item['title'] as String, maxLines: 1),
                ),
              );
            },
          ),
        );
      }).toList(),
    );
  }
}
