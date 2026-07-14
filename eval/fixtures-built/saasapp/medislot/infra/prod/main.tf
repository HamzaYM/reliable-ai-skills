module "deploy_role" {
  source             = "../modules/deploy_role"
  oidc_sub_condition = "repo:acme-health/medislot:environment:staging"
}

resource "synthetic_app_service" "api" {
  name        = "medislot-prod"
  environment = [for k, v in var.app_settings : "${k}=${v}"]
}

variable "app_settings" {
  type = map(string)
}
