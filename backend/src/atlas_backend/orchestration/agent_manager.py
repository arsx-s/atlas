"""Agent coordination and execution."""

from __future__ import annotations

from typing import Any


class AgentManager:
    """Coordinates execution of specialized agents."""

    def __init__(self) -> None:
        self._agents: dict[str, Any] = {}
        self._agent_states: dict[str, str] = {}

    def register_agent(self, agent_id: str, agent: Any) -> None:
        """Register an agent with the manager."""
        self._agents[agent_id] = agent
        self._agent_states[agent_id] = "idle"

    def get_agent(self, agent_id: str) -> Any | None:
        """Get a registered agent."""
        return self._agents.get(agent_id)

    def mark_agent_busy(self, agent_id: str) -> bool:
        """Mark an agent as busy."""
        if agent_id not in self._agents:
            return False
        self._agent_states[agent_id] = "busy"
        return True

    def mark_agent_idle(self, agent_id: str) -> bool:
        """Mark an agent as idle."""
        if agent_id not in self._agents:
            return False
        self._agent_states[agent_id] = "idle"
        return True

    def get_available_agents(self) -> list[str]:
        """Get list of available agents."""
        return [agent_id for agent_id, state in self._agent_states.items() if state == "idle"]

    def get_agent_state(self, agent_id: str) -> str | None:
        """Get the state of an agent."""
        return self._agent_states.get(agent_id)

    async def execute_task(self, agent_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """Execute a task with an agent."""
        agent = self._agents.get(agent_id)
        if agent is None:
            return {"success": False, "error": "Agent not found"}

        self.mark_agent_busy(agent_id)
        try:
            result = await agent.execute(task_data)
            return result
        finally:
            self.mark_agent_idle(agent_id)

    def get_agent_list(self) -> list[dict[str, str]]:
        """Get list of all agents and their states."""
        return [
            {"agent_id": agent_id, "state": state}
            for agent_id, state in self._agent_states.items()
        ]
