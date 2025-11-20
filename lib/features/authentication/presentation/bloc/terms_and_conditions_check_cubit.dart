import 'package:bloc/bloc.dart';

class TermsAndConditionsCheckCubit extends Cubit<bool> {
  TermsAndConditionsCheckCubit() : super(false);

  void switchCheck(bool isChecked) => emit(isChecked);
}
