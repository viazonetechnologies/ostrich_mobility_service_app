import 'package:bloc_test/bloc_test.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';

void main() {
  blocTest(
    'Obscure password test',
    build: () => ObscurePasswordCubit(),
    act: (bloc) => [bloc.switchObscure(), bloc.switchObscure()],
    expect: () => [false, true],
    tearDown: () async => await ObscurePasswordCubit().close(),
  );
}
