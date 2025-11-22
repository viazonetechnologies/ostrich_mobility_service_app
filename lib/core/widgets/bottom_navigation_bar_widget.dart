import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/core/cubits/bottom_navigation_bar_index_cubit.dart';

class BottomNavigationBarWidget extends StatelessWidget {
  const BottomNavigationBarWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      /// When adding [SafeArea] parent, BottomNavigation bar will show above on
      /// the system navigation bar part.
      child: BlocBuilder<BottomNavigationBarIndexCubit, int>(
        builder: (context, stateIndex) {
          return BottomNavigationBar(
            currentIndex: stateIndex,
            type: BottomNavigationBarType.fixed,
            items: const [
              BottomNavigationBarItem(
                icon: AppIcons.homeIcon,
                label: AppStrings.home,
              ),
              BottomNavigationBarItem(
                icon: AppIcons.storeIcon,
                label: AppStrings.shops,
              ),
            ],
            onTap: (index) {
              BlocProvider.of<BottomNavigationBarIndexCubit>(
                context,
              ).changeIndex(index);
            },
          );
        },
      ),
    );
  }
}
