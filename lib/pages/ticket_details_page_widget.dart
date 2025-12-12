import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';

class TicketDetailsPageWidget extends StatefulWidget {
  const TicketDetailsPageWidget({super.key});

  @override
  State<TicketDetailsPageWidget> createState() =>
      _TicketDetailsPageWidgetState();
}

class _TicketDetailsPageWidgetState extends State<TicketDetailsPageWidget> {
  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () {
            GoRouter.of(context).pop();
          },
          icon: AppIcons.arrowBackIcon,
          color: Colors.white,
        ),
        title: const Text(
          AppStrings.ticketDetails,
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
