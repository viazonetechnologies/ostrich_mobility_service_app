import 'package:equatable/equatable.dart';

class ResponseEntity extends Equatable {
  final dynamic data;
  final String? message;
  final int? statusCode;
  final bool? success;

  const ResponseEntity({
    required this.data,
    required this.message,
    required this.statusCode,
    required this.success,
  });

  @override
  List<Object?> get props => [data, message, statusCode, success];
}
