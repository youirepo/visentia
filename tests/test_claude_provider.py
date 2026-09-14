"""The Anthropic provider (issue #27's model decision, finally built).

These tests pin the *request shape*, because that is where this provider can be wrong in
ways that only show up as a 400 from the API: `temperature` must not be sent, structured
output must go in `output_config.format` as real JSON Schema, and the reply must be read
past the thinking block.
"""

from __future__ import annotations

import anthropic
import pytest

from visentia.llm import CHAT_MODEL, CODEGEN_MODEL, Claude
from visentia.llm.base import CLASSIFICATION_TEMPERATURE, LLMError, MissingApiKeyError
from visentia.llm.claude import HIGH_EFFORT, LOW_EFFORT, to_json_schema


class _Block:
    def __init__(self, type_: str, text: str = "") -> None:
        self.type = type_
        self.text = text


class _Response:
    def __init__(self, blocks, stop_reason="end_turn", stop_details=None) -> None:
        self.content = blocks
        self.stop_reason = stop_reason
        self.stop_details = stop_details


class _FakeMessages:
    def __init__(self, response=None, raises=None) -> None:
        self._response = response or _Response([_Block("text", "ok")])
        self._raises = raises
        self.last_request: dict | None = None

    def create(self, **kwargs):
        self.last_request = kwargs
        if self._raises is not None:
            raise self._raises
        return self._response


def _provider(monkeypatch, response=None, raises=None) -> tuple[Claude, _FakeMessages]:
    fake = _FakeMessages(response, raises)

    class _FakeClient:
        def __init__(self, **kwargs) -> None:
            self.messages = fake

    monkeypatch.setattr(anthropic, "Anthropic", _FakeClient)
    return Claude(model=CHAT_MODEL, effort=LOW_EFFORT, api_key="test-key"), fake


class TestRequestShape:
    def test_temperature_is_never_sent(self, monkeypatch):
        """Opus 5 and Sonnet 5 reject `temperature` with a 400.

        The interface still takes one because every call site passes it, so the risk is
        passing it through to the API by accident.
        """

        provider, fake = _provider(monkeypatch)
        provider.complete(
            [{"role": "user", "content": "hi"}], temperature=CLASSIFICATION_TEMPERATURE
        )
        assert "temperature" not in fake.last_request

    def test_system_prompt_is_a_top_level_parameter(self, monkeypatch):
        provider, fake = _provider(monkeypatch)
        provider.complete([{"role": "user", "content": "hi"}], system="be terse")

        assert fake.last_request["system"] == "be terse"
        assert [m["role"] for m in fake.last_request["messages"]] == ["user"]

    def test_system_is_omitted_when_absent(self, monkeypatch):
        provider, fake = _provider(monkeypatch)
        provider.complete([{"role": "user", "content": "hi"}])
        assert "system" not in fake.last_request

    def test_response_schema_becomes_output_config_format(self, monkeypatch):
        provider, fake = _provider(monkeypatch)
        provider.complete(
            [{"role": "user", "content": "hi"}],
            response_schema={
                "type": "OBJECT",
                "properties": {"kind": {"type": "STRING"}},
                "required": ["kind"],
            },
        )

        output_config = fake.last_request["output_config"]
        assert output_config["format"]["type"] == "json_schema"
        assert output_config["format"]["schema"]["type"] == "object"
        assert "response_schema" not in fake.last_request

    def test_effort_is_sent_and_reflects_the_role(self, monkeypatch):
        provider, fake = _provider(monkeypatch)
        provider.complete([{"role": "user", "content": "hi"}])
        assert fake.last_request["output_config"]["effort"] == LOW_EFFORT

    def test_format_is_absent_when_no_schema_is_requested(self, monkeypatch):
        provider, fake = _provider(monkeypatch)
        provider.complete([{"role": "user", "content": "hi"}])
        assert "format" not in fake.last_request["output_config"]


class TestResponseHandling:
    def test_thinking_blocks_are_skipped(self, monkeypatch):
        """Thinking is adaptive by default, so content routinely opens with a thinking block."""

        response = _Response([_Block("thinking", "hmm"), _Block("text", '{"a": 1}')])
        provider, _ = _provider(monkeypatch, response)
        assert provider.complete([{"role": "user", "content": "hi"}]) == '{"a": 1}'

    def test_a_refusal_is_an_llm_error(self, monkeypatch):
        class _Details:
            category = "cyber"

        response = _Response([], stop_reason="refusal", stop_details=_Details())
        provider, _ = _provider(monkeypatch, response)

        with pytest.raises(LLMError, match="declined"):
            provider.complete([{"role": "user", "content": "hi"}])

    def test_an_empty_reply_is_an_llm_error(self, monkeypatch):
        provider, _ = _provider(monkeypatch, _Response([_Block("thinking", "hmm")]))
        with pytest.raises(LLMError):
            provider.complete([{"role": "user", "content": "hi"}])


class TestErrorMapping:
    def test_authentication_failure_asks_for_the_key(self, monkeypatch):
        error = anthropic.AuthenticationError(
            "bad key", response=_FakeHttpResponse(401), body=None
        )
        provider, _ = _provider(monkeypatch, raises=error)

        with pytest.raises(MissingApiKeyError, match="ANTHROPIC_API_KEY"):
            provider.complete([{"role": "user", "content": "hi"}])

    def test_connection_failure_is_an_llm_error(self, monkeypatch):
        error = anthropic.APIConnectionError(request=None)
        provider, _ = _provider(monkeypatch, raises=error)

        with pytest.raises(LLMError, match="reach"):
            provider.complete([{"role": "user", "content": "hi"}])


class _FakeHttpResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        self.headers = {}
        self.request = None


class TestSchemaTranslation:
    def test_gemini_type_names_become_json_schema_types(self):
        translated = to_json_schema(
            {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "count": {"type": "INTEGER"},
                    "size": {"type": "NUMBER"},
                    "flag": {"type": "BOOLEAN"},
                },
                "required": ["name"],
            }
        )

        assert translated["type"] == "object"
        kinds = {k: v["type"] for k, v in translated["properties"].items()}
        assert kinds == {
            "name": "string",
            "count": "integer",
            "size": "number",
            "flag": "boolean",
        }

    def test_nested_arrays_of_objects_are_translated(self):
        """The Stage 6 `beats` list is an array of objects — the deepest shape in use."""

        translated = to_json_schema(
            {
                "type": "OBJECT",
                "properties": {
                    "beats": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {"kind": {"type": "STRING"}},
                            "required": ["kind"],
                        },
                    }
                },
                "required": ["beats"],
            }
        )

        beats = translated["properties"]["beats"]
        assert beats["type"] == "array"
        assert beats["items"]["type"] == "object"
        assert beats["items"]["properties"]["kind"]["type"] == "string"

    def test_objects_reject_extra_properties(self):
        """A model inventing a parameter should fail at the boundary, not be dropped."""

        translated = to_json_schema({"type": "OBJECT", "properties": {"a": {"type": "STRING"}}})
        assert translated["additionalProperties"] is False

    def test_a_declared_required_list_is_preserved(self):
        """Optional params (y_min, y_max) must stay optional."""

        translated = to_json_schema(
            {
                "type": "OBJECT",
                "properties": {"a": {"type": "STRING"}, "b": {"type": "STRING"}},
                "required": ["a"],
            }
        )
        assert translated["required"] == ["a"]

    def test_every_registered_template_schema_translates(self):
        from visentia.templates import TemplateLibrary

        for spec in TemplateLibrary().list_templates():
            translated = to_json_schema(spec.param_schema)
            assert translated["type"] == "object"
            assert translated["additionalProperties"] is False


def test_the_two_roles_use_the_models_decided_in_27():
    assert CHAT_MODEL == "claude-sonnet-5"
    assert CODEGEN_MODEL == "claude-opus-5"


def test_orchestrator_splits_the_roles():
    """Classification runs on the cheap model; freeform codegen on the capable one."""

    from visentia.orchestrator import RepairOrchestrator

    orchestrator = RepairOrchestrator()
    assert orchestrator.provider.model == CHAT_MODEL
    assert orchestrator.codegen_provider.model == CODEGEN_MODEL
    assert orchestrator.provider.effort == LOW_EFFORT
    assert orchestrator.codegen_provider.effort == HIGH_EFFORT
