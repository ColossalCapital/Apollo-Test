#!/usr/bin/env python3
"""Apollo AI Charm - Universal AI assistant"""

import logging
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, WaitingStatus, MaintenanceStatus
from ops.pebble import Layer

logger = logging.getLogger(__name__)


class ApolloAICharm(CharmBase):
    """Charm for Apollo AI assistant service."""

    def __init__(self, *args):
        super().__init__(*args)
        
        self.framework.observe(self.on.apollo_pebble_ready, self._on_apollo_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.ai_assistant_relation_joined, self._on_ai_assistant_relation_joined)

    def _on_apollo_pebble_ready(self, event):
        logger.info("Apollo container ready")
        self._configure_apollo(event)

    def _on_config_changed(self, event):
        self._configure_apollo(event)

    def _on_ai_assistant_relation_joined(self, event):
        """Provide Apollo AI endpoint to apps."""
        host = self.model.get_binding("ai-assistant").network.bind_address
        event.relation.data[self.app].update({
            "api-url": f"http://{host}:{self.config['port']}",
            "websocket-url": f"ws://{host}:{self.config['port']}/ws",
        })

    def _configure_apollo(self, event):
        container = self.unit.get_container("apollo")
        if not container.can_connect():
            self.unit.status = WaitingStatus("Waiting for Apollo")
            event.defer()
            return

        self.unit.status = MaintenanceStatus("Configuring Apollo AI")

        # Get service connections
        ollama_config = self._get_ollama_config()
        db_config = self._get_database_config()
        redis_config = self._get_redis_config()
        hermes_config = self._get_hermes_config()

        env_vars = {
            "PORT": str(self.config["port"]),
            "ENABLE_OLLAMA": str(self.config.get("enable-ollama", True)),
            "ENABLE_OPENAI": str(self.config.get("enable-openai", False)),
            "DEFAULT_MODEL": self.config.get("default-model", "mistral"),
            "ENABLE_LEARNING": str(self.config.get("enable-learning", True)),
            "ENABLE_CROSS_SERVICE": str(self.config.get("enable-cross-service", True)),
        }

        if ollama_config:
            env_vars["OLLAMA_URL"] = ollama_config.get("url", "http://ollama:11434")

        if db_config:
            env_vars["DATABASE_URL"] = f"postgresql://{db_config.get('username')}:{db_config.get('password')}@{db_config.get('host')}:{db_config.get('port')}/apollo"

        if redis_config:
            env_vars["REDIS_URL"] = f"redis://{redis_config.get('host')}:6379"

        if hermes_config:
            env_vars["HERMES_API_URL"] = hermes_config.get("api-url", "http://hermes:8081")

        layer = Layer({
            "summary": "Apollo AI assistant",
            "services": {
                "apollo": {
                    "override": "replace",
                    "command": "/app/apollo-ai",  # Rust/Axum binary
                    "startup": "enabled",
                    "environment": env_vars,
                }
            },
            "checks": {
                "apollo-ready": {
                    "override": "replace",
                    "level": "ready",
                    "http": {"url": "http://localhost:8082/health"},
                },
            },
        })

        container.add_layer("apollo", layer, combine=True)
        container.replan()

        self.unit.status = ActiveStatus("Apollo AI running")

    def _get_ollama_config(self):
        relation = self.model.get_relation("llm")
        return relation.data.get(relation.app) if relation else None

    def _get_database_config(self):
        relation = self.model.get_relation("database")
        return relation.data.get(relation.app) if relation else None

    def _get_redis_config(self):
        relation = self.model.get_relation("cache")
        return relation.data.get(relation.app) if relation else None

    def _get_hermes_config(self):
        relation = self.model.get_relation("hermes")
        return relation.data.get(relation.app) if relation else None


if __name__ == "__main__":
    main(ApolloAICharm)

