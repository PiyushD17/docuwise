resource "azurerm_cognitive_account" "aoai" {
  name                = "aoai${local.suffix}" # e.g., aoai26f3d6
  location            = var.location          # keep same region if supported
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "OpenAI" # this makes it an Azure OpenAI resource
  sku_name            = "S0"
  # Nice to have: custom subdomain for cleaner endpoint
  custom_subdomain_name = "aoai-${local.name_prefix}" # e.g., aoai-docuwise-dev
  tags                  = local.tags
}

output "aoai_endpoint" {
  value = azurerm_cognitive_account.aoai.endpoint # Base endpoint URL
}

output "aoai_key" {
  value     = azurerm_cognitive_account.aoai.primary_access_key
  sensitive = true
}
