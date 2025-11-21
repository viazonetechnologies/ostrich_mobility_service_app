import 'package:bloc/bloc.dart';

class ObscurePasswordCubit extends Cubit<bool> {
  ObscurePasswordCubit() : super(true);

  void switchObscure() => emit(!state);
}
