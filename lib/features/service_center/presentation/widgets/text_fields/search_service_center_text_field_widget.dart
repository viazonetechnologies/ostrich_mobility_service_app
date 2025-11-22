import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';

class SearchServiceCenterTextFieldWidget extends StatelessWidget {
  const SearchServiceCenterTextFieldWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return TextField(
      decoration: const InputDecoration(
        hintText: 'Search By PIN / Location',
        suffixIcon: AppIcons.searchIcon,
      ),
      onTapOutside: (_) => FocusManager.instance.primaryFocus?.unfocus(),
    );
  }
}
