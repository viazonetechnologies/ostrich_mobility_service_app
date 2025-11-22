import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/service_center/presentation/widgets/list_views/service_center_speed_filter_list_view_widget.dart';
import 'package:ostrich_service/features/service_center/presentation/widgets/list_views/service_locations_list_view_widget.dart';
import 'package:ostrich_service/features/service_center/presentation/widgets/text_fields/search_service_center_text_field_widget.dart';
import 'package:ostrich_service/pages/shops_page_widget.dart';

import '../../helpers/test_helpers.dart';

void main() {
  testWidgets('Shops page widget test', (tester) async {
    await tester.binding.setSurfaceSize(testDeviceScreenSize);
    await tester.pumpWidget(const MaterialApp(home: ShopsPageWidget()));

    // Ensures that no overflow error.
    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);

    // Find widgets
    expect(find.byType(SearchServiceCenterTextFieldWidget), findsOneWidget);
    expect(find.byType(ServiceCenterSpeedFilterListViewWidget), findsOneWidget);
    expect(find.byType(ServiceLocationsListViewWidget), findsOneWidget);

    // Find texts
    expect(find.text(AppStrings.nearestServiceCenter), findsOneWidget);
    expect(find.text(AppStrings.nearestServiceCenter), findsOneWidget);
  });
}
