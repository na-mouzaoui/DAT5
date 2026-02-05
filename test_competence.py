import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QRadioButton, QPushButton,
                             QButtonGroup, QMessageBox, QFrame, QLineEdit, QFormLayout,
                             QStackedWidget, QInputDialog, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import datetime
from pdf_generator import generate_test_report_pdf

app_state = {
    'window': None,
    'stacked_widget': None,
    'form_page': None,
    'instructions_page': None,
    'test_page': None,
    'thanks_page': None,
    'report_page': None,
    'questions': [],
    'current_question': 0,
    'user_answers': [],
    'candidat_info': {},
    'timer': None,
    'timer_label': None,
    'time_remaining': 20 * 60,
    'question_label': None,
    'instruction_label': None,
    'phrase_label': None,
    'button_group': None,
    'radio_buttons': [],
    'nom_input': None,
    'prenom_input': None,
    'age_input': None,
    'homme_radio': None,
    'femme_radio': None,
    'sexe_group': None
}

def load_questions():
    """Charger les questions depuis le fichier JSON"""
    try:
        with open('questions_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        QMessageBox.critical(None, "Erreur", f"Erreur lors du chargement des questions:\n{str(e)}")
        sys.exit(1)

def update_timer():
    """Mettre à jour le compte à rebours"""
    app_state['time_remaining'] -= 1
    minutes = app_state['time_remaining'] // 60
    seconds = app_state['time_remaining'] % 60
    app_state['timer_label'].setText(f"Temps restant: {minutes:02d}:{seconds:02d}")
    
    if app_state['time_remaining'] <= 300:
        app_state['timer_label'].setStyleSheet("color: #f44336; font-size: 18px; font-weight: bold; padding: 10px;")
    elif app_state['time_remaining'] <= 600:
        app_state['timer_label'].setStyleSheet("color: #FF9800; font-size: 18px; font-weight: bold; padding: 10px;")
    
    if app_state['time_remaining'] <= 0:
        time_expired()

def time_expired():
    """Gérer l'expiration du temps"""
    app_state['timer'].stop()
    QMessageBox.information(app_state['window'], "Temps écoulé", "Le temps imparti est écoulé. Le test sera soumis automatiquement.")
    app_state['stacked_widget'].setCurrentWidget(app_state['thanks_page'])
    generate_pdf_report()

def generate_pdf_report():
    """Générer le rapport PDF"""
    score = sum(1 for i, (_, _, _, correct) in enumerate(app_state['questions'])
                if app_state['user_answers'][i] == correct)
    total_questions = len(app_state['questions'])
    
    try:
        pdf_path = generate_test_report_pdf(
            app_state['candidat_info'],
            score,
            total_questions,
            "Compétence Linguistique"
        )
        QMessageBox.information(app_state['window'], "PDF généré", f"Le rapport a été téléchargé avec succès:\n{pdf_path}")
    except Exception as e:
        QMessageBox.critical(app_state['window'], "Erreur", f"Erreur lors de la génération du PDF:\n{str(e)}")

def validate_form():
    """Valider le formulaire d'informations"""
    if not app_state['nom_input'].text().strip():
        QMessageBox.warning(app_state['window'], "Champ requis", "Veuillez entrer votre nom.")
        return
    if not app_state['prenom_input'].text().strip():
        QMessageBox.warning(app_state['window'], "Champ requis", "Veuillez entrer votre prénom.")
        return
    if not app_state['age_input'].text().strip():
        QMessageBox.warning(app_state['window'], "Champ requis", "Veuillez entrer votre âge.")
        return
    if not app_state['homme_radio'].isChecked() and not app_state['femme_radio'].isChecked():
        QMessageBox.warning(app_state['window'], "Champ requis", "Veuillez sélectionner votre sexe.")
        return
    
    sexe = "Homme" if app_state['homme_radio'].isChecked() else "Femme"
    app_state['candidat_info'] = {
        'nom': app_state['nom_input'].text().strip(),
        'prenom': app_state['prenom_input'].text().strip(),
        'age': app_state['age_input'].text().strip(),
        'sexe': sexe,
        'date': datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    app_state['stacked_widget'].setCurrentWidget(app_state['instructions_page'])

def start_test():
    """Démarrer le test"""
    app_state['stacked_widget'].setCurrentWidget(app_state['test_page'])
    app_state['time_remaining'] = 20 * 60
    app_state['timer'].start(1000)
    display_question()

def display_question():
    """Afficher la question actuelle"""
    idx = app_state['current_question']
    question, consigne, propositions, _ = app_state['questions'][idx]
    
    app_state['question_label'].setText(f"Question {idx + 1} / {len(app_state['questions'])}")
    app_state['instruction_label'].setText(consigne)
    app_state['phrase_label'].setText(question)
    
    for i, radio in enumerate(app_state['radio_buttons']):
        if i < len(propositions):
            radio.setText(propositions[i])
            radio.setVisible(True)
        else:
            radio.setVisible(False)
    
    saved_answer = app_state['user_answers'][idx]
    if saved_answer != -1:
        app_state['radio_buttons'][saved_answer].setChecked(True)
    else:
        app_state['button_group'].setExclusive(False)
        for radio in app_state['radio_buttons']:
            radio.setChecked(False)
        app_state['button_group'].setExclusive(True)

def on_answer_selected(index):
    """Enregistrer la réponse sélectionnée"""
    app_state['user_answers'][app_state['current_question']] = index

def previous_question():
    """Question précédente"""
    if app_state['current_question'] > 0:
        app_state['current_question'] -= 1
        display_question()

def next_question():
    """Question suivante"""
    if app_state['current_question'] < len(app_state['questions']) - 1:
        app_state['current_question'] += 1
        display_question()

def submit_test():
    """Soumettre le test"""
    unanswered = [i+1 for i, ans in enumerate(app_state['user_answers']) if ans == -1]
    if unanswered:
        QMessageBox.warning(app_state['window'], "Questions non répondues",
                           f"Veuillez répondre à toutes les questions.\nQuestions: {', '.join(map(str, unanswered))}")
        return
    # Arrêter le timer
    app_state['timer'].stop()
    # Afficher page de remerciement
    app_state['stacked_widget'].setCurrentWidget(app_state['thanks_page'])
    # Générer le PDF automatiquement
    generate_pdf_report()

def request_password():
    """Demander le mot de passe pour le rapport"""
    password, ok = QInputDialog.getText(app_state['window'], "Mot de passe requis",
                                       "Entrez le mot de passe:", QLineEdit.Password)
    if ok:
        if password == "dadou76":
            show_report()
        else:
            QMessageBox.warning(app_state['window'], "Mot de passe incorrect",
                              "Le mot de passe est incorrect.")
            request_password()

def show_report():
    """Afficher le rapport de résultats"""
    score = sum(1 for i, (_, _, _, correct) in enumerate(app_state['questions'])
                if app_state['user_answers'][i] == correct)
    percentage = (score / len(app_state['questions'])) * 100
    
    classification_colors = [
        (90, "Excellent", "#4CAF50"),
        (75, "Bon", "#8BC34A"),
        (60, "Moyen", "#FFC107"),
        (40, "Mauvais", "#FF9800"),
    ]
    classification = "Médiocre"
    class_color = "#f44336"
    for threshold, label, hex_color in classification_colors:
        if percentage >= threshold:
            classification = label
            class_color = hex_color
            break

    if app_state['report_page']:
        app_state['stacked_widget'].removeWidget(app_state['report_page'])

    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(24)
    layout.setContentsMargins(60, 60, 60, 60)

    title = QLabel("Rapport de Test de Compétence Linguistique")
    title.setFont(QFont("Arial", 28, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    info = app_state['candidat_info']
    info_label = QLabel(f"{info.get('prenom', '')} {info.get('nom', '')} — {info.get('age', '')} ans — {info.get('sexe', '')} — {info.get('date', '')}")
    info_label.setFont(QFont("Arial", 14))
    info_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(info_label)

    result_label = QLabel(f"Résultat : {percentage:.1f}% ({score}/{len(app_state['questions'])})")
    result_label.setFont(QFont("Arial", 20))
    result_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(result_label)

    class_label = QLabel(f"Classification : {classification}")
    class_label.setFont(QFont("Arial", 20, QFont.Bold))
    class_label.setAlignment(Qt.AlignCenter)
    class_label.setStyleSheet(f"color: {class_color};")
    layout.addWidget(class_label)

    close_btn = QPushButton("Fermer")
    close_btn.clicked.connect(app_state['window'].close)
    layout.addWidget(close_btn, alignment=Qt.AlignCenter)

    app_state['report_page'] = page
    app_state['stacked_widget'].addWidget(page)
    app_state['stacked_widget'].setCurrentWidget(page)

def restart_test():
    """Recommencer le test"""
    app_state['current_question'] = 0
    app_state['user_answers'] = [-1] * len(app_state['questions'])
    app_state['nom_input'].clear()
    app_state['prenom_input'].clear()
    app_state['age_input'].clear()
    app_state['homme_radio'].setChecked(False)
    app_state['femme_radio'].setChecked(False)
    if app_state['report_page']:
        app_state['stacked_widget'].removeWidget(app_state['report_page'])
        app_state['report_page'] = None
    app_state['stacked_widget'].setCurrentWidget(app_state['form_page'])

def create_form_page():
    """Créer la page du formulaire"""
    page = QWidget()
    page.setStyleSheet("background: #fff;")
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(32)
    layout.setContentsMargins(40, 40, 40, 40)
    
    main_container = QWidget()
    main_container.setMaximumWidth(600)
    main_container.setStyleSheet("background: #fff; border-radius: 10px; padding: 40px 40px;")
    main_layout = QVBoxLayout(main_container)
    main_layout.setSpacing(24)
    
    title = QLabel("Informations du Candidat")
    title.setFont(QFont("Arial", 24, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("color: #111; padding-bottom: 18px;")
    main_layout.addWidget(title)
    
    form_container = QWidget()
    form_layout = QFormLayout(form_container)
    form_layout.setSpacing(16)
    form_layout.setLabelAlignment(Qt.AlignLeft)
    form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
    
    label_style = "font-size: 15px; color: #222; font-weight: 500; padding: 5px 0; font-family: Arial;"
    input_style = """
        QLineEdit {
            padding: 10px;
            border: 1px solid #d1d1d1;
            border-radius: 5px;
            font-size: 15px;
            background: #fafafa;
            min-width: 320px;
            color: #222;
            font-family: Arial;
        }
        QLineEdit:focus {
            border-color: #222;
            background: #fff;
            outline: none;
        }
    """
    
    app_state['nom_input'] = QLineEdit()
    app_state['nom_input'].setStyleSheet(input_style)
    nom_label = QLabel("Nom")
    nom_label.setStyleSheet(label_style)
    form_layout.addRow(nom_label, app_state['nom_input'])
    
    app_state['prenom_input'] = QLineEdit()
    app_state['prenom_input'].setStyleSheet(input_style)
    prenom_label = QLabel("Prénom")
    prenom_label.setStyleSheet(label_style)
    form_layout.addRow(prenom_label, app_state['prenom_input'])
    
    app_state['age_input'] = QLineEdit()
    app_state['age_input'].setStyleSheet(input_style)
    age_label = QLabel("Âge")
    age_label.setStyleSheet(label_style)
    form_layout.addRow(age_label, app_state['age_input'])
    
    sexe_label = QLabel("Sexe")
    sexe_label.setStyleSheet(label_style)
    app_state['sexe_group'] = QButtonGroup()
    
    radio_style = """
        QRadioButton {
            font-size: 15px;
            color: #222;
            padding: 8px 24px 8px 0;
            border-radius: 5px;
            background: transparent;
            font-family: Arial;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }
        QRadioButton:checked {
            background: #ededed;
            color: #222;
            font-weight: bold;
        }
    """
    
    sexe_row = QWidget()
    sexe_row_layout = QHBoxLayout(sexe_row)
    sexe_row_layout.setContentsMargins(0, 0, 0, 0)
    sexe_row_layout.setSpacing(24)
    
    app_state['homme_radio'] = QRadioButton("Homme")
    app_state['homme_radio'].setStyleSheet(radio_style)
    app_state['sexe_group'].addButton(app_state['homme_radio'])
    sexe_row_layout.addWidget(app_state['homme_radio'])
    
    app_state['femme_radio'] = QRadioButton("Femme")
    app_state['femme_radio'].setStyleSheet(radio_style)
    app_state['sexe_group'].addButton(app_state['femme_radio'])
    sexe_row_layout.addWidget(app_state['femme_radio'])
    
    sexe_row_layout.addStretch()
    form_layout.addRow(sexe_label, sexe_row)
    
    main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
    
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setFrameShadow(QFrame.Sunken)
    sep.setStyleSheet("background: #fff; min-height: 1px; max-height: 1px; margin: 18px 0;")
    main_layout.addWidget(sep)
    
    next_btn = QPushButton("Continuer")
    next_btn.setFont(QFont("Arial", 15, QFont.Bold))
    next_btn.setFixedHeight(40)
    next_btn.setMinimumWidth(180)
    next_btn.setStyleSheet("""
        QPushButton {
            background-color: #222;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 10px 0;
            font-size: 15px;
            font-family: Arial;
        }
        QPushButton:hover {
            background-color: #444;
        }
    """)
    next_btn.setCursor(Qt.PointingHandCursor)
    next_btn.clicked.connect(validate_form)
    main_layout.addWidget(next_btn, alignment=Qt.AlignCenter)
    
    layout.addWidget(main_container, alignment=Qt.AlignCenter)
    return page

def create_instructions_page():
    """Créer la page d'instructions"""
    page = QWidget()
    page.setStyleSheet("background: #fff;")
    layout = QVBoxLayout(page)
    layout.setSpacing(32)
    layout.setContentsMargins(80, 60, 80, 60)
    
    title = QLabel("Instructions du Test")
    title.setFont(QFont("Arial", 20, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("color: #222; padding: 10px 0 18px 0;")
    layout.addWidget(title)
    
    instructions_container = QWidget()
    instructions_container.setStyleSheet("background: #fff; border-radius: 8px; padding: 32px 32px;")
    instructions_layout = QVBoxLayout(instructions_container)
    instructions_layout.setSpacing(12)
    
    instructions_text = [
        "Ce test évalue vos compétences linguistiques",
        "Prenez le temps nécessaire pour chaque question",
        "Choisissez la réponse la plus appropriée",
        "Vous pouvez naviguer entre les questions",
        "Vos réponses sont automatiquement sauvegardées",
        "Cliquez sur 'Soumettre' à la dernière question"
    ]
    
    for text in instructions_text:
        label = QLabel(text)
        label.setFont(QFont("Arial", 14))
        label.setStyleSheet("color: #222; padding: 8px 0 8px 0;")
        label.setWordWrap(True)
        instructions_layout.addWidget(label)
    
    layout.addWidget(instructions_container)
    
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setFrameShadow(QFrame.Sunken)
    sep.setStyleSheet("background: #fff; min-height: 1px; max-height: 1px; margin: 18px 0;")
    layout.addWidget(sep)
    
    start_btn = QPushButton("Commencer le Test")
    start_btn.setFont(QFont("Arial", 15, QFont.Bold))
    start_btn.setFixedHeight(40)
    start_btn.setMinimumWidth(180)
    start_btn.setStyleSheet("""
        QPushButton {
            background-color: #222;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 10px 0;
            font-size: 15px;
            font-family: Arial;
        }
        QPushButton:hover {
            background-color: #444;
        }
    """)
    start_btn.setCursor(Qt.PointingHandCursor)
    start_btn.clicked.connect(start_test)
    
    button_container = QWidget()
    button_layout = QHBoxLayout(button_container)
    button_layout.addStretch()
    button_layout.addWidget(start_btn)
    button_layout.addStretch()
    layout.addWidget(button_container)
    
    return page

def create_test_page():
    """Créer la page du test"""
    page = QWidget()
    
    main_layout = QHBoxLayout(page)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addStretch(1)
    
    content_widget = QWidget()
    content_widget.setMaximumWidth(1400)
    content_widget.setStyleSheet("background-color: white;")
    main_layout.addWidget(content_widget, 4)
    main_layout.addStretch(1)
    
    content_layout = QVBoxLayout()
    content_layout.setContentsMargins(40, 50, 40, 50)
    content_layout.setSpacing(35)
    content_widget.setLayout(content_layout)
    
    # Timer
    app_state['timer_label'] = QLabel("Temps restant: 20:00")
    app_state['timer_label'].setFont(QFont("Arial", 18, QFont.Bold))
    app_state['timer_label'].setAlignment(Qt.AlignCenter)
    app_state['timer_label'].setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold; padding: 10px;")
    content_layout.addWidget(app_state['timer_label'])
    
    # Numéro de question
    app_state['question_label'] = QLabel()
    app_state['question_label'].setFont(QFont("Arial", 22, QFont.Bold))
    app_state['question_label'].setAlignment(Qt.AlignCenter)
    app_state['question_label'].setStyleSheet("color: #111; background: transparent; padding: 10px;")
    content_layout.addWidget(app_state['question_label'])
    
    # Consigne
    app_state['instruction_label'] = QLabel()
    app_state['instruction_label'].setFont(QFont("Arial", 15))
    app_state['instruction_label'].setWordWrap(True)
    app_state['instruction_label'].setAlignment(Qt.AlignLeft)
    app_state['instruction_label'].setStyleSheet("color: #444; background: transparent; padding: 10px;")
    content_layout.addWidget(app_state['instruction_label'])
    
    # Phrase à compléter
    phrase_container = QWidget()
    phrase_container.setStyleSheet("background-color: white; border-radius: 8px; padding: 25px 35px;")
    phrase_layout = QVBoxLayout(phrase_container)
    
    app_state['phrase_label'] = QLabel()
    app_state['phrase_label'].setFont(QFont("Arial", 20, QFont.Bold))
    app_state['phrase_label'].setWordWrap(True)
    app_state['phrase_label'].setAlignment(Qt.AlignCenter)
    app_state['phrase_label'].setStyleSheet("color: #222; background: transparent;")
    phrase_layout.addWidget(app_state['phrase_label'])
    content_layout.addWidget(phrase_container)
    
    # Zone des propositions (3 colonnes: 2-2-1)
    propositions_container = QWidget()
    propositions_container.setStyleSheet("background-color: white;")
    propositions_layout = QHBoxLayout(propositions_container)
    propositions_layout.setSpacing(20)
    propositions_layout.setContentsMargins(0, 20, 0, 20)
    
    app_state['button_group'] = QButtonGroup()
    app_state['radio_buttons'] = []
    
    radio_style = """
        QRadioButton {
            font-size: 16px;
            color: #222;
            padding: 20px 28px;
            border-radius: 8px;
            background: #fafafa;
            border: 2px solid transparent;
            font-family: Arial;
        }
        QRadioButton:checked {
            background: #ededed;
            color: #222;
            font-weight: bold;
            border: 2px solid #000;
        }
        QRadioButton::indicator {
            width: 0px;
            height: 0px;
        }
    """
    
    # Colonne 1 (2 boutons)
    col1 = QWidget()
    col1_layout = QVBoxLayout(col1)
    col1_layout.setSpacing(15)
    for i in range(2):
        radio = QRadioButton()
        radio.setFont(QFont("Arial", 16))
        radio.setStyleSheet(radio_style)
        radio.setCursor(Qt.PointingHandCursor)
        radio.toggled.connect(lambda checked, idx=i: on_answer_selected(idx) if checked else None)
        app_state['button_group'].addButton(radio, i)
        app_state['radio_buttons'].append(radio)
        col1_layout.addWidget(radio)
    propositions_layout.addWidget(col1, 1)
    
    # Colonne 2 (2 boutons)
    col2 = QWidget()
    col2_layout = QVBoxLayout(col2)
    col2_layout.setSpacing(15)
    for i in range(2, 4):
        radio = QRadioButton()
        radio.setFont(QFont("Arial", 16))
        radio.setStyleSheet(radio_style)
        radio.setCursor(Qt.PointingHandCursor)
        radio.toggled.connect(lambda checked, idx=i: on_answer_selected(idx) if checked else None)
        app_state['button_group'].addButton(radio, i)
        app_state['radio_buttons'].append(radio)
        col2_layout.addWidget(radio)
    propositions_layout.addWidget(col2, 1)
    
    # Colonne 3 (1 bouton centré)
    col3 = QWidget()
    col3_layout = QVBoxLayout(col3)
    col3_layout.addStretch()
    radio = QRadioButton()
    radio.setFont(QFont("Arial", 16))
    radio.setStyleSheet(radio_style)
    radio.setCursor(Qt.PointingHandCursor)
    radio.toggled.connect(lambda checked: on_answer_selected(4) if checked else None)
    app_state['button_group'].addButton(radio, 4)
    app_state['radio_buttons'].append(radio)
    col3_layout.addWidget(radio)
    col3_layout.addStretch()
    propositions_layout.addWidget(col3, 1)
    
    content_layout.addWidget(propositions_container)
    content_layout.addStretch()
    
    # Boutons de navigation
    nav_container = QWidget()
    nav_container.setStyleSheet("background-color: white;")
    nav_layout = QHBoxLayout(nav_container)
    nav_layout.setContentsMargins(0, 15, 0, 0)
    nav_layout.setSpacing(24)
    
    button_style = """
        QPushButton {
            background-color: #222;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-family: Arial;
        }
        QPushButton:hover {
            background-color: #444;
        }
    """
    
    app_state['prev_button'] = QPushButton("← Précédent")
    app_state['prev_button'].setFont(QFont("Arial", 14))
    app_state['prev_button'].setFixedHeight(40)
    app_state['prev_button'].setMinimumWidth(140)
    app_state['prev_button'].setStyleSheet(button_style)
    app_state['prev_button'].setCursor(Qt.PointingHandCursor)
    app_state['prev_button'].clicked.connect(previous_question)
    nav_layout.addWidget(app_state['prev_button'])
    
    nav_layout.addStretch()
    
    app_state['next_button'] = QPushButton("Suivant →")
    app_state['next_button'].setFont(QFont("Arial", 14))
    app_state['next_button'].setFixedHeight(40)
    app_state['next_button'].setMinimumWidth(140)
    app_state['next_button'].setStyleSheet(button_style)
    app_state['next_button'].setCursor(Qt.PointingHandCursor)
    app_state['next_button'].clicked.connect(next_question)
    nav_layout.addWidget(app_state['next_button'])
    
    app_state['submit_button'] = QPushButton("Soumettre")
    app_state['submit_button'].setFont(QFont("Arial", 14, QFont.Bold))
    app_state['submit_button'].setFixedHeight(40)
    app_state['submit_button'].setMinimumWidth(160)
    app_state['submit_button'].setStyleSheet("""
        QPushButton {
            background-color: #444;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-family: Arial;
        }
        QPushButton:hover {
            background-color: #222;
        }
    """)
    app_state['submit_button'].setCursor(Qt.PointingHandCursor)
    app_state['submit_button'].clicked.connect(submit_test)
    app_state['submit_button'].hide()
    nav_layout.addWidget(app_state['submit_button'])
    
    content_layout.addWidget(nav_container)
    
    return page

def create_thanks_page():
    """Créer la page de remerciement"""
    page = QWidget()
    page.setStyleSheet("background: #fff;")
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(0)
    layout.setContentsMargins(60, 100, 60, 100)
    
    # Conteneur principal centré
    main_container = QWidget()
    main_container.setMaximumWidth(1200)
    main_container.setStyleSheet("background: #fff; border-radius: 12px; padding: 80px 100px;")
    main_layout = QVBoxLayout(main_container)
    main_layout.setSpacing(50)
    main_layout.setAlignment(Qt.AlignCenter)
    
    # Titre principal avec espacement
    
    # Titre principal
    title = QLabel("Test Terminé avec Succès")
    title.setFont(QFont("Arial", 36, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("color: #111; padding: 15px 0;")
    title.setMinimumHeight(80)
    main_layout.addWidget(title)
    
    # Séparateur
    sep1 = QFrame()
    sep1.setFrameShape(QFrame.HLine)
    sep1.setFrameShadow(QFrame.Sunken)
    sep1.setStyleSheet("background: #fff; min-height: 2px; max-height: 2px; margin: 25px 100px;")
    main_layout.addWidget(sep1)
    
    # Message de remerciement
    thanks_msg = QLabel(
        "Merci d'avoir complété ce test de compétence linguistique.\n\n"
        "Vos réponses ont été enregistrées avec succès.\n\n"
        "Vous pouvez maintenant consulter votre rapport détaillé\n"
        "ou recommencer un nouveau test."
    )
    thanks_msg.setFont(QFont("Arial", 18))
    thanks_msg.setAlignment(Qt.AlignCenter)
    thanks_msg.setStyleSheet("color: #444; padding: 40px 50px; line-height: 2.0;")
    thanks_msg.setWordWrap(True)
    thanks_msg.setMinimumHeight(250)
    main_layout.addWidget(thanks_msg)
    
    # Séparateur
    sep2 = QFrame()
    sep2.setFrameShape(QFrame.HLine)
    sep2.setFrameShadow(QFrame.Sunken)
    sep2.setStyleSheet("background: #fff; min-height: 2px; max-height: 2px; margin: 20px 80px;")
    main_layout.addWidget(sep2)
    
    # Conteneur des boutons
    buttons_container = QWidget()
    buttons_container.setStyleSheet("background: #fff;")
    buttons_layout = QVBoxLayout(buttons_container)
    buttons_layout.setSpacing(20)
    buttons_layout.setAlignment(Qt.AlignCenter)
    
    # Bouton rapport
    report_btn = QPushButton("Afficher le Rapport Détaillé")
    report_btn.setFont(QFont("Arial", 16, QFont.Bold))
    report_btn.setFixedHeight(55)
    report_btn.setMinimumWidth(350)
    report_btn.setStyleSheet("""
        QPushButton {
            background-color: #222;
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 15px 30px;
            font-size: 16px;
            font-family: Arial;
        }
        QPushButton:hover {
            background-color: #444;
        }
    """)
    report_btn.setCursor(Qt.PointingHandCursor)
    report_btn.clicked.connect(request_password)
    buttons_layout.addWidget(report_btn, alignment=Qt.AlignCenter)
    
    # Bouton recommencer
    restart_btn = QPushButton("Recommencer le Test")
    restart_btn.setFont(QFont("Arial", 15))
    restart_btn.setFixedHeight(50)
    restart_btn.setMinimumWidth(350)
    restart_btn.setStyleSheet("""
        QPushButton {
            background-color: #ededed;
            color: #222;
            border: 2px solid #d1d1d1;
            border-radius: 8px;
            font-size: 15px;
            font-family: Arial;
        }
        QPushButton:hover {
            background-color: #d1d1d1;
            border-color: #b1b1b1;
        }
    """)
    restart_btn.setCursor(Qt.PointingHandCursor)
    restart_btn.clicked.connect(lambda: restart_test())
    buttons_layout.addWidget(restart_btn, alignment=Qt.AlignCenter)
    
    main_layout.addWidget(buttons_container)
    layout.addWidget(main_container, alignment=Qt.AlignCenter)
    
    return page

def main():
    """Fonction principale"""
    app = QApplication(sys.argv)
    
    if not load_questions():
        sys.exit(1)
    
    window = QMainWindow()
    window.setWindowTitle("Test de Compétence")
    window.setStyleSheet("QMainWindow { background: #fff; }")
    app_state['window'] = window
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    central_widget.setLayout(main_layout)
    
    app_state['stacked_widget'] = QStackedWidget()
    main_layout.addWidget(app_state['stacked_widget'])
    
    # Créer le timer
    app_state['timer'] = QTimer()
    app_state['timer'].timeout.connect(update_timer)
    
    app_state['form_page'] = create_form_page()
    app_state['instructions_page'] = create_instructions_page()
    app_state['test_page'] = create_test_page()
    app_state['thanks_page'] = create_thanks_page()
    
    app_state['stacked_widget'].addWidget(app_state['form_page'])
    app_state['stacked_widget'].addWidget(app_state['instructions_page'])
    app_state['stacked_widget'].addWidget(app_state['test_page'])
    app_state['stacked_widget'].addWidget(app_state['thanks_page'])
    
    app_state['stacked_widget'].setCurrentWidget(app_state['form_page'])
    
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
