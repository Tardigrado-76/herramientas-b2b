import pytest
from aegis.models import SuiteSummary, TestResult, TestCategory, AgentExecutionOutput
from aegis.report import ReportGenerator

def test_report_generator_markdown_and_pdf(tmp_path):
    gen = ReportGenerator(output_dir=str(tmp_path))

    r1 = TestResult(
        test_case_id="F-01",
        category=TestCategory.FUNCTIONAL,
        passed=True,
        overall_score=95.0,
        execution_output=AgentExecutionOutput(latency_ms=150.0)
    )
    summary = SuiteSummary(
        suite_name="Integration Battery",
        timestamp="2026-10-23T12:00:00Z",
        total_tests=1,
        passed_tests=1,
        failed_tests=0,
        pass_rate_percent=100.0,
        overall_score=95.0,
        category_scores={"functional": 95.0},
        average_latency_ms=150.0,
        quality_gate_passed=True,
        results=[r1]
    )

    # 1. Test Markdown generation
    md_file = gen.generate_markdown(summary)
    assert md_file.exists()
    content = md_file.read_text(encoding="utf-8")
    assert "Aegis-Harness Evaluation Report" in content
    assert "Integration Battery" in content
    assert "PASSED" in content

    # 2. Test PDF generation
    pdf_file = gen.generate_pdf(summary)
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 1000
