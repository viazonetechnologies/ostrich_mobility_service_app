import 'package:bloc_test/bloc_test.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/terms_and_conditions_check_cubit.dart';

void main() {
  blocTest(
    'Terms and conditions check cubit test',
    build: () => TermsAndConditionsCheckCubit(),
    act: (bloc) => [bloc.switchCheck(false), bloc.switchCheck(true)],
    tearDown: () => TermsAndConditionsCheckCubit().close(),
    expect: () => [false, true],
  );
}
