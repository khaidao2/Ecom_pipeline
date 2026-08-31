# ===========================================
# Vault Configuration
# ===========================================

ui = true

# Dev mode settings
dev = true
dev_root_token_id = "dev-root-token"

# Storage backend (file for dev, consider consul/raft for prod)
storage "file" {
  path = "/vault/file"
}

# Listener
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1
}

# API address
api_addr = "http://0.0.0.0:8200"

# Log level
log_level = "info"
