import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/tickets/presentation/providers/tickets_list_filter_provider.dart';
import 'package:ostrich_service/features/tickets/presentation/widgets/list_views/service_tickets_list_view_widget.dart';
import 'package:ostrich_service/features/tickets/presentation/widgets/ticket_filter_options_list_widget.dart';
import 'package:provider/provider.dart';

class HomePageWidget extends StatefulWidget {
  const HomePageWidget({super.key});

  @override
  State<HomePageWidget> createState() => _HomePageWidgetState();
}

class _HomePageWidgetState extends State<HomePageWidget>
    with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    _tabController = TabController(length: 2, vsync: this);
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) _tabController.animateTo(0);
      },
      child: Scaffold(
        appBar: AppBar(
          title: const Text(
            AppStrings.ostrichMobility,
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ),
        body: SafeArea(
          child: LayoutBuilder(
            builder: (context, cons) {
              final maxContainerWidth = cons.maxWidth;
              return Padding(
                padding: const EdgeInsets.only(
                  left: 15.0,
                  right: 15.0,
                  top: 15.0,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  spacing: 10.0,
                  children: [
                    SizedBox(
                      width: maxContainerWidth / 2,
                      child: const FittedBox(
                        child: Text(
                          AppStrings.serviceDashboard,
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                    TabBar(
                      controller: _tabController,
                      dividerColor: Colors.grey[300],
                      labelStyle: const TextStyle(
                        fontWeight: FontWeight.normal,
                      ),
                      unselectedLabelColor: AppColors.subtitleColor,
                      tabs: const [
                        Tab(text: AppStrings.active),
                        Tab(text: AppStrings.completed),
                      ],
                    ),
                    ChangeNotifierProvider(
                      create: (context) => TicketsListFilterProvider(),
                      child: const TicketFilterOptionsListWidget(),
                    ),
                    Expanded(
                      child: TabBarView(
                        controller: _tabController,
                        children: const [
                          ServiceTicketsListViewWidget(),
                          ServiceTicketsListViewWidget(),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}
