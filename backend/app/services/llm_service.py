"""LLM service for agent-based analysis using OpenAI."""

from typing import Optional, Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.output_parsers import PydanticOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
from app.config import settings
import logging
import json

logger = logging.getLogger(__name__)


class RootCauseAnalysis(BaseModel):
    """Structured root cause analysis."""
    category: str = Field(..., description="Failure category")
    root_cause: str = Field(..., description="Core root cause explanation")
    affected_components: List[str] = Field(..., description="Affected system components")
    causal_chain: List[str] = Field(..., description="Chain of causality")
    confidence: int = Field(..., description="Confidence level 0-100")
    security_implications: Optional[str] = Field(None, description="Security concerns if any")


class ProposedCodeFix(BaseModel):
    """Structured code fix proposal."""
    file_path: str = Field(..., description="File to modify")
    function_name: str = Field(..., description="Function to change")
    problem_description: str = Field(..., description="What's wrong")
    fix_description: str = Field(..., description="How to fix it")
    code_before: str = Field(..., description="Original code snippet")
    code_after: str = Field(..., description="Fixed code snippet")
    risk_level: str = Field(..., description="low, medium, or high")
    regression_tests: List[str] = Field(..., description="Regression test cases")


class LLMService:
    """Service for leveraging LLMs in debugging workflow."""

    def __init__(self):
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured. LLM features disabled.")
            self.llm = None
        else:
            self.llm = ChatOpenAI(
                model_name=settings.model_name,
                temperature=settings.model_temperature,
                max_tokens=settings.max_tokens,
                openai_api_key=settings.openai_api_key,
            )

    async def analyze_failure(self, failure: Dict[str, Any]) -> RootCauseAnalysis:
        """
        Use LLM to perform root cause analysis on a failure.
        
        Args:
            failure: Test failure data with error, traceback, etc.
            
        Returns:
            Structured root cause analysis
        """
        if not self.llm:
            logger.warning("LLM not configured, returning mock analysis")
            return self._mock_analysis()

        try:
            error = failure.get("error", "")
            traceback = failure.get("traceback", "")
            test_name = failure.get("test_name", "")

            prompt = ChatPromptTemplate.from_template("""
You are an expert software debugging engineer. Analyze this test failure and provide a detailed root cause analysis.

Test: {test_name}
Error: {error}
Traceback:
{traceback}

Provide a JSON response with:
- category: the failure type (LOGIC_ERROR, TYPE_ERROR, RUNTIME_ERROR, etc.)
- root_cause: the actual root cause (not the symptom)
- affected_components: list of affected components
- causal_chain: step-by-step chain of how this failure occurred
- confidence: your confidence in this analysis (0-100)
- security_implications: any security concerns (null if none)

Focus on finding the REAL root cause, not just the error message.
""")

            parser = PydanticOutputParser(pydantic_object=RootCauseAnalysis)
            chain = prompt | self.llm | parser

            analysis = await chain.ainvoke({
                "test_name": test_name,
                "error": error,
                "traceback": traceback,
            })

            logger.info(f"LLM analysis for {test_name}: confidence={analysis.confidence}")
            return analysis

        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            return self._mock_analysis()

    async def propose_fix(self, analysis: RootCauseAnalysis, source_code: Optional[str] = None) -> ProposedCodeFix:
        """
        Use LLM to propose a code fix based on root cause analysis.
        
        Args:
            analysis: Root cause analysis
            source_code: Relevant source code snippet
            
        Returns:
            Proposed code fix
        """
        if not self.llm:
            logger.warning("LLM not configured, returning mock fix")
            return self._mock_fix()

        try:
            prompt = ChatPromptTemplate.from_template("""
You are an expert software developer. Based on this root cause analysis, propose a minimal, safe code fix.

Root Cause: {root_cause}
Affected Components: {components}
Confidence: {confidence}%

{source_code_section}

Propose a fix that:
1. Addresses the root cause
2. Is minimal (smallest possible change)
3. Maintains existing behavior
4. Includes appropriate error handling
5. Has no security regressions

Provide a JSON response with:
- file_path: file to modify
- function_name: function to change
- problem_description: what's wrong
- fix_description: how to fix it
- code_before: original code snippet
- code_after: fixed code snippet
- risk_level: low/medium/high
- regression_tests: list of test cases to verify the fix

Be specific with code examples.
""")

            source_code_section = f"Current code:\n{source_code}" if source_code else ""

            parser = PydanticOutputParser(pydantic_object=ProposedCodeFix)
            chain = prompt | self.llm | parser

            fix = await chain.ainvoke({
                "root_cause": analysis.root_cause,
                "components": ", ".join(analysis.affected_components),
                "confidence": analysis.confidence,
                "source_code_section": source_code_section,
            })

            logger.info(f"LLM proposed fix for {fix.file_path}: risk={fix.risk_level}")
            return fix

        except Exception as e:
            logger.error(f"LLM fix proposal failed: {str(e)}")
            return self._mock_fix()

    async def generate_security_analysis(self, code: str, error: str) -> Dict[str, Any]:
        """
        Use LLM to analyze security implications.
        
        Args:
            code: Code snippet
            error: Error message
            
        Returns:
            Security analysis results
        """
        if not self.llm:
            return {"vulnerabilities": [], "risk_level": "low"}

        try:
            prompt = ChatPromptTemplate.from_template("""
You are a security expert. Analyze this code for vulnerabilities and security risks.

Error Context: {error}

Code:
{code}

Identify:
1. SQL injection risks
2. Command injection risks
3. Authentication/authorization issues
4. Data exposure risks
5. Insecure deserialization
6. Any other security concerns

Respond with JSON:
{{
    "vulnerabilities": [list of issues found],
    "risk_level": "low/medium/high/critical",
    "recommendations": [list of security fixes]
}}
""")

            chain = prompt | self.llm | JsonOutputParser()

            analysis = await chain.ainvoke({
                "code": code,
                "error": error,
            })

            return analysis

        except Exception as e:
            logger.error(f"LLM security analysis failed: {str(e)}")
            return {"vulnerabilities": [], "risk_level": "low"}

    def _mock_analysis(self) -> RootCauseAnalysis:
        """Return mock analysis when LLM is not available."""
        return RootCauseAnalysis(
            category="UNKNOWN",
            root_cause="Manual investigation required",
            affected_components=["unknown"],
            causal_chain=["Unable to determine without LLM"],
            confidence=0,
            security_implications=None,
        )

    def _mock_fix(self) -> ProposedCodeFix:
        """Return mock fix when LLM is not available."""
        return ProposedCodeFix(
            file_path="unknown",
            function_name="unknown",
            problem_description="Unable to determine without LLM",
            fix_description="Manual fix required",
            code_before="",
            code_after="",
            risk_level="high",
            regression_tests=[],
        )


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
