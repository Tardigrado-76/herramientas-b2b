"""
Data models for Aegis-Harness using Pydantic v2.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field

class TestCategory(str, Enum):
    __test__ = False
    FUNCTIONAL = "functional"
    ADVERSARIAL = "adversarial"
    EDGE_CASE = "edge_case"
    REGRESSION = "regression"

class ExpectedToolCall(BaseModel):
    __test__ = False
    server: str
    tool: str
    arguments: Optional[Dict[str, Any]] = None
    exact_match: bool = False

class TestCase(BaseModel):
    __test__ = False
    id: str
    category: TestCategory
    description: str
    input_query: str
    expected_server: Optional[str] = None
    expected_tool: Optional[str] = None
    expected_args: Optional[Dict[str, Any]] = None
    expected_tools: Optional[List[ExpectedToolCall]] = None
    prohibited_strings: List[str] = Field(default_factory=list)
    required_strings: List[str] = Field(default_factory=list)
    max_latency_ms: int = 3500
    security_tags: List[str] = Field(default_factory=list)

class AgentExecutionOutput(BaseModel):
    __test__ = False
    selected_server: Optional[str] = None
    selected_tool: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    final_response: str = ""
    latency_ms: float = 0.0
    tokens_used: Optional[int] = None
    raw_error: Optional[str] = None

class MetricEvaluation(BaseModel):
    __test__ = False
    name: str
    score: float = Field(ge=0.0, le=100.0)
    passed: bool
    weight: float = 1.0
    details: str = ""

class TestResult(BaseModel):
    __test__ = False
    test_case_id: str
    category: TestCategory
    passed: bool
    overall_score: float = Field(ge=0.0, le=100.0)
    metrics: List[MetricEvaluation] = Field(default_factory=list)
    execution_output: AgentExecutionOutput
    failure_reason: Optional[str] = None

class SuiteSummary(BaseModel):
    __test__ = False
    suite_name: str
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate_percent: float
    overall_score: float
    category_scores: Dict[str, float] = Field(default_factory=dict)
    average_latency_ms: float = 0.0
    quality_gate_passed: bool
    results: List[TestResult] = Field(default_factory=list)
