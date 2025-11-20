import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/cubits/obscure_password_cubit.dart';

class ObscurePasswordButtonWidget extends StatelessWidget {
  const ObscurePasswordButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      onPressed: () {
        BlocProvider.of<ObscurePasswordCubit>(context).switchObscure();
      },
      icon: BlocBuilder<ObscurePasswordCubit, bool>(
        builder: (context, state) =>
            state == true ? AppIcons.eyeIcon : AppIcons.eyeOffIcon,
      ),
    );
  }
}
