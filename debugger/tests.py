import json
import os
from unittest.mock import patch

from django.test import Client, SimpleTestCase

from debugger.demo import DEMO_CODE_CONTEXT, DEMO_ERROR_LOG
from debugger.services.debugger import (
    DEBUGGER_RESPONSE_FORMAT,
    analysis_from_dict,
    fallback_analysis,
    parse_model_response,
)


class DebuggerServiceTests(SimpleTestCase):
    def test_parse_model_response_returns_analysis(self):
        raw = json.dumps(
            {
                "issue_summary": "Template reverses a URL with a missing pk.",
                "root_cause": "The context does not include a primary key.",
                "suspected_location": {"file": "posts/views.py", "function": "post_list"},
                "suggested_fix": "Include id in the values() query.",
                "patch_diff": "",
                "confidence": 0.82,
                "regression_test": "Render the list page with one Post and assert it links to detail.",
            }
        )

        analysis = parse_model_response(raw)

        self.assertTrue(analysis.parsed)
        self.assertEqual(analysis.confidence_percent, 82)
        self.assertEqual(analysis.suspected_location.file, "posts/views.py")
        self.assertEqual(
            analysis.as_dict()["suspected_location"]["function"],
            "post_list",
        )
        self.assertEqual(analysis.confidence_label, "High confidence")
        self.assertEqual(len(analysis.timeline_steps), 5)
        self.assertIn("Traceback parsed", analysis.timeline_steps[0]["title"])
        self.assertTrue(analysis.diagnosis_reasons)

    def test_analysis_validation_rejects_missing_required_fields(self):
        with self.assertRaises(ValueError):
            analysis_from_dict({"issue_summary": "Too small"})

    def test_fallback_analysis_is_renderable(self):
        analysis = fallback_analysis("not json", "Bad JSON")

        self.assertFalse(analysis.parsed)
        self.assertEqual(analysis.confidence, 0.0)
        self.assertIn("not json", analysis.raw_response)

    def test_response_format_requires_expected_product_fields(self):
        schema = DEBUGGER_RESPONSE_FORMAT["json_schema"]["schema"]

        self.assertEqual(DEBUGGER_RESPONSE_FORMAT["type"], "json_schema")
        self.assertTrue(DEBUGGER_RESPONSE_FORMAT["json_schema"]["strict"])
        self.assertIn("patch_diff", schema["required"])
        self.assertFalse(schema["additionalProperties"])


class DebuggerViewTests(SimpleTestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_demo_post_renders_structured_result_without_api_key(self):
        response = Client().post(
            "/",
            {
                "error_log": DEMO_ERROR_LOG,
                "code_context": DEMO_CODE_CONTEXT,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Diagnosis Complete")
        self.assertContains(response, "Analysis Timeline")
        self.assertContains(response, "Why this diagnosis?")
        self.assertContains(response, "Copy JSON")
        self.assertContains(response, "The post list template tries to reverse")
