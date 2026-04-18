from django.shortcuts import render

from debugger.demo import DEMO_CODE_CONTEXT, DEMO_ERROR_LOG
from debugger.forms import BugReportForm
from debugger.services.debugger import analyze_bug


def index(request):
    analysis = None
    analysis_payload = None

    if request.method == "POST":
        form = BugReportForm(request.POST)
        if form.is_valid():
            analysis = analyze_bug(
                error_log=form.cleaned_data["error_log"],
                code_context=form.cleaned_data.get("code_context", ""),
            )
            analysis_payload = analysis.as_dict()
    else:
        form = BugReportForm()

    return render(
        request,
        "debugger/index.html",
        {
            "form": form,
            "analysis": analysis,
            "analysis_payload": analysis_payload,
            "demo_error_log": DEMO_ERROR_LOG,
            "demo_code_context": DEMO_CODE_CONTEXT,
        },
    )
