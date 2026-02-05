import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,QHBoxLayout, QLabel, QRadioButton, QPushButton,QButtonGroup, QMessageBox, QFrame, QLineEdit, QFormLayout,QStackedWidget, QInputDialog, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
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
    'question_image_label': None,
    'reponses_image_label': None,
    'button_group': None,
    'radio_buttons': {},
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
        with open('questions_abstract.json', 'r', encoding='utf-8') as f:
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
    # Calculer le score
    score = sum(1 for i, ans in enumerate(app_state['user_answers']) if ans is not None and ans == app_state['questions'][i]['reponse_correcte'])
    total_questions = len(app_state['questions'])
    
    # Générer le PDF
    try:
        pdf_path = generate_test_report_pdf(
            app_state['candidat_info'],
            score,
            total_questions,
            "Raisonnement Abstrait"
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
    question_data = app_state['questions'][idx]
    
    app_state['question_label'].setText(f"Question {idx + 1} / {len(app_state['questions'])}")
    app_state['instruction_label'].setText("Choisissez la bonne réponse")
    
    question_img_path = question_data.get('image_question', '')
    if os.path.exists(question_img_path):
        pixmap = QPixmap(question_img_path)
        scaled_pixmap = pixmap.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app_state['question_image_label'].setPixmap(scaled_pixmap)
    
    reponses_img_path = question_data.get('image_reponses', '')
    if os.path.exists(reponses_img_path):
        pixmap = QPixmap(reponses_img_path)
        scaled_pixmap = pixmap.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app_state['reponses_image_label'].setPixmap(scaled_pixmap)
    
    saved_answer = app_state['user_answers'][idx]
    if saved_answer is not None and saved_answer != -1:
        radio = app_state['radio_buttons'].get(saved_answer)
        if radio:
            radio.setChecked(True)
    else:
        app_state['button_group'].setExclusive(False)
        for radio in app_state['radio_buttons'].values():
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
    unanswered = [i+1 for i, ans in enumerate(app_state['user_answers']) if ans is None or ans == -1]
    if unanswered:
        QMessageBox.warning(app_state['window'], "Questions non répondues",
                           f"Veuillez répondre à toutes les questions.\nQuestions: {', '.join(map(str, unanswered))}")
        return
    app_state['timer'].stop()
    app_state['stacked_widget'].setCurrentWidget(app_state['thanks_page'])
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
    score = sum(1 for i, ans in enumerate(app_state['user_answers']) if ans is not None and ans == app_state['questions'][i]['reponse_correcte'])
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
    layout.setContentsMargins(60, 60, 60, 60)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignCenter)

    title = QLabel("Rapport du Test Abstrait")
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
    app_state['user_answers'] = [None] * len(app_state['questions'])
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
        "Ce test évalue vos compétences de raisonnement abstrait",
        "Observez attentivement les motifs et les séquences",
        "Choisissez la réponse (A, B, C, D ou E) qui complète le mieux le motif",
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
    
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    page.setLayout(main_layout)
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("QScrollArea { border: none; background-color: white; }")
    main_layout.addWidget(scroll)
    
    scroll_content = QWidget()
    scroll_content.setStyleSheet("background-color: white;")
    scroll.setWidget(scroll_content)
    
    content_layout = QVBoxLayout()
    content_layout.setContentsMargins(40, 30, 40, 30)
    content_layout.setSpacing(25)
    scroll_content.setLayout(content_layout)
    
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
    app_state['instruction_label'].setAlignment(Qt.AlignCenter)
    app_state['instruction_label'].setStyleSheet("color: #444; background: transparent; padding: 10px;")
    content_layout.addWidget(app_state['instruction_label'])
    
    # Titre Question
    question_title = QLabel("Question :")
    question_title.setFont(QFont("Arial", 16, QFont.Bold))
    question_title.setAlignment(Qt.AlignCenter)
    question_title.setStyleSheet("color: #222; background: transparent; padding: 10px;")
    content_layout.addWidget(question_title)
    
    # Image question
    app_state['question_image_label'] = QLabel()
    app_state['question_image_label'].setAlignment(Qt.AlignCenter)
    app_state['question_image_label'].setStyleSheet("background: white; border-radius: 8px; padding: 10px;")
    app_state['question_image_label'].setMaximumHeight(400)
    app_state['question_image_label'].setScaledContents(False)
    content_layout.addWidget(app_state['question_image_label'])
    
    # Titre Options de réponse
    reponses_title = QLabel("Options de réponse (A, B, C, D, E) :")
    reponses_title.setFont(QFont("Arial", 16, QFont.Bold))
    reponses_title.setAlignment(Qt.AlignCenter)
    reponses_title.setStyleSheet("color: #222; background: transparent; padding: 10px;")
    content_layout.addWidget(reponses_title)
    
    # Image réponses
    app_state['reponses_image_label'] = QLabel()
    app_state['reponses_image_label'].setAlignment(Qt.AlignCenter)
    app_state['reponses_image_label'].setStyleSheet("background: white; border-radius: 8px; padding: 10px;")
    app_state['reponses_image_label'].setMaximumHeight(400)
    app_state['reponses_image_label'].setScaledContents(False)
    content_layout.addWidget(app_state['reponses_image_label'])
    
    # Zone de sélection A, B, C, D, E
    selection_wrapper = QHBoxLayout()
    selection_wrapper.addStretch()
    
    selection_container = QWidget()
    selection_layout = QHBoxLayout(selection_container)
    selection_layout.setSpacing(24)
    selection_layout.setContentsMargins(0, 0, 0, 0)
    
    app_state['button_group'] = QButtonGroup()
    
    radio_style = """
        QRadioButton {
            font-size: 16px;
            color: #222;
            padding: 18px 32px;
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
    
    for letter in ['A', 'B', 'C', 'D', 'E']:
        radio = QRadioButton(letter)
        radio.setFont(QFont("Arial", 16, QFont.Bold))
        radio.setStyleSheet(radio_style)
        radio.setCursor(Qt.PointingHandCursor)
        radio.toggled.connect(lambda checked, l=letter: on_answer_selected(l) if checked else None)
        app_state['button_group'].addButton(radio)
        app_state['radio_buttons'][letter] = radio
        selection_layout.addWidget(radio)
    
    selection_wrapper.addWidget(selection_container)
    selection_wrapper.addStretch()
    content_layout.addLayout(selection_wrapper)
    content_layout.addStretch()
    
    # Boutons de navigation
    nav_container = QWidget()
    nav_container.setStyleSheet("background-color: white;")
    nav_layout = QHBoxLayout(nav_container)
    nav_layout.setContentsMargins(0, 15, 0, 15)
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
        "Merci d'avoir complété ce test de raisonnement abstrait.\n\n"
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
    
    data = load_questions()
    if not data:
        sys.exit(1)
    
    app_state['questions'] = data.get('questions', [])
    if not app_state['questions']:
        QMessageBox.critical(None, "Erreur", "Aucune question trouvée dans le fichier JSON.")
        sys.exit(1)
    
    # Initialiser les réponses utilisateur
    app_state['user_answers'] = [None] * len(app_state['questions'])
    
    window = QMainWindow()
    window.setWindowTitle("Test de Raisonnement Abstrait")
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
