variable "oidc_sub_condition" {
  description = "GitHub OIDC sub claim that may assume the deploy role"
  type        = string
}

resource "synthetic_iam_role" "deploy" {
  name = "medislot-deploy"
  assume_role_condition = {
    "token.actions.example.com:sub" = var.oidc_sub_condition
  }
}
