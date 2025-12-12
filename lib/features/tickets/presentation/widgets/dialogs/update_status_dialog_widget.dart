import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/core/widgets/dialog_close_button_widget.dart';
import 'package:ostrich_service/features/tickets/presentation/providers/tickets_controller_provider.dart';
import 'package:ostrich_service/features/tickets/presentation/widgets/text_fields/update_status_text_field_widget.dart';
import 'package:provider/provider.dart';

class UpdateStatusDialogWidget extends StatelessWidget {
  const UpdateStatusDialogWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      actions: [
        MaterialButton(
          color: AppColors.primaryColor,
          elevation: 0.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10.0),
          ),
          textColor: Colors.white,
          onPressed: () {
            final updateMessage = Provider.of<TicketsControllerProvider>(
              context,
              listen: false,
            ).updateStatus;
            if (updateMessage.isNotEmpty) return;
            Navigator.pop(context);
          },
          child: const Text(AppStrings.update),
        ),
        const DialogCloseButtonWidget(),
      ],
      actionsAlignment: MainAxisAlignment.center,
      content: const SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          spacing: 10.0,
          children: [
            Text(
              AppStrings.message,
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            UpdateStatusTextFieldWidget(),
          ],
        ),
      ),
      contentPadding: const EdgeInsets.all(15.0),
    );
  }
}
