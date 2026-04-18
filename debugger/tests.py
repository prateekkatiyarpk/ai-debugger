import json

from django.test import SimpleTestCase

from debugger.services.debugger import analysis_from_dict, fallback_analysis, parse_model_response


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

    def test_analysis_validation_rejects_missing_required_fields(self):
        with self.assertRaises(ValueError):
            analysis_from_dict({"issue_summary": "Too small"})

    def test_fallback_analysis_is_renderable(self):
        analysis = fallback_analysis("not json", "Bad JSON")

        self.assertFalse(analysis.parsed)
        self.assertEqual(analysis.confidence, 0.0)
        self.assertIn("not json", analysis.raw_response)
