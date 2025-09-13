resource "azurerm_eventhub_namespace" "ehns" {
  name                = "ehns-${local.name_prefix}" # ehns-docuwise-dev
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Basic" # Cheapest SKU
  capacity            = 1       # 1 TU
  tags                = local.tags
}

resource "azurerm_eventhub" "ingest" {
  name                = "docuwise-ingest" # Hub name your app/worker will use
  namespace_name      = azurerm_eventhub_namespace.ehns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2 # 2 partitions is fine to start
  message_retention   = 1 # Keep messages 1 days
}

resource "azurerm_eventhub_authorization_rule" "send" {
  name                = "send" # Shared Access Policy for API to send
  namespace_name      = azurerm_eventhub_namespace.ehns.name
  eventhub_name       = azurerm_eventhub.ingest.name
  resource_group_name = azurerm_resource_group.rg.name
  listen              = false
  send                = true
  manage              = false
}

resource "azurerm_eventhub_authorization_rule" "listen" {
  name                = "listen" # Shared Access Policy for worker to listen
  namespace_name      = azurerm_eventhub_namespace.ehns.name
  eventhub_name       = azurerm_eventhub.ingest.name
  resource_group_name = azurerm_resource_group.rg.name
  listen              = true
  send                = false
  manage              = false
}

output "eventhub_namespace" {
  value = azurerm_eventhub_namespace.ehns.name
} # Namespace name

output "eventhub_name" {
  value = azurerm_eventhub.ingest.name
} # Hub name

output "eventhub_conn_send" {
  value     = azurerm_eventhub_authorization_rule.send.primary_connection_string
  sensitive = true
} # SAS send

output "eventhub_conn_listen" {
  value     = azurerm_eventhub_authorization_rule.listen.primary_connection_string
  sensitive = true
} # SAS listen
