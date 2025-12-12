import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/utils/helpers/platform_helper.dart';

class ServiceLocationsListViewWidget extends StatelessWidget {
  const ServiceLocationsListViewWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemBuilder: (context, index) {
        return Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(10.0),
            color: Colors.white,
          ),
          padding: const EdgeInsets.all(15.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            spacing: 5.0,
            children: [
              // Location and status
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                spacing: 10.0,
                children: [
                  const Flexible(
                    child: Text(
                      'Ostrich Mobility Downtown',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(15.0),
                      color: const Color.fromARGB(255, 225, 255, 190),
                    ),
                    padding: const EdgeInsets.all(5.0),
                    child: const Text(
                      'Open',
                      style: TextStyle(color: Colors.green),
                    ),
                  ),
                ],
              ),
              // Distance
              const Text(
                '1.2 miles away',
                style: TextStyle(color: AppColors.primaryColor),
              ),
              // Location
              Row(
                spacing: 5.0,
                children: [
                  AppIcons.locationIcon,
                  Flexible(
                    child: Text(
                      '123 Main Street, Downtown, NY 10001',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(color: AppColors.subtitleColor),
                    ),
                  ),
                ],
              ),
              // Time Availability
              Row(
                spacing: 5.0,
                children: [
                  AppIcons.timeIcon,
                  Flexible(
                    child: Text(
                      'Mon-Fri: 9AM-6PM, Sat: 10AM-4PM',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(color: AppColors.subtitleColor),
                    ),
                  ),
                ],
              ),
              // Direction and Call
              Row(
                spacing: 5.0,
                children: [
                  Expanded(
                    child: MaterialButton(
                      onPressed: () {
                        // Open Maps.
                        final latitude = '9.979882';
                        final longitude = '76.580307';
                        PlatformHelper.launchMaps(latitude, longitude);
                      },
                      color: AppColors.primaryColor,
                      elevation: 0.0,
                      padding: const EdgeInsets.all(10.0),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10.0),
                      ),
                      textColor: Colors.white,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        mainAxisSize: MainAxisSize.min,
                        spacing: 5.0,
                        children: [
                          Icon(AppIcons.mapIcon.icon),
                          const Flexible(
                            child: Text(
                              AppStrings.directions,
                              style: TextStyle(fontWeight: FontWeight.normal),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Expanded(
                    child: MaterialButton(
                      onPressed: () {
                        // Open default call app.
                        final phone = '+919999999999';
                        PlatformHelper.launchCallApp(phone);
                      },
                      elevation: 0.0,
                      padding: const EdgeInsets.all(10.0),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10.0),
                        side: const BorderSide(color: AppColors.primaryColor),
                      ),
                      textColor: AppColors.primaryColor,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        mainAxisSize: MainAxisSize.min,
                        spacing: 5.0,
                        children: [
                          Icon(AppIcons.phoneIcon.icon),
                          const Flexible(
                            child: Text(
                              AppStrings.call,
                              style: TextStyle(fontWeight: FontWeight.normal),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
      itemCount: 5,
      separatorBuilder: (_, _) => const SizedBox(height: 10.0),
    );
  }
}
