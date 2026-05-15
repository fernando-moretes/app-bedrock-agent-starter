"""Agent loop using the Amazon Bedrock Converse API.

Small, readable state machine. See ARCHITECTURE.md for the design notes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from agent.config import Settings
from agent.memory import InMemoryMemory, Memory
from agent.observability import emit_emf, log_turn
from agent.tools import dispatch, tool_specs


@dataclass
class AgentResult:
    """Outcome of one ``Agent.run`` call."""

    output_text: str
    session_id: str
    turns: int
    tool_calls: list[str] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0


class Agent:
    """Bedrock Converse-based agent with tool use.

    Inject a custom ``bedrock_client`` for tests; otherwise the agent builds one
    from boto3 using the settings' region.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        memory: Memory | None = None,
        bedrock_client: Any | None = None,
    ) -> None:
        self.settings = settings or Settings.from_env()
        self.memory = memory or InMemoryMemory()
        if bedrock_client is not None:
            self._bedrock = bedrock_client
        else:
            import boto3

            self._bedrock = boto3.client("bedrock-runtime", region_name=self.settings.region)

    def run(self, user_message: str, session_id: str | None = None) -> AgentResult:
        """Run one turn (which may include multiple tool-call rounds)."""
        session_id = session_id or f"s_{uuid.uuid4().hex[:12]}"
        start = time.perf_counter()

        history = self.memory.read(session_id)
        history.append({"role": "user", "content": [{"text": user_message}]})

        tool_call_names: list[str] = []
        total_input = 0
        total_output = 0
        round_idx = 0
        final_text = ""

        while round_idx < self.settings.max_tool_rounds:
            response = self._bedrock.converse(
                modelId=self.settings.model_id,
                messages=history,
                system=[{"text": self.settings.system_prompt}],
                inferenceConfig={
                    "maxTokens": self.settings.max_tokens,
                    "temperature": self.settings.temperature,
                },
                toolConfig={"tools": tool_specs()},
            )

            if "stopReason" not in response:
                raise KeyError("Bedrock response missing required field: stopReason")

            usage = response.get("usage", {})
            total_input += int(usage.get("inputTokens", 0) or 0)
            total_output += int(usage.get("outputTokens", 0) or 0)

            stop_reason = response.get("stopReason")
            assistant_msg = response["output"]["message"]
            history.append(assistant_msg)

            if stop_reason == "tool_use":
                tool_uses = [b for b in assistant_msg["content"] if "toolUse" in b]
                tool_results: list[dict[str, Any]] = []
                for block in tool_uses:
                    tu = block["toolUse"]
                    name = tu["name"]
                    args = tu.get("input", {})
                    tool_call_names.append(name)
                    try:
                        result = dispatch(name, args)
                        tool_results.append(
                            {
                                "toolResult": {
                                    "toolUseId": tu["toolUseId"],
                                    "content": [{"text": str(result)}],
                                }
                            }
                        )
                    except Exception as e:  # noqa: BLE001 — surface failure to the model
                        emit_emf("BedrockAgent", {"ToolErrors": (1, "Count")}, {"tool": name})
                        tool_results.append(
                            {
                                "toolResult": {
                                    "toolUseId": tu["toolUseId"],
                                    "content": [{"text": f"ERROR: {e}"}],
                                    "status": "error",
                                }
                            }
                        )
                history.append({"role": "user", "content": tool_results})
                round_idx += 1
                continue

            # end_turn (or any other terminal stop reason)
            final_text = _extract_text(assistant_msg)
            break
        else:
            final_text = (
                "[agent] Reached max tool-call rounds without a final answer. "
                "Increase AGENT_MAX_TOOL_ROUNDS or simplify the prompt."
            )

        duration_ms = int((time.perf_counter() - start) * 1000)

        self.memory.append(session_id, history[-(round_idx * 2 + 2) :])

        result = AgentResult(
            output_text=final_text,
            session_id=session_id,
            turns=round_idx + 1,
            tool_calls=tool_call_names,
            input_tokens=total_input,
            output_tokens=total_output,
            duration_ms=duration_ms,
        )

        log_turn(
            session_id=session_id,
            turn=result.turns,
            model_id=self.settings.model_id,
            input_tokens=total_input,
            output_tokens=total_output,
            tool_calls=tool_call_names,
            duration_ms=duration_ms,
        )
        emit_emf(
            "BedrockAgent",
            {
                "Turns": (result.turns, "Count"),
                "InputTokens": (total_input, "Count"),
                "OutputTokens": (total_output, "Count"),
                "Duration": (duration_ms, "Milliseconds"),
            },
            {"model_id": self.settings.model_id},
        )

        return result


def _extract_text(assistant_msg: dict[str, Any]) -> str:
    return "".join(b.get("text", "") for b in assistant_msg.get("content", []) if "text" in b)
