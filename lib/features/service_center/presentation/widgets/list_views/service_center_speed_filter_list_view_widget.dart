import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/features/service_center/presentation/state_helpers/service_center_state_helper.dart';

class ServiceCenterSpeedFilterListViewWidget extends StatelessWidget {
  const ServiceCenterSpeedFilterListViewWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      itemBuilder: (context, index) {
        final name =
            ServiceCenterStateHelper.serviceCenterSpeedFilters[index]['name'];
        return MaterialButton(
          color: AppColors.primaryColor,
          elevation: 0.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(50.0),
          ),
          textColor: Colors.white,
          onPressed: () {},
          child: Text(name!),
        );
      },
      padding: const EdgeInsets.only(left: 15.0, right: 15.0),
      scrollDirection: Axis.horizontal,
      separatorBuilder: (_, _) => const SizedBox(width: 10.0),
      itemCount: ServiceCenterStateHelper.serviceCenterSpeedFilters.length,
    );
  }
}
