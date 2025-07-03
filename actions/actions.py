# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List, Optional
from datetime import datetime
import re

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, EventType, Form, FollowupAction, ActiveLoop


class ActionStartSinistreForm(Action):
    """Démarre le formulaire de déclaration de sinistre"""
    
    def name(self) -> Text:
        return "action_start_sinistre_form"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print("\n--- ActionStartSinistreForm est appelée ---")
        
        # Vérifier si l'utilisateur a déjà mentionné un type de sinistre
        text = tracker.latest_message.get("text", "").lower()
        
        # Types de sinistres possibles
        sinistre_types = {
            "accident": "accident de voiture",
            "voiture": "accident de voiture",
            "incendie": "incendie",
            "feu": "incendie",
            "vol": "vol",
            "cambriolage": "cambriolage",
            "dégât": "dégât des eaux",
            "eau": "dégât des eaux",
            "inondation": "dégât des eaux",
            "bris": "bris de glace",
            "glace": "bris de glace",
            "catastrophe": "catastrophe naturelle",
            "responsabilité": "responsabilité civile"
        }
        
        # Chercher un type de sinistre dans le message
        detected_type = None
        for keyword, sinistre_type in sinistre_types.items():
            if keyword in text:
                detected_type = sinistre_type
                break
        
        events = []
        
        if detected_type:
            # Si un type est détecté, le définir et passer à la date
            events.append(SlotSet("type_sinistre", detected_type))
            dispatcher.utter_message(text=f"J'ai compris que vous voulez déclarer un {detected_type}.")
            dispatcher.utter_message(template="utter_ask_date_sinistre")
            events.append(SlotSet("requested_slot", "date_sinistre"))
        else:
            # Sinon, demander le type
            dispatcher.utter_message(template="utter_ask_type_sinistre")
            events.append(SlotSet("requested_slot", "type_sinistre"))
        
        # Activer le formulaire
        events.append(ActiveLoop("sinistre_form"))
        
        return events


class ActionAskTypeSinistre(Action):
    """Demande le type de sinistre"""
    
    def name(self) -> Text:
        return "action_ask_type_sinistre"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print("\n--- ActionAskTypeSinistre est appelée ---")
        dispatcher.utter_message(template="utter_ask_type_sinistre")
        return [SlotSet("requested_slot", "type_sinistre")]


class ActionAskDateSinistre(Action):
    """Demande la date du sinistre"""
    
    def name(self) -> Text:
        return "action_ask_date_sinistre"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print("\n--- ActionAskDateSinistre est appelée ---")
        dispatcher.utter_message(template="utter_ask_date_sinistre")
        return [SlotSet("requested_slot", "date_sinistre")]


class ActionAskLieu(Action):
    """Demande le lieu du sinistre"""
    
    def name(self) -> Text:
        return "action_ask_lieu"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print("\n--- ActionAskLieu est appelée ---")
        dispatcher.utter_message(template="utter_ask_lieu")
        return [SlotSet("requested_slot", "lieu")]


class ActionAskDescription(Action):
    """Demande la description du sinistre"""
    
    def name(self) -> Text:
        return "action_ask_description"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print("\n--- ActionAskDescription est appelée ---")
        dispatcher.utter_message(template="utter_ask_description")
        return [SlotSet("requested_slot", "description")]


class ActionAskNbPersonnes(Action):
    """Demande le nombre de personnes impliquées"""
    
    def name(self) -> Text:
        return "action_ask_nb_personnes"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print("\n--- ActionAskNbPersonnes est appelée ---")
        dispatcher.utter_message(template="utter_ask_nb_personnes")
        return [SlotSet("requested_slot", "nb_personnes")]


class ValidateSinistreForm(FormValidationAction):
    """Valide les réponses pour le formulaire sinistre"""
    
    def name(self) -> Text:
        return "validate_sinistre_form"
    
    def extract_type_sinistre(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Extrait le type de sinistre depuis le message de l'utilisateur"""
        print("\n--- extract_type_sinistre est appelée ---")
        
        valid_types = [
            "accident de voiture", 
            "incendie", 
            "dégât des eaux", 
            "vol", 
            "cambriolage", 
            "bris de glace", 
            "catastrophe naturelle", 
            "responsabilité civile"
        ]
        
        # Récupérer le dernier message
        text = tracker.latest_message.get("text", "").lower().strip()
        print(f"Message utilisateur: {text}")
        
        # Vérifier si le message contient un type valide
        for valid_type in valid_types:
            if valid_type in text:
                print(f"Type trouvé: {valid_type}")
                return {"type_sinistre": valid_type}
        
        print("Aucun type valide trouvé")
        return {}
    
    def validate_type_sinistre(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valide le type de sinistre"""
        print("\n--- validate_type_sinistre est appelée ---")
        print(f"Slot value: {slot_value}")
        
        # D'abord essayer d'extraire le type du dernier message
        extracted = self.extract_type_sinistre(dispatcher, tracker, domain)
        if extracted:
            print(f"Type extrait: {extracted['type_sinistre']}")
            # Planifier l'action suivante
            return extracted
        
        valid_types = [
            "accident de voiture", 
            "incendie", 
            "dégât des eaux", 
            "vol", 
            "cambriolage", 
            "bris de glace", 
            "catastrophe naturelle", 
            "responsabilité civile"
        ]
        
        # Si une valeur est fournie, vérifier si elle est valide
        if slot_value:
            slot_value = slot_value.lower().strip()
            for valid_type in valid_types:
                if valid_type in slot_value or slot_value in valid_type:
                    print(f"Type validé: {valid_type}")
                    return {"type_sinistre": valid_type}
        
        print("Type non validé, demande de précision")
        dispatcher.utter_message(text=f"Je n'ai pas reconnu le type de sinistre. Veuillez choisir parmi : accident de voiture, incendie, dégât des eaux, vol/cambriolage, bris de glace, catastrophe naturelle, responsabilité civile.")
        # Retourne None pour que le bot redemande la valeur
        return {"type_sinistre": None}
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extrait une date depuis un texte"""
        # Chercher des patterns comme "le 10/10/2006" ou "10/10/2006" ou "10-10-2006"
        date_pattern1 = r"(?:le\s+)?(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})"
        match = re.search(date_pattern1, text)
        if match:
            day, month, year = match.groups()
            # S'assurer que le jour et le mois ont 2 chiffres
            day = day.zfill(2)
            month = month.zfill(2)
            # Gérer les années à 2 chiffres
            if len(year) == 2:
                year = "20" + year if int(year) < 30 else "19" + year
            return f"{day}/{month}/{year}"
        
        # Gérer les dates textuelles comme "le 10 octobre 2006"
        months = {
            "janvier": "01", "février": "02", "mars": "03", "avril": "04",
            "mai": "05", "juin": "06", "juillet": "07", "août": "08",
            "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12"
        }
        date_pattern2 = r"(?:le\s+)?(\d{1,2})(?:\s+)(\w+)(?:\s+)(\d{4})"
        match = re.search(date_pattern2, text)
        if match:
            day, month_text, year = match.groups()
            month_text = month_text.lower()
            if month_text in months:
                day = day.zfill(2)
                month = months[month_text]
                return f"{day}/{month}/{year}"
        
        return None
    
    def validate_date_sinistre(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valide la date du sinistre"""
        print("\n--- validate_date_sinistre est appelée ---")
        print(f"Slot value: {slot_value}")
        
        # Essayer d'extraire la date du dernier message
        text = tracker.latest_message.get("text", "")
        print(f"Message utilisateur: {text}")
        
        extracted_date = self.extract_date(text)
        if extracted_date:
            print(f"Date extraite: {extracted_date}")
            return {"date_sinistre": extracted_date}
        
        # Si pas de date extraite, vérifier la valeur fournie
        if slot_value:
            date_pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
            if re.match(date_pattern, slot_value):
                try:
                    # Parser la date pour s'assurer qu'elle est valide
                    day, month, year = map(int, slot_value.split("/"))
                    datetime(year, month, day)
                    print(f"Date validée: {slot_value}")
                    return {"date_sinistre": slot_value}
                except ValueError:
                    pass
            
            # Essayer d'extraire une date de la valeur fournie
            extracted_date = self.extract_date(slot_value)
            if extracted_date:
                print(f"Date extraite de la valeur: {extracted_date}")
                return {"date_sinistre": extracted_date}
        
        print("Date non validée, demande de précision")
        dispatcher.utter_message(text="Je n'ai pas pu comprendre la date. Veuillez la saisir au format JJ/MM/AAAA (par exemple 01/06/2025).")
        return {"date_sinistre": None}
    
    def validate_lieu(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valide le lieu du sinistre"""
        print("\n--- validate_lieu est appelée ---")
        print(f"Slot value: {slot_value}")
        
        text = tracker.latest_message.get("text", "")
        print(f"Message utilisateur: {text}")
        
        # Si le message fait plus de 3 caractères, on l'accepte comme lieu
        if len(text) > 3:
            print(f"Lieu accepté: {text}")
            return {"lieu": text}
        
        # Si une valeur est fournie et fait plus de 3 caractères, on l'accepte
        if slot_value and len(slot_value) > 3:
            print(f"Lieu fourni accepté: {slot_value}")
            return {"lieu": slot_value}
        
        print("Lieu non validé, demande de précision")
        dispatcher.utter_message(text="Pourriez-vous préciser le lieu du sinistre avec plus de détails ?")
        return {"lieu": None}
    
    def validate_description(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valide la description du sinistre"""
        print("\n--- validate_description est appelée ---")
        print(f"Slot value: {slot_value}")
        
        text = tracker.latest_message.get("text", "")
        print(f"Message utilisateur: {text}")
        
        # Si le message fait plus de 10 caractères, on l'accepte comme description
        if len(text) > 10:
            print(f"Description acceptée: {text}")
            return {"description": text}
        
        # Si une valeur est fournie et fait plus de 10 caractères, on l'accepte
        if slot_value and len(slot_value) > 10:
            print(f"Description fournie acceptée: {slot_value}")
            return {"description": slot_value}
        
        print("Description non validée, demande de précision")
        dispatcher.utter_message(text="Pourriez-vous décrire plus en détail ce qui s'est passé ? (au moins 10 caractères)")
        return {"description": None}
    
    def validate_nb_personnes(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valide le nombre de personnes impliquées"""
        print("\n--- validate_nb_personnes est appelée ---")
        print(f"Slot value: {slot_value}")
        
        text = tracker.latest_message.get("text", "").lower().strip()
        print(f"Message utilisateur: {text}")
        
        # Essayer de convertir le texte en nombre
        try:
            nb = int(text)
            if nb >= 0:
                print(f"Nombre de personnes accepté: {nb}")
                return {"nb_personnes": str(nb)}
        except ValueError:
            # Si ce n'est pas un nombre, vérifier si c'est "plusieurs"
            if text in ["plusieurs", "beaucoup", "nombreux", "nombreuses"]:
                print("Nombre de personnes accepté: plusieurs")
                return {"nb_personnes": "plusieurs"}
        
        # Si une valeur est fournie, essayer de la convertir
        if slot_value:
            try:
                nb = int(slot_value)
                if nb >= 0:
                    print(f"Nombre de personnes fourni accepté: {nb}")
                    return {"nb_personnes": str(nb)}
            except ValueError:
                # Si ce n'est pas un nombre, vérifier si c'est "plusieurs"
                if slot_value.lower().strip() in ["plusieurs", "beaucoup", "nombreux", "nombreuses"]:
                    print("Nombre de personnes fourni accepté: plusieurs")
                    return {"nb_personnes": "plusieurs"}
        
        print("Nombre de personnes non validé, demande de précision")
        dispatcher.utter_message(text="Je n'ai pas compris le nombre de personnes. Veuillez indiquer un nombre ou 'plusieurs'.")
        return {"nb_personnes": None}
    
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        """Détermine les slots requis"""
        print("\n--- required_slots est appelée ---")
        print(f"Domain slots: {domain_slots}")
        print(f"Requested slot: {tracker.get_slot('requested_slot')}")
        
        slots = ["type_sinistre", "date_sinistre", "lieu", "description", "nb_personnes"]
        
        # Ajouter des slots supplémentaires en fonction du type de sinistre
        type_sinistre = tracker.get_slot("type_sinistre")
        if type_sinistre == "accident de voiture":
            slots.extend(["immatriculation", "tiers_impliques", "blessures"])
        
        print(f"Slots requis: {slots}")
        return slots


class ActionSubmitSinistre(Action):
    """Soumet les informations du sinistre"""
    
    def name(self) -> Text:
        return "action_submit_sinistre"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Soumet les informations du sinistre"""
        print("\n--- ActionSubmitSinistre est appelée ---")
        
        # Récupérer les valeurs des slots
        type_sinistre = tracker.get_slot("type_sinistre")
        date_sinistre = tracker.get_slot("date_sinistre")
        lieu = tracker.get_slot("lieu")
        description = tracker.get_slot("description")
        nb_personnes = tracker.get_slot("nb_personnes")
        
        print(f"Type: {type_sinistre}")
        print(f"Date: {date_sinistre}")
        print(f"Lieu: {lieu}")
        print(f"Description: {description}")
        print(f"Nombre de personnes: {nb_personnes}")
        
        # Générer un résumé
        summary = f"Merci pour votre déclaration. Voici un résumé de votre sinistre :\n"
        summary += f"- Type de sinistre: {type_sinistre if type_sinistre else 'Non renseigné'}\n"
        summary += f"- Date: {date_sinistre if date_sinistre else 'Non renseignée'}\n"
        summary += f"- Lieu: {lieu if lieu else 'Non renseigné'}\n"
        summary += f"- Description: {description if description else 'Non renseignée'}\n"
        summary += f"- Nombre de personnes impliquées: {nb_personnes if nb_personnes else 'Non renseigné'}\n"
        
        # Ajouter des informations spécifiques au type de sinistre
        if type_sinistre == "accident de voiture":
            immatriculation = tracker.get_slot("immatriculation")
            tiers_impliques = tracker.get_slot("tiers_impliques")
            blessures = tracker.get_slot("blessures")
            
            summary += f"- Immatriculation: {immatriculation if immatriculation else 'Non renseignée'}\n"
            summary += f"- Tiers impliqués: {tiers_impliques if tiers_impliques else 'Non renseigné'}\n"
            summary += f"- Blessures: {blessures if blessures else 'Non renseigné'}\n"
        
        summary += "\nVotre déclaration a été enregistrée avec succès et sera traitée dans les plus brefs délais."
        
        # Envoyer le résumé
        dispatcher.utter_message(text=summary)
        
        return []


class ActionResetSlots(Action):
    """Réinitialise tous les slots"""
    
    def name(self) -> Text:
        return "action_reset_slots"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Réinitialise tous les slots"""
        print("\n--- ActionResetSlots est appelée ---")
        return [AllSlotsReset()]


class ActionShowSummary(Action):
    """Affiche un résumé des informations collectées"""
    
    def name(self) -> Text:
        return "action_show_summary"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Affiche un résumé des informations collectées"""
        print("\n--- ActionShowSummary est appelée ---")
        
        # Informations de base
        type_sinistre = tracker.get_slot("type_sinistre")
        date_sinistre = tracker.get_slot("date_sinistre")
        lieu = tracker.get_slot("lieu")
        description = tracker.get_slot("description")
        nb_personnes = tracker.get_slot("nb_personnes")
        
        summary = f"Voici le résumé de votre déclaration :\n"
        summary += f"- Type de sinistre: {type_sinistre if type_sinistre else 'Non renseigné'}\n"
        summary += f"- Date: {date_sinistre if date_sinistre else 'Non renseignée'}\n"
        summary += f"- Lieu: {lieu if lieu else 'Non renseigné'}\n"
        summary += f"- Description: {description if description else 'Non renseignée'}\n"
        summary += f"- Nombre de personnes impliquées: {nb_personnes if nb_personnes else 'Non renseigné'}\n"
        
        # Ajouter des informations spécifiques au type de sinistre
        if type_sinistre == "accident de voiture":
            immatriculation = tracker.get_slot("immatriculation")
            tiers_impliques = tracker.get_slot("tiers_impliques")
            blessures = tracker.get_slot("blessures")
            
            summary += f"- Immatriculation: {immatriculation if immatriculation else 'Non renseignée'}\n"
            summary += f"- Tiers impliqués: {tiers_impliques if tiers_impliques else 'Non renseigné'}\n"
            summary += f"- Blessures: {blessures if blessures else 'Non renseigné'}\n"
        elif type_sinistre == "incendie":
            type_bien = tracker.get_slot("type_bien")
            pompiers = tracker.get_slot("pompiers")
            dommages_majeurs = tracker.get_slot("dommages_majeurs")
            
            summary += f"- Type de bien: {type_bien if type_bien else 'Non renseigné'}\n"
            summary += f"- Pompiers: {pompiers if pompiers else 'Non renseigné'}\n"
            summary += f"- Dommages majeurs: {dommages_majeurs if dommages_majeurs else 'Non renseigné'}\n"
        elif type_sinistre in ["vol", "cambriolage"]:
            depot_plainte = tracker.get_slot("depot_plainte")
            biens_voles = tracker.get_slot("biens_voles")
            
            summary += f"- Dépôt de plainte: {depot_plainte if depot_plainte else 'Non renseigné'}\n"
            summary += f"- Biens volés: {biens_voles if biens_voles else 'Non renseignés'}\n"
        elif type_sinistre == "responsabilité civile":
            identite_tiers = tracker.get_slot("identite_tiers")
            nature_dommage = tracker.get_slot("nature_dommage")
            
            summary += f"- Identité du tiers: {identite_tiers if identite_tiers else 'Non renseignée'}\n"
            summary += f"- Nature du dommage: {nature_dommage if nature_dommage else 'Non renseignée'}\n"
        
        dispatcher.utter_message(text=summary)
        
        return []
