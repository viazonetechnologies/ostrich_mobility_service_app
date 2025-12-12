import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/tickets/presentation/providers/tickets_controller_provider.dart';
import 'package:provider/provider.dart';

class UpdateStatusTextFieldWidget extends StatelessWidget {
  const UpdateStatusTextFieldWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: Provider.of<TicketsControllerProvider>(
        context,
        listen: false,
      ).updateStatusController,
      decoration: const InputDecoration(
        helperText: AppStrings.optional,
        hintText: AppStrings.enterMessage,
      ),
      maxLength: 256,
      maxLines: null,
      onTapOutside: (_) => FocusManager.instance.primaryFocus?.unfocus(),
    );
  }
}
