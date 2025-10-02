import streamlit as st
from module1 import (
    MarketAnalyzerAgent,
    ValueEstimatorAgent,
    TrendTrackerAgent,
    PropertyConditionAssessorAgent,
    PropertyValuationTeam
)

st.set_page_config(page_title="Property Valuation AI", layout="wide")
st.title("🏡 Property Valuation AI Platform")
st.markdown("Interagissez avec l’équipe d’agents spécialisés en évaluation immobilière.")

# Sélecteur d'agent
agent_choice = st.sidebar.selectbox(
    "Choisissez un agent ou l'équipe",
    [
        "Market Analyzer",
        "Value Estimator",
        "Trend Tracker",
        "Property Condition Assessor",
        "Property Valuation Team"
    ]
)

# Zone de saisie
user_input = st.text_area("💬 Entrez votre question / demande :", height=150)

def call_agent(choice: str, text: str):
    """Appelle l'agent choisi avec la signature correcte Agno (input=...)."""
    if choice == "Market Analyzer":
        return MarketAnalyzerAgent.run(input=text)
    elif choice == "Value Estimator":
        return ValueEstimatorAgent.run(input=text)
    elif choice == "Trend Tracker":
        return TrendTrackerAgent.run(input=text)
    elif choice == "Property Condition Assessor":
        return PropertyConditionAssessorAgent.run(input=text)
    else:
        return PropertyValuationTeam.run(input=text)

def render_response(resp):
    """Affiche la réponse sans déclencher l’erreur Streamlit JSON."""
    # 1) dict/list => JSON OK
    if isinstance(resp, (dict, list)):
        st.json(resp)
        return

    # 2) chaîne
    if isinstance(resp, str):
        st.write(resp)
        return

    # 3) objets "chunk" (générateurs / itérables)
    #    On essaie d'itérer proprement (sans considérer string/bytes/dict comme itérables)
    if hasattr(resp, "__iter__") and not isinstance(resp, (str, bytes, dict)):
        # Affichage progressif si flux de chunks
        buf = []
        for chunk in resp:
            piece = getattr(chunk, "content", None)
            if piece is None:
                piece = str(chunk)
            buf.append(piece)
            # Affiche au fil de l'eau
            st.write(piece)
        if buf:
            return  # on a déjà affiché
        # si iterable vide, on tombe au fallback plus bas

    # 4) objets spéciaux (Message/RunResult/models pydantic)
    #    Essaye model_dump (pydantic v2) ou dict()
    for attr in ("model_dump", "dict", "__dict__"):
        if hasattr(resp, attr):
            try:
                data = getattr(resp, attr)()
                if isinstance(data, (dict, list)):
                    st.json(data)
                else:
                    st.code(str(data))
                return
            except Exception:
                pass

    # 5) fallback
    st.write(str(resp))

if st.button("Analyser"):
    if not user_input.strip():
        st.warning("Veuillez entrer une question ou une demande.")
    else:
        st.info(f"🔎 Analyse en cours avec **{agent_choice}**...")
        try:
            response = call_agent(agent_choice, user_input)
            render_response(response)
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
