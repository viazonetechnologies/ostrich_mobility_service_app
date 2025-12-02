import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/cubits/bottom_navigation_bar_index_cubit.dart';
import 'package:ostrich_service/core/widgets/bottom_navigation_bar_widget.dart';
import 'package:ostrich_service/pages/home_page_widget.dart';
import 'package:ostrich_service/pages/shops_page_widget.dart';
import 'package:ostrich_service/utils/local_storage/token_manager.dart';

class MainPageWidget extends StatefulWidget {
  const MainPageWidget({super.key});

  @override
  State<MainPageWidget> createState() => _MainPageWidgetState();
}

class _MainPageWidgetState extends State<MainPageWidget> {
  @override
  void initState() {
    super.initState();
    _initialSetup();
  }

  Future<void> _initialSetup() async {
    await GetIt.I<TokenManager>().getUserTokens();
  }

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (context) => BottomNavigationBarIndexCubit()),
      ],
      child: Scaffold(
        body: BlocConsumer<BottomNavigationBarIndexCubit, int>(
          listener: (context, state) {},
          builder: (context, state) {
            return IndexedStack(
              index: state,
              children: [const HomePageWidget(), const ShopsPageWidget()],
            );
          },
        ),
        bottomNavigationBar: const Material(
          color: Colors.white,
          child: BottomNavigationBarWidget(),
        ),
      ),
    );
  }
}
