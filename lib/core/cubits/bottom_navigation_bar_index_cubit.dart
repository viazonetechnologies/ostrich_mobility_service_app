import 'package:bloc/bloc.dart';

class BottomNavigationBarIndexCubit extends Cubit<int> {
  BottomNavigationBarIndexCubit() : super(0);

  void changeIndex(int index) {
    if (state != index) emit(index);
  }
}
