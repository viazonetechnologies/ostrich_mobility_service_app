import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/tickets/presentation/providers/tickets_controller_provider.dart';
import 'package:ostrich_service/features/tickets/presentation/widgets/dialogs/update_status_dialog_widget.dart';
import 'package:provider/provider.dart';

class UpdateTicketStatusButtonWidget extends StatelessWidget {
  const UpdateTicketStatusButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialButton(
      elevation: 0.0,
      padding: const EdgeInsets.all(10.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10.0),
        side: const BorderSide(color: AppColors.primaryColor),
      ),
      textColor: AppColors.primaryColor,
      onPressed: () {
        // Go to the Details view page for tickets.
        showDialog(
          context: context,
          builder: (context) => ChangeNotifierProvider(
            create: (context) => TicketsControllerProvider(),
            child: const UpdateStatusDialogWidget(),
          ),
        );
      },
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        spacing: 10.0,
        children: [
          AppIcons.editIcon,
          Flexible(
            child: Text(
              AppStrings.updateStatus,
              style: TextStyle(fontWeight: FontWeight.normal),
            ),
          ),
        ],
      ),
    );
  }
}
