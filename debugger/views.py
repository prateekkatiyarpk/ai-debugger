from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from debugger.demo import DEMO_CODE_CONTEXT, DEMO_ERROR_LOG
from debugger.forms import BugReportForm
from debugger.services.debugger import analyze_bug
from debugger.services.repo_ingest import (
    build_repository_context_from_workspace,
    prepare_repository_workspace,
)
from debugger.services.repro_runner import capture_repro_command
from debugger.services.traceback_parse import fallback_evidence, parse_failure_clues


def index(request):
    analysis = None
    analysis_payload = None
    repo_context = None
    command_capture = None
    command_output_used_for_analysis = False
    failure_source_label = ""

    if request.method == "POST":
        form = BugReportForm(request.POST, request.FILES)
        if form.is_valid():
            pasted_error_log = form.cleaned_data.get("error_log", "").strip()
            repro_command = form.cleaned_data.get("repro_command", "").strip()
            manual_context = form.cleaned_data.get("code_context", "")

            with prepare_repository_workspace(
                github_url=form.cleaned_data.get("github_url", ""),
                uploaded_zip=form.cleaned_data.get("repo_zip"),
            ) as workspace:
                if repro_command and workspace.has_repo_input:
                    command_capture = capture_repro_command(workspace.execution_root, repro_command)
                elif repro_command and not pasted_error_log:
                    command_capture = capture_repro_command(None, repro_command)

                active_error_log = pasted_error_log
                if active_error_log:
                    failure_source_label = "Pasted log"
                elif command_capture and command_capture.has_output:
                    active_error_log = command_capture.output
                    failure_source_label = "Captured from command"
                    command_output_used_for_analysis = True

                if active_error_log:
                    repo_context = build_repository_context_from_workspace(
                        workspace,
                        error_log=active_error_log,
                        manual_context=manual_context,
                    )
                    analysis = analyze_bug(
                        error_log=active_error_log,
                        code_context=repo_context.combined_context,
                        detected_language=repo_context.detected_language,
                        detected_framework=repo_context.detected_framework,
                        fallback_evidence=fallback_evidence(
                            parse_failure_clues(active_error_log),
                            repo_context.inspected_files,
                            repo_context.detected_language,
                            repo_context.detected_framework,
                        ),
                    )
                    analysis_payload = analysis.as_dict()
                else:
                    if workspace.errors:
                        for error in workspace.errors:
                            form.add_error(None, error)
                    if command_capture and command_capture.error_message:
                        form.add_error(None, command_capture.error_message)
                    elif repro_command:
                        form.add_error(
                            None,
                            "The repro command did not produce usable output. Paste the failure log instead or try a command that reproduces the failure.",
                        )
    else:
        form = BugReportForm()

    return render(
        request,
        "debugger/index.html",
        {
            "form": form,
            "analysis": analysis,
            "analysis_payload": analysis_payload,
            "repo_context": repo_context,
            "command_capture": command_capture,
            "command_output_used_for_analysis": command_output_used_for_analysis,
            "failure_source_label": failure_source_label,
            "demo_error_log": DEMO_ERROR_LOG,
            "demo_code_context": DEMO_CODE_CONTEXT,
        },
    )


def intentional_failure(request):
    demo_post = _load_broken_demo_post()
    detail_url = _build_demo_detail_url(demo_post)
    return HttpResponse(detail_url)


def demo_detail(request, pk):
    return HttpResponse(f"Demo detail {pk}")


def _load_broken_demo_post():
    return {"title": "Intentional prod failure"}


def _build_demo_detail_url(post):
    return reverse("debugger:demo-detail", kwargs={"pk": post.get("pk", "")})
