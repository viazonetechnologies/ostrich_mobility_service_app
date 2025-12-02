import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/features/tickets/presentation/widgets/buttons/update_ticket_status_button_widget.dart';
import 'package:ostrich_service/features/tickets/presentation/widgets/buttons/view_service_tickets_details_button_widget.dart';

class ServiceTicketsListViewWidget extends StatelessWidget {
  const ServiceTicketsListViewWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      itemBuilder: (context, index) {
        return Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(10.0),
            color: Colors.white,
          ),
          padding: const EdgeInsets.all(10.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            spacing: 5.0,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                spacing: 10.0,
                children: [
                  Flexible(
                    child: Text(
                      '#TKT-10$index',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(50.0),
                      color: const Color.fromARGB(255, 255, 243, 228),
                    ),
                    padding: const EdgeInsets.all(5.0),
                    child: const Text(
                      'Pending',
                      style: TextStyle(color: Colors.deepOrange),
                    ),
                  ),
                ],
              ),
              Text(
                'John Smith • 2.3 km away',
                style: TextStyle(color: AppColors.subtitleColor),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('CityRider Scooter - Pro Model'),
                  Text(
                    'Motor not functioning, battery drainage issue',
                    style: TextStyle(color: AppColors.subtitleColor),
                  ),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                spacing: 10.0,
                children: [
                  Flexible(
                    child: FittedBox(
                      child: Text(
                        'Scheduled: Today, 10:00 AM',
                        style: TextStyle(color: AppColors.subtitleColor),
                      ),
                    ),
                  ),
                  const Text(
                    'High Priority',
                    style: TextStyle(color: Colors.red),
                  ),
                ],
              ),
              const Row(
                spacing: 10.0,
                children: [
                  Expanded(child: ViewServiceTicketsDetailsButtonWidget()),
                  Expanded(child: UpdateTicketStatusButtonWidget()),
                ],
              ),
            ],
          ),
        );
      },
      itemCount: 25,
      padding: const EdgeInsets.only(top: 10.0, bottom: 10.0),
      separatorBuilder: (_, _) => const SizedBox(height: 10.0),
    );
  }
}
