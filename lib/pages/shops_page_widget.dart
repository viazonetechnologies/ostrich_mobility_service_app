import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/core/cubits/bottom_navigation_bar_index_cubit.dart';
import 'package:ostrich_service/features/service_center/presentation/widgets/list_views/service_center_speed_filter_list_view_widget.dart';
import 'package:ostrich_service/features/service_center/presentation/widgets/list_views/service_locations_list_view_widget.dart';
import 'package:ostrich_service/features/service_center/presentation/widgets/text_fields/search_service_center_text_field_widget.dart';

class ShopsPageWidget extends StatelessWidget {
  const ShopsPageWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) {
          // Change bottom navigation bar index number to [HomePage] index.
          const homePageIndexNumber = 0;
          BlocProvider.of<BottomNavigationBarIndexCubit>(
            context,
          ).changeIndex(homePageIndexNumber);
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: const Text(
            AppStrings.ostrichMobility,
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ),
        body: SafeArea(
          child: RefreshIndicator(
            onRefresh: () async {
              // Fetch the service location data.
            },
            child: ListView(
              children: [
                const Padding(
                  padding: EdgeInsets.only(left: 15.0, right: 15.0, top: 15.0),
                  child: Text(
                    AppStrings.nearestServiceCenter,
                    maxLines: 1,
                    style: TextStyle(
                      fontSize: 25.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(height: 10.0),
                const Padding(
                  padding: EdgeInsets.only(left: 15.0, right: 15.0),
                  child: SearchServiceCenterTextFieldWidget(),
                ),
                const SizedBox(height: 10.0),
                Builder(
                  builder: (context) {
                    /// child widget of [SizedBox] return list view of Material
                    /// button in horizontal direction.
                    ///
                    /// Access the height of button from [Theme] using context.
                    final boxHeight = Theme.of(context).buttonTheme.height + 5;
                    return SizedBox(
                      height: boxHeight,
                      child: const ServiceCenterSpeedFilterListViewWidget(),
                    );
                  },
                ),
                const SizedBox(height: 10.0),
                const Padding(
                  padding: EdgeInsets.only(left: 15.0, right: 15.0),
                  child: ServiceLocationsListViewWidget(),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
