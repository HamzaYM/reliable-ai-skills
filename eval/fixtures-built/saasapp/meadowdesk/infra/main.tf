resource "synthetic_security_group" "api" {
  name    = "meadowdesk-api"
  ingress = ["0.0.0.0/0"]  # F-10: over-permissive
}
