output "resource_group" { value = azurerm_resource_group.rg.name }                                # RG name
output "location" { value = var.location }                                                        # Region
output "container_apps_environment" { value = azurerm_container_app_environment.cae.name }        # CAE name
output "api_identity_client_id" { value = azurerm_user_assigned_identity.api_mi.client_id }       # API MI client id
output "worker_identity_client_id" { value = azurerm_user_assigned_identity.worker_mi.client_id } # Worker MI client id
