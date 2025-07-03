import streamlit as st
import json
from datetime import datetime
import re

# Configuration de la page
st.set_page_config(
    page_title="Assistant Déclaration Sinistre",
    page_icon="🚗",
    layout="wide"
)

# Initialisation des variables de session
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'sinistre_data' not in st.session_state:
    st.session_state.sinistre_data = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Types de sinistres et leurs questions spécifiques
SINISTRE_TYPES = {
    "accident_voiture": {
        "label": "Accident de voiture",
        "questions": [
            "type_sinistre", "date_sinistre", "lieu", "description", 
            "nb_personnes", "immatriculation", "tiers_impliques", "blessures"
        ]
    },
    "incendie": {
        "label": "Incendie",
        "questions": [
            "type_sinistre", "date_sinistre", "lieu", "description", 
            "nb_personnes", "type_bien", "pompiers", "dommages_majeurs"
        ]
    },
    "vol": {
        "label": "Vol/Cambriolage",
        "questions": [
            "type_sinistre", "date_sinistre", "lieu", "description", 
            "nb_personnes", "depot_plainte", "biens_voles"
        ]
    },
    "degat_eaux": {
        "label": "Dégât des eaux",
        "questions": [
            "type_sinistre", "date_sinistre", "lieu", "description", 
            "nb_personnes", "origine_fuite", "dommages_majeurs"
        ]
    }
}

# Questions et leurs libellés
QUESTIONS = {
    "type_sinistre": "Quel type de sinistre souhaitez-vous déclarer ?",
    "date_sinistre": "À quelle date s'est produit le sinistre ? (JJ/MM/AAAA)",
    "lieu": "Où s'est produit le sinistre ?",
    "description": "Pouvez-vous décrire ce qui s'est passé ?",
    "nb_personnes": "Combien de personnes étaient impliquées ?",
    "immatriculation": "Quelle est l'immatriculation du véhicule ?",
    "tiers_impliques": "Y a-t-il d'autres personnes impliquées ? (oui/non)",
    "blessures": "Y a-t-il eu des blessés ? (oui/non)",
    "type_bien": "Quel type de bien a été touché ?",
    "pompiers": "Les pompiers sont-ils intervenus ? (oui/non)",
    "dommages_majeurs": "Y a-t-il des dommages importants ? (oui/non)",
    "depot_plainte": "Avez-vous déposé plainte ? (oui/non)",
    "biens_voles": "Quels biens ont été volés ?",
    "origine_fuite": "Quelle est l'origine de la fuite ?"
}

def add_message(role, content):
    """Ajoute un message à l'historique"""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

def detect_sinistre_type(text):
    """Détecte automatiquement le type de sinistre"""
    text = text.lower()
    if any(word in text for word in ["accident", "voiture", "véhicule", "collision"]):
        return "accident_voiture"
    elif any(word in text for word in ["incendie", "feu", "brûlé"]):
        return "incendie"
    elif any(word in text for word in ["vol", "cambriolage", "volé"]):
        return "vol"
    elif any(word in text for word in ["eau", "fuite", "inondation", "dégât"]):
        return "degat_eaux"
    return None

def validate_date(date_str):
    """Valide le format de date"""
    patterns = [
        r"^\d{2}/\d{2}/\d{4}$",
        r"^\d{1,2}/\d{1,2}/\d{4}$"
    ]
    return any(re.match(pattern, date_str) for pattern in patterns)

def get_current_question():
    """Retourne la question actuelle"""
    if st.session_state.step == 0:
        return "Bonjour ! Je suis votre assistant pour déclarer un sinistre. Quel type de sinistre souhaitez-vous déclarer ?"
    
    sinistre_type = st.session_state.sinistre_data.get('type_sinistre')
    if not sinistre_type:
        return "Veuillez d'abord sélectionner le type de sinistre."
    
    questions = SINISTRE_TYPES[sinistre_type]["questions"]
    
    if st.session_state.step <= len(questions):
        question_key = questions[st.session_state.step - 1]
        return QUESTIONS[question_key]
    
    return "Merci ! Votre déclaration est terminée."

def process_answer(answer):
    """Traite la réponse de l'utilisateur"""
    if st.session_state.step == 0:
        # Première étape : détection du type de sinistre
        detected_type = detect_sinistre_type(answer)
        if detected_type:
            st.session_state.sinistre_data['type_sinistre'] = detected_type
            st.session_state.step = 1
            return f"J'ai compris que vous voulez déclarer un {SINISTRE_TYPES[detected_type]['label']}."
        else:
            return "Je n'ai pas compris le type de sinistre. Pouvez-vous préciser : accident de voiture, incendie, vol/cambriolage, ou dégât des eaux ?"
    
    # Étapes suivantes
    sinistre_type = st.session_state.sinistre_data.get('type_sinistre')
    if not sinistre_type:
        return "Erreur : type de sinistre non défini."
    
    questions = SINISTRE_TYPES[sinistre_type]["questions"]
    
    if st.session_state.step <= len(questions):
        question_key = questions[st.session_state.step - 1]
        
        # Validation spécifique selon le type de question
        if question_key == "date_sinistre" and not validate_date(answer):
            return "Format de date invalide. Veuillez utiliser le format JJ/MM/AAAA."
        
        # Enregistrer la réponse
        st.session_state.sinistre_data[question_key] = answer
        st.session_state.step += 1
        
        if st.session_state.step <= len(questions):
            return "Merci ! Question suivante :"
        else:
            return "Parfait ! Votre déclaration est terminée."
    
    return "Déclaration terminée."

def generate_summary():
    """Génère un résumé de la déclaration"""
    data = st.session_state.sinistre_data
    sinistre_type = data.get('type_sinistre', '')
    
    summary = f"## 📋 Résumé de votre déclaration\n\n"
    summary += f"**Type de sinistre :** {SINISTRE_TYPES.get(sinistre_type, {}).get('label', 'Non défini')}\n\n"
    
    for key, value in data.items():
        if key != 'type_sinistre' and key in QUESTIONS:
            summary += f"**{QUESTIONS[key].replace(' ?', '')} :** {value}\n\n"
    
    summary += f"**Date de déclaration :** {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"
    summary += "✅ Votre déclaration a été enregistrée avec succès !"
    
    return summary

# Interface utilisateur
st.title("🚗 Assistant de Déclaration de Sinistre")

# Sidebar avec informations
with st.sidebar:
    st.header("📊 Progression")
    
    if st.session_state.sinistre_data.get('type_sinistre'):
        sinistre_type = st.session_state.sinistre_data['type_sinistre']
        total_questions = len(SINISTRE_TYPES[sinistre_type]["questions"])
        progress = min(st.session_state.step / total_questions, 1.0)
        st.progress(progress)
        st.write(f"Étape {st.session_state.step}/{total_questions}")
    
    st.header("ℹ️ Types de sinistres")
    for key, value in SINISTRE_TYPES.items():
        st.write(f"• {value['label']}")
    
    if st.button("🔄 Recommencer"):
        st.session_state.step = 0
        st.session_state.sinistre_data = {}
        st.session_state.messages = []
        st.rerun()

# Zone de chat
st.header("💬 Conversation")

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(f"**{message['timestamp']}** - {message['content']}")

# Message initial du bot
if not st.session_state.messages:
    initial_message = get_current_question()
    add_message("assistant", initial_message)
    with st.chat_message("assistant"):
        st.write(f"**{datetime.now().strftime('%H:%M:%S')}** - {initial_message}")

# Input utilisateur
if prompt := st.chat_input("Tapez votre réponse ici..."):
    # Afficher le message utilisateur
    add_message("user", prompt)
    with st.chat_message("user"):
        st.write(f"**{datetime.now().strftime('%H:%M:%S')}** - {prompt}")
    
    # Traiter la réponse
    response = process_answer(prompt)
    add_message("assistant", response)
    
    # Afficher la réponse du bot
    with st.chat_message("assistant"):
        st.write(f"**{datetime.now().strftime('%H:%M:%S')}** - {response}")
    
    # Poser la question suivante si nécessaire
    if st.session_state.step > 0:
        next_question = get_current_question()
        if "terminée" not in next_question:
            add_message("assistant", next_question)
            with st.chat_message("assistant"):
                st.write(f"**{datetime.now().strftime('%H:%M:%S')}** - {next_question}")
    
    st.rerun()

# Affichage du résumé si terminé
sinistre_type = st.session_state.sinistre_data.get('type_sinistre')
if sinistre_type:
    total_questions = len(SINISTRE_TYPES[sinistre_type]["questions"])
    if st.session_state.step > total_questions:
        st.markdown("---")
        st.markdown(generate_summary())
        
        # Bouton de téléchargement
        summary_json = json.dumps(st.session_state.sinistre_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Télécharger la déclaration (JSON)",
            data=summary_json,
            file_name=f"declaration_sinistre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        ) 