locals {
  base        = "${var.project}-${var.environment}"                               # "docuwise-dev"
  suffix      = substr(md5(local.base), 0, 6)                                     # Stable 6-char hex (e.g., "a1b2c3")
  name_prefix = replace(local.base, "_", "-")                                     # Replace underscores with dashes for names
  tags        = merge({ project = var.project, env = var.environment }, var.tags) # Default+custom tags
}
