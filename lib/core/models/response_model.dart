import 'package:ostrich_service/core/entity/response_entity.dart';

class ResponseModel extends ResponseEntity {
  const ResponseModel({
    required super.data,
    required super.message,
    required super.statusCode,
    required super.success,
  });

  factory ResponseModel.fromJson(Map<dynamic, dynamic> json) {
    return ResponseModel(
      data: json['data'],
      message: json['message'],
      statusCode: json['status_ode'],
      success: json['success'],
    );
  }
}
