resource "azurerm_container_app" "qdrant" {
  name                         = "qdrant-${local.name_prefix}"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.cae.id
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.api_mi.id]
  }

  ingress {
    external_enabled = true
    target_port      = 6333
    transport        = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  # Pull the API key from Key Vault into a Container Apps secret
  secret {
    name                = "qdrant-api-key"
    key_vault_secret_id = azurerm_key_vault_secret.qdrant_api_key.versionless_id
    identity            = azurerm_user_assigned_identity.api_mi.id
  }

  template {
    # cheap autoscaling
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "qdrant"
      image  = "qdrant/qdrant:v1"
      cpu    = 1.0
      memory = "2Gi"

      # env from secret
      env {
        name        = "QDRANT__SERVICE__API_KEY"
        secret_name = "qdrant-api-key"
      }
      env {
        name  = "QDRANT__SERVICE__HTTP_PORT"
        value = "6333"
      }
      env {
        name  = "QDRANT__SERVICE__GRPC_PORT"
        value = "6334"
      }

      # mount Azure Files share at Qdrant's storage path
      volume_mounts {
        name = "qdrantdata"
        path = "/qdrant/storage"
      }
    }

    # reference the CAE storage registration (from storage-qdrant.tf)
    volume {
      name         = "qdrantdata"
      storage_type = "AzureFile" # SMB via Azure Files
      storage_name = azurerm_container_app_environment_storage.qdrant.name
    }
  }
}
