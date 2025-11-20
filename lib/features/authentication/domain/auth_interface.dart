abstract interface class AuthInterface {
  Future<String> loginUser(String identifier, String password);
  Future<String> logoutUser();
}
