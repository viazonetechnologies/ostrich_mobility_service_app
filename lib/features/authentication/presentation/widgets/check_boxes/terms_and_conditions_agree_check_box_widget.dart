import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/terms_and_conditions_check_cubit.dart';

class TermsAndConditionsAgreeCheckBoxWidget extends StatelessWidget {
  const TermsAndConditionsAgreeCheckBoxWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<TermsAndConditionsCheckCubit, bool>(
      builder: (context, isChecked) {
        return Checkbox(
          // By default value needs to be false.
          value: isChecked,
          onChanged: (value) {
            BlocProvider.of<TermsAndConditionsCheckCubit>(
              context,
            ).switchCheck(value!);
          },
        );
      },
    );
  }
}
