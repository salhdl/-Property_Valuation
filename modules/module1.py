# modules/module1/module1.py

from dotenv import load_dotenv
import os
from pathlib import Path
from agno.models.google import Gemini
from agno.agent import Agent
from agno.team.team import Team
from agno.models.mistral import MistralChat
from agno.tools.file import FileTools
from agno.tools.financial_datasets import FinancialDatasetsTools
from agno.tools.pandas import PandasTools
from agno.tools.calculator import CalculatorTools
from agno.tools.python import PythonTools

# --- Pré-déclarations pour éviter "possibly unbound" (Pylance) ---
TextKnowledgeBase = None  # type: ignore[assignment]
PgVector = None           # type: ignore[assignment]
MistralEmbedder = None    # type: ignore[assignment]
KB_AVAILABLE = False

# (Optionnel) si Agno KB + PgVector + MistralEmbedder sont installés
try:
    from agno.knowledge.text import TextKnowledgeBase as _TextKnowledgeBase  # type: ignore
    from agno.vectordb.pgvector import PgVector as _PgVector                 # type: ignore
    from agno.embedder.mistral import MistralEmbedder as _MistralEmbedder    # type: ignore
    TextKnowledgeBase = _TextKnowledgeBase
    PgVector = _PgVector
    MistralEmbedder = _MistralEmbedder
    KB_AVAILABLE = True
except Exception:
    # Pas de KB/Vector/Embedder -> on continue sans KB
    pass

# --- Tools personnalisés (ton fichier tools.py) ---
try:
    from .tools import (
        mls_integration,
        avm_engine,
        market_trend_analyzer,
        market_monitor,
        comps_analyzer,
        property_condition_assessor,
        inspection_report_analyzer,
        maintenance_cost_estimator
    )
except ImportError:
    from tools import (
        mls_integration,
        avm_engine,
        market_trend_analyzer,
        market_monitor,
        comps_analyzer,
        property_condition_assessor,
        inspection_report_analyzer,
        maintenance_cost_estimator
    )

load_dotenv()

# =============================================================================
# Knowledge Base (optionnelle)
# =============================================================================
knowledge_base = None
if KB_AVAILABLE and TextKnowledgeBase and PgVector and MistralEmbedder:
    try:
        knowledge_base = TextKnowledgeBase(
            path=os.path.join(
                os.path.dirname(__file__),
                "knowledge",
                "Property_Valuation_Knowledge.md",
            ),
            formats=[".md", ".txt"],
            vector_db=PgVector(
                table_name="property_valuation_knowledge",
                db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
                embedder=MistralEmbedder(api_key=os.getenv("MISTRAL_API_KEY")),
            ),
        )
        knowledge_base.load(recreate=True)
    except Exception as e:
        print(f"Warning: Could not load knowledge base: {e}")
        print("Continuing without knowledge base...")

# =============================================================================
# LLMs (utiliser llm= dans Agent/Team)
# =============================================================================
mistral_small = MistralChat(id="mistral-small-latest", api_key=os.getenv("MISTRAL_API_KEY"))
mistral_large = MistralChat(id="mistral-large-latest", api_key=os.getenv("MISTRAL_API_KEY"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAlMVCqCy9dURLZpHa4xTvAdGUPyYi_5qQ")
# =============================================================================
# Agents (kwargs non supportés retirés : memory, show_tool_calls, agent_id, storage, markdown, knowledge)
# =============================================================================

MarketAnalyzerAgent = Agent(
    name="Market Analyzer",
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    tools=[
        FileTools(
            base_dir=Path(os.path.join(os.path.dirname(__file__), "documents"))
        ),
        FinancialDatasetsTools(),
        PandasTools(),
        # Google Search retiré (import inconnu dans ta build)
        mls_integration,
        market_trend_analyzer,
        market_monitor,
    ],
    description="Automated comparable sales analysis and market trend evaluation.",
    instructions="Provide comps, trends, neighborhood context, and positioning.",
)

ValueEstimatorAgent = Agent(
    name="Value Estimator",
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    tools=[
        FileTools(
            base_dir=Path(os.path.join(os.path.dirname(__file__), "documents"))
        ),
        FinancialDatasetsTools(),
        PandasTools(),
        CalculatorTools(),
        PythonTools(),
        avm_engine,
        comps_analyzer,
        mls_integration,
    ],
    description="AI-driven valuation using multiple methodologies.",
    instructions="Cross-validate results; provide ranges and confidence.",
)

TrendTrackerAgent = Agent(
    name="Trend Tracker",
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    tools=[
        FileTools(
    base_dir=Path(os.path.join(os.path.dirname(__file__), "documents"))
),
        FinancialDatasetsTools(),
        PandasTools(),
        PythonTools(),
        market_trend_analyzer,
        market_monitor,
        mls_integration,
    ],
    description="Monitor market movements, risks, and drivers.",
    instructions="Explain drivers and provide short-term forecasts.",
)

PropertyConditionAssessorAgent = Agent(
    name="Property Condition Assessor",
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    tools=[
        FileTools(
            base_dir=Path(os.path.join(os.path.dirname(__file__), "documents"))
        ),
        FinancialDatasetsTools(),
        PandasTools(),
        CalculatorTools(),
        PythonTools(),
        property_condition_assessor,
        inspection_report_analyzer,
        maintenance_cost_estimator,
        mls_integration,
    ],
    description="Assess property condition and maintenance requirements.",
    instructions="Provide condition scores, priorities, and cost estimates.",
)

# =============================================================================
# Team
# =============================================================================
PropertyValuationTeam = Team(
    name="Property Valuation Team",
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    members=[
        MarketAnalyzerAgent,
        ValueEstimatorAgent,
        TrendTrackerAgent,
        PropertyConditionAssessorAgent,
    ],
    description="Coordinated market analysis, trends, condition assessment, and valuation.",
    instructions="Coordinate outputs; ValueEstimator synthesizes final valuation with confidence.",
)

# =============================================================================
# Tests (print_response(input=...), Team.run(input=..., stream=...))
# =============================================================================
def test_market_analysis():
    MarketAnalyzerAgent.print_response(
        input=(
            "Analyze a 3-bed, 2-bath SFH in Downtown Austin, TX. If an exact address is provided, run a subject-property comp set within 0.75 mi and last 6 months; otherwise, analyze Downtown Austin (78701 + adjacent tracts) using the same filters. Include comps, trends, neighborhood, risks, positioning, and a 6–12 month forecast. Raise alerts for changes beyond ±5% in median price or inventory MoM."
        )
    )

def test_property_valuation():
    ValueEstimatorAgent.print_response(
        input=(
            "Perform a comprehensive valuation for a 2,200 sqft SFH, 4bd/3ba, built 2015 in Casablanca, good condition. "
            "Use comps, price per sqft, and regression. Provide confidence and valuation range."
        )
    )

def test_trend_monitoring():
    TrendTrackerAgent.print_response(
        input=(
           
            "Monitor real-time residential property trends for the Austin, TX metro area. Identify risk signals, track new economic, development, regulatory, and demographic factors, and provide a 6–12 month forecast. Use an alert threshold of significant changes above ±5% in pricing or demand indicators."
        )
    )

def test_property_condition_assessment():
    PropertyConditionAssessorAgent.print_response(
        input=(
            "Assess a 25-year-old SFH at 123 Main Street with HVAC and electrical issues. "
            "Provide condition assessment, priorities, and repair cost estimates."
        )
    )

def test_comprehensive_valuation():
    for chunk in PropertyValuationTeam.run(
        input=(
            "Comprehensive valuation:\n"
            "1) Market analysis & comps\n"
            "2) Trends & risks\n"
            "3) Multi-method valuation\n"
            "4) Final report with confidence"
        ),
        stream=True,
    ):
        try:
            print(chunk.content, end="", flush=True)
        except Exception:
            print(chunk, end="", flush=True)

if __name__ == "__main__":
    print("Property Valuation Module Loaded Successfully!")
    print("Available Agents:")
    print("1. MarketAnalyzerAgent")
    # test_market_analysis()
    print("2. ValueEstimatorAgent")
    # test_property_valuation()
    print("3. TrendTrackerAgent")
    # test_trend_monitoring()
    print("4. PropertyConditionAssessorAgent")
    test_property_condition_assessment()
    print("\nTeam: PropertyValuationTeam")
    # test_comprehensive_valuation()
