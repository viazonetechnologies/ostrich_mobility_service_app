import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ostrich_service/features/tickets/presentation/widgets/list_views/service_tickets_list_view_widget.dart';
import 'package:ostrich_service/features/tickets/presentation/widgets/ticket_filter_options_list_widget.dart';
import 'package:ostrich_service/pages/home_page_widget.dart';

import '../../helpers/test_helpers.dart';

void main() {
  testWidgets('Home page widget test', (tester) async {
    await tester.binding.setSurfaceSize(testDeviceScreenSize);
    await tester.pumpWidget(const MaterialApp(home: HomePageWidget()));

    // Ensures that no overflow exception comes out!.
    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);

    // Find widgets
    expect(find.byType(TicketFilterOptionsListWidget), findsOneWidget);
    expect(find.byType(ServiceTicketsListViewWidget), findsOneWidget);
  });
}
