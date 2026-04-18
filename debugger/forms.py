from django import forms


class BugReportForm(forms.Form):
    error_log = forms.CharField(
        label="Traceback or failing test output",
        required=True,
        max_length=60000,
        widget=forms.Textarea(
            attrs={
                "class": "textarea textarea-error",
                "rows": 16,
                "placeholder": "Paste the Python/Django traceback, failing pytest output, or server error here...",
                "spellcheck": "false",
            }
        ),
    )
    code_context = forms.CharField(
        label="Code context",
        required=False,
        max_length=60000,
        widget=forms.Textarea(
            attrs={
                "class": "textarea textarea-code",
                "rows": 16,
                "placeholder": "Optional: paste the view, model, serializer, template, URL config, or test that may be involved...",
                "spellcheck": "false",
            }
        ),
    )
