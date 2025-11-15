import 'package:bloc_test/bloc_test.dart';
import 'package:ostrich_service/core/cubits/bottom_navigation_bar_index_cubit.dart';

void main() {
  blocTest(
    'Bottom navigation bar index cubit test',
    build: () => BottomNavigationBarIndexCubit(),
    act: (bloc) => [bloc.changeIndex(5), bloc.changeIndex(3)],
    expect: () => [5, 3],
    tearDown: () => BottomNavigationBarIndexCubit().close(),
  );
}
