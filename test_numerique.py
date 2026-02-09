import sys
import json
import traceback
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,QHBoxLayout, QLabel, QRadioButton, QPushButton,QButtonGroup, QMessageBox, QFrame, QLineEdit, QFormLayout,QStackedWidget, QInputDialog, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
import datetime
try:
    from pdf_generator import generate_test_report_pdf
    PDF_AVAILABLE = True
except Exception as e:
    print(f"Erreur lors de l'import du générateur PDF: {e}")
    PDF_AVAILABLE = False

class TestNumeriqueModern(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            print("Initialisation de la fenêtre...")
            self.setWindowTitle("Test de Calcul Numérique")
            self.setStyleSheet("QMainWindow { background: #fff; }")
            print("Chargement des questions...")
            self.load_questions()
            self.current_question = 0
            self.user_answers = [-1] * len(self.questions)
            self.candidat_info = {}
            print(f"{len(self.questions)} questions chargées avec succès")
        
            self.time_remaining = 20 * 60
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_timer)
            self.timer_label = None
            
            print("Initialisation de l'interface...")
            self.init_ui()
            print("Interface initialisée avec succès")
        except Exception as e:
            print(f"ERREUR lors de l'initialisation: {e}")
            traceback.print_exc()
            QMessageBox.critical(None, "Erreur d'initialisation", 
                               f"Une erreur s'est produite lors de l'initialisation:\n{str(e)}")
            sys.exit(1)
    
    def update_timer(self):
        """Mettre à jour le compte à rebours"""
        self.time_remaining -= 1
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.setText(f"Temps restant: {minutes:02d}:{seconds:02d}")
        
        if self.time_remaining <= 300:
            self.timer_label.setStyleSheet("color: #f44336; font-size: 18px; font-weight: bold; padding: 10px;")
        elif self.time_remaining <= 600:
            self.timer_label.setStyleSheet("color: #FF9800; font-size: 18px; font-weight: bold; padding: 10px;")
        
        if self.time_remaining <= 0:
            self.time_expired()
    
    def time_expired(self):
        """Gérer l'expiration du temps"""
        self.timer.stop()
        QMessageBox.information(self, "Temps écoulé", "Le temps imparti est écoulé. Le test sera soumis automatiquement.")
        self.stacked_widget.setCurrentWidget(self.thanks_page)
        self.generate_pdf_report()
    
    def generate_pdf_report(self):
        """Générer le rapport PDF"""
        score = sum(1 for i, q in enumerate(self.questions)
                    if self.user_answers[i] == q['reponse_correcte'])
        total_questions = len(self.questions)
        
        if not PDF_AVAILABLE:
            QMessageBox.warning(self, "PDF non disponible", 
                              "La génération de PDF n'est pas disponible.\n"
                              "Installez reportlab avec: pip install reportlab")
            return
        
        try:
            print("Génération du PDF...")
            pdf_path = generate_test_report_pdf(
                self.candidat_info,
                score,
                total_questions,
                "Calcul Numérique"
            )
            print(f"PDF généré: {pdf_path}")
            QMessageBox.information(self, "PDF généré", f"Le rapport a été téléchargé avec succès:\n{pdf_path}")
        except Exception as e:
            print(f"Erreur PDF: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du PDF:\n{str(e)}")
    
    def show_report(self):
        """Afficher le rapport de résultats"""
        score = sum(1 for i, q in enumerate(self.questions)
                    if self.user_answers[i] == q['reponse_correcte'])
        percentage = (score / len(self.questions)) * 100
        
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
        
        if self.report_page:
            self.stacked_widget.removeWidget(self.report_page)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        layout.setContentsMargins(80, 80, 80, 80)

        title = QLabel("Rapport de Test de Calcul Numérique")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = self.candidat_info
        info_label = QLabel(f"{info.get('prenom', '')} {info.get('nom', '')} — {info.get('age', '')} ans — {info.get('sexe', '')} — {info.get('date', '')}")
        info_label.setFont(QFont("Arial", 14))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        result_label = QLabel(f"Résultat : {percentage:.1f}% ({score}/{len(self.questions)})")
        result_label.setFont(QFont("Arial", 20))
        result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(result_label)

        class_label = QLabel(f"Classification : {classification}")
        class_label.setFont(QFont("Arial", 20, QFont.Bold))
        class_label.setAlignment(Qt.AlignCenter)
        class_label.setStyleSheet(f"color: {class_color};")
        layout.addWidget(class_label)

        close_btn = QPushButton("Fermer")
        close_btn.setFixedHeight(40)
        close_btn.setMinimumWidth(160)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.report_page = page
        self.stacked_widget.addWidget(page)
        self.stacked_widget.setCurrentWidget(page)

    def start_test(self):
        self.stacked_widget.setCurrentWidget(self.test_page)
        self.time_remaining = 20 * 60
        self.timer.start(1000)
        if hasattr(self, 'display_question'):
            self.display_question()

    def validate_form(self):
        if not self.nom_input.text().strip():
            QMessageBox.warning(self, "Champ requis", "Veuillez entrer votre nom.")
            return
        if not self.prenom_input.text().strip():
            QMessageBox.warning(self, "Champ requis", "Veuillez entrer votre prénom.")
            return
        if not self.age_input.text().strip():
            QMessageBox.warning(self, "Champ requis", "Veuillez entrer votre âge.")
            return
        if not self.homme_radio.isChecked() and not self.femme_radio.isChecked():
            QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner votre sexe.")
            return
        sexe = "Homme" if self.homme_radio.isChecked() else "Femme"
        self.candidat_info = {
            'nom': self.nom_input.text().strip(),
            'prenom': self.prenom_input.text().strip(),
            'age': self.age_input.text().strip(),
            'sexe': sexe,
            'date': datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        self.stacked_widget.setCurrentWidget(self.instructions_page)

    def load_questions(self):
        try:
            print("Ouverture du fichier questions_numerique.json...")
            with open('questions_numerique.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.instruction = data.get('instruction', 'Choisissez la bonne réponse')
            self.questions = data.get('questions', [])
            if not self.questions:
                raise ValueError("Aucune question trouvée dans le fichier JSON.")
            print(f"Questions chargées: {len(self.questions)}")
        except FileNotFoundError:
            error_msg = "Le fichier 'questions_numerique.json' est introuvable."
            print(f"ERREUR: {error_msg}")
            QMessageBox.critical(None, "Erreur", error_msg)
            sys.exit(1)
        except json.JSONDecodeError as e:
            error_msg = f"Erreur de format JSON: {str(e)}"
            print(f"ERREUR: {error_msg}")
            QMessageBox.critical(None, "Erreur", error_msg)
            sys.exit(1)
        except Exception as e:
            error_msg = f"Erreur lors du chargement des questions: {str(e)}"
            print(f"ERREUR: {error_msg}")
            traceback.print_exc()
            QMessageBox.critical(None, "Erreur", error_msg)
            sys.exit(1)

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background: #fff;")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        self.form_page = self.create_form_page()
        self.instructions_page = self.create_instructions_page()
        self.test_page = self.create_test_page()
        self.thanks_page = self.create_thanks_page()
        self.report_page = None
        self.stacked_widget.addWidget(self.form_page)
        self.stacked_widget.addWidget(self.instructions_page)
        self.stacked_widget.addWidget(self.test_page)
        self.stacked_widget.addWidget(self.thanks_page)
        self.stacked_widget.setCurrentWidget(self.form_page)

    def create_form_page(self):
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
        label_style = "font-size: 15px; color: #222; font-weight: 500; padding: 5px 0; font-family: Arial, Helvetica, Segoe UI, sans-serif;"
        input_style = """
            QLineEdit {
                padding: 10px;
                border: 1px solid #d1d1d1;
                border-radius: 5px;
                font-size: 15px;
                background: #fafafa;
                min-width: 320px;
                color: #222;
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
            }
            QLineEdit:focus {
                border-color: #222;
                background: #fff;
                outline: none;
            }
        """
        self.nom_input = QLineEdit()
        self.nom_input.setStyleSheet(input_style)
        nom_label = QLabel("Nom")
        nom_label.setStyleSheet(label_style)
        form_layout.addRow(nom_label, self.nom_input)
        self.prenom_input = QLineEdit()
        self.prenom_input.setStyleSheet(input_style)
        prenom_label = QLabel("Prénom")
        prenom_label.setStyleSheet(label_style)
        form_layout.addRow(prenom_label, self.prenom_input)
        self.age_input = QLineEdit()
        self.age_input.setStyleSheet(input_style)
        age_label = QLabel("Âge")
        age_label.setStyleSheet(label_style)
        form_layout.addRow(age_label, self.age_input)
        sexe_label = QLabel("Sexe")
        sexe_label.setStyleSheet(label_style)
        self.sexe_group = QButtonGroup()
        radio_style = """
            QRadioButton {
                font-size: 15px;
                color: #222;
                padding: 8px 24px 8px 0;
                border-radius: 5px;
                background: transparent;
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
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
        self.homme_radio = QRadioButton("Homme")
        self.homme_radio.setStyleSheet(radio_style)
        self.sexe_group.addButton(self.homme_radio)
        sexe_row_layout.addWidget(self.homme_radio)
        self.femme_radio = QRadioButton("Femme")
        self.femme_radio.setStyleSheet(radio_style)
        self.sexe_group.addButton(self.femme_radio)
        sexe_row_layout.addWidget(self.femme_radio)
        sexe_row_layout.addStretch()
        form_layout.addRow(sexe_label, sexe_row)
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        main_layout.addSpacing(20)
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
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.clicked.connect(self.validate_form)
        main_layout.addWidget(next_btn, alignment=Qt.AlignCenter)
        layout.addWidget(main_container, alignment=Qt.AlignCenter)
        return page

    def create_instructions_page(self):
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
            "Ce test évalue vos compétences en calcul numérique",
            "Prenez le temps nécessaire pour chaque opération",
            "Choisissez le résultat correct",
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
        layout.addSpacing(20)
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
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.clicked.connect(self.start_test)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(start_btn)
        button_layout.addStretch()
        layout.addWidget(button_container)
        return page

    def create_test_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(0)

        # crée des placeholders pour éviter les connexions avant définition
        self.previous_question = lambda: None
        self.next_question = lambda: None
        self.submit_test = lambda: None
        self.on_answer_selected = lambda idx: None
        self.display_question = lambda: None

        # ===== PARTIE 1/5 : Header (Timer + Question + Instruction) =====
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        header_layout.setAlignment(Qt.AlignTop)
        
        # Timer
        self.timer_label = QLabel("Temps restant: 20:00")
        self.timer_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold; padding: 5px;")
        header_layout.addWidget(self.timer_label)

        # Titre question
        self.question_label = QLabel()
        self.question_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setStyleSheet("color: #111; background: transparent; padding: 5px;")
        header_layout.addWidget(self.question_label)

        # Consigne
        self.instruction_label = QLabel(self.instruction)
        self.instruction_label.setFont(QFont("Arial", 14))
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("color: #444; background: transparent; padding: 5px;")
        header_layout.addWidget(self.instruction_label)
        
        header_layout.addStretch()
        layout.addWidget(header_container, 1)  # 1/5 de l'espace

        # ===== PARTIES 2-3/5 : Opération/Phrase au milieu =====
        self.operation_container = QWidget()
        self.operation_layout = QVBoxLayout(self.operation_container)
        self.operation_layout.setAlignment(Qt.AlignCenter)
        self.operation_layout.setSpacing(5)
        self.operation_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.operation_container, 2)  # 2/5 de l'espace

        # ===== PARTIE 4/5 : Propositions =====
        propositions_wrapper = QWidget()
        propositions_wrapper_layout = QVBoxLayout(propositions_wrapper)
        propositions_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        propositions_wrapper_layout.setSpacing(0)
        propositions_wrapper_layout.setAlignment(Qt.AlignCenter)
        
        self.propositions_container = QWidget()
        self.propositions_layout = QHBoxLayout(self.propositions_container)
        self.propositions_layout.setSpacing(24)
        self.propositions_layout.setContentsMargins(0, 0, 0, 0)
        self.button_group = QButtonGroup()
        self.radio_buttons = []
        radio_style = """
            QRadioButton {
                font-size: 16px;
                color: #222;
                padding: 18px 32px;
                border-radius: 8px;
                background: #fafafa;
                border: 2px solid transparent;
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
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
        for i in range(5):
            radio = QRadioButton()
            radio.setFont(QFont("Arial", 16))
            radio.setStyleSheet(radio_style)
            radio.setCursor(Qt.PointingHandCursor)
            radio.toggled.connect(lambda checked, idx=i: self.on_answer_selected(idx) if checked else None)
            self.button_group.addButton(radio, i)
            self.radio_buttons.append(radio)
            self.propositions_layout.addWidget(radio)
        
        propositions_wrapper_layout.addWidget(self.propositions_container)
        layout.addWidget(propositions_wrapper, 1)  # 1/5 de l'espace

        # ===== PARTIE 5/5 : Navigation =====
        nav_wrapper = QWidget()
        nav_wrapper_layout = QVBoxLayout(nav_wrapper)
        nav_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        nav_wrapper_layout.setSpacing(0)
        nav_wrapper_layout.setAlignment(Qt.AlignBottom)
        
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(24)
        self.prev_button = QPushButton("← Précédent")
        self.prev_button.setFont(QFont("Arial", 14))
        self.prev_button.setFixedHeight(40)
        self.prev_button.setMinimumWidth(140)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: #fff;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.clicked.connect(lambda: self.previous_question())
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        self.next_button = QPushButton("Suivant →")
        self.next_button.setFont(QFont("Arial", 14))
        self.next_button.setFixedHeight(40)
        self.next_button.setMinimumWidth(140)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: #fff;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        self.next_button.setCursor(Qt.PointingHandCursor)
        self.next_button.clicked.connect(lambda: self.next_question())
        nav_layout.addWidget(self.next_button)
        self.submit_button = QPushButton("Soumettre")
        self.submit_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.submit_button.setFixedHeight(40)
        self.submit_button.setMinimumWidth(160)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: #fff;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
            }
            QPushButton:hover {
                background-color: #222;
            }
        """)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.clicked.connect(lambda: self.submit_test())
        self.submit_button.hide()
        nav_layout.addWidget(self.submit_button)
        
        nav_wrapper_layout.addWidget(nav_container)
        layout.addWidget(nav_wrapper, 1)  # 1/5 de l'espace

        # Pour afficher dynamiquement les opérations
        self.operation_labels = []

        # Méthodes pour navigation et affichage
        def display_question():
            self.question_label.setText(f"Question {self.current_question + 1}/{len(self.questions)}")
            # Nettoyer opération
            for label in self.operation_labels:
                label.deleteLater()
            self.operation_labels.clear()
            question = self.questions[self.current_question]
            
            # Affichage opération selon le type
            if question.get('type') == 'vertical':
                label1 = QLabel(question['ligne1'])
                label1.setFont(QFont("Courier New", 28, QFont.Bold))
                label1.setAlignment(Qt.AlignRight)
                label1.setStyleSheet("color: #222; background: transparent; padding: 3px 20px;")
                self.operation_layout.addWidget(label1)
                self.operation_labels.append(label1)
                label2 = QLabel(question['ligne2'])
                label2.setFont(QFont("Courier New", 28, QFont.Bold))
                label2.setAlignment(Qt.AlignRight)
                label2.setStyleSheet("color: #222; background: transparent; padding: 3px 20px;")
                self.operation_layout.addWidget(label2)
                self.operation_labels.append(label2)
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Plain)
                separator.setStyleSheet("background-color: #222;")
                separator.setFixedHeight(2)
                separator.setMinimumWidth(100)
                self.operation_layout.addWidget(separator)
                self.operation_labels.append(separator)
                label_result = QLabel(question['ligne_resultat'])
                label_result.setFont(QFont("Courier New", 28, QFont.Bold))
                label_result.setAlignment(Qt.AlignRight)
                label_result.setStyleSheet("color: #222; background: transparent; padding: 3px 20px;")
                self.operation_layout.addWidget(label_result)
                self.operation_labels.append(label_result)
            elif question.get('type') == 'racine' or question.get('type') == 'phrase':
                label = QLabel(question['phrase'])
                label.setFont(QFont("Arial", 24, QFont.Bold))
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("color: #222; background: transparent; padding: 5px;")
                self.operation_layout.addWidget(label)
                self.operation_labels.append(label)
            elif question.get('type') == 'image':
                # Afficher la question textuelle
                phrase_label = QLabel(question['phrase'])
                phrase_label.setFont(QFont("Arial", 20, QFont.Bold))
                phrase_label.setAlignment(Qt.AlignCenter)
                phrase_label.setStyleSheet("color: #222; background: transparent; padding: 10px;")
                self.operation_layout.addWidget(phrase_label)
                self.operation_labels.append(phrase_label)
                
                # Afficher l'image
                image_path = question.get('image_path', '')
                if image_path and os.path.exists(image_path):
                    image_label = QLabel()
                    pixmap = QPixmap(image_path)
                    # Redimensionner l'image si nécessaire (max 900x600)
                    if pixmap.width() > 900 or pixmap.height() > 600:
                        pixmap = pixmap.scaled(900, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignCenter)
                    image_label.setStyleSheet("padding: 15px;")
                    self.operation_layout.addWidget(image_label)
                    self.operation_labels.append(image_label)
                else:
                    error_label = QLabel(f"Image non trouvée: {image_path}")
                    error_label.setFont(QFont("Arial", 14))
                    error_label.setAlignment(Qt.AlignCenter)
                    error_label.setStyleSheet("color: #f44336; padding: 10px;")
                    self.operation_layout.addWidget(error_label)
                    self.operation_labels.append(error_label)
            elif question.get('type') == 'operations_verticales':
                # Afficher la question textuelle
                phrase_label = QLabel(question['phrase'])
                phrase_label.setFont(QFont("Arial", 18, QFont.Bold))
                phrase_label.setAlignment(Qt.AlignCenter)
                phrase_label.setStyleSheet("color: #222; background: transparent; padding: 5px;")
                self.operation_layout.addWidget(phrase_label)
                self.operation_labels.append(phrase_label)
                
                # Ajouter un petit espacement
                self.operation_layout.addSpacing(5)
                
                # Créer un conteneur pour les opérations verticales
                ops_container = QWidget()
                ops_layout = QHBoxLayout(ops_container)
                ops_layout.setSpacing(40)
                ops_layout.setContentsMargins(0, 0, 0, 0)
                
                letters = ['A', 'B', 'C', 'D', 'E']
                for i, op_data in enumerate(question['propositions'][:5]):
                    # Conteneur pour chaque opération
                    op_col = QWidget()
                    op_col_layout = QVBoxLayout(op_col)
                    op_col_layout.setSpacing(0)
                    op_col_layout.setAlignment(Qt.AlignCenter)
                    
                    # Conteneur pour l'opération verticale
                    op_widget = QWidget()
                    op_widget.setStyleSheet("background: white;")
                    op_inner_layout = QVBoxLayout(op_widget)
                    op_inner_layout.setSpacing(0)
                    op_inner_layout.setContentsMargins(10, 0, 10, 0)
                    
                    # Afficher l'opération verticale
                    ligne1_lbl = QLabel(op_data['ligne1'])
                    ligne1_lbl.setFont(QFont("Courier New", 24, QFont.Bold))
                    ligne1_lbl.setAlignment(Qt.AlignRight)
                    ligne1_lbl.setStyleSheet("color: #222; background: transparent;")
                    op_inner_layout.addWidget(ligne1_lbl)
                    
                    ligne2_lbl = QLabel(op_data['ligne2'])
                    ligne2_lbl.setFont(QFont("Courier New", 24, QFont.Bold))
                    ligne2_lbl.setAlignment(Qt.AlignRight)
                    ligne2_lbl.setStyleSheet("color: #222; background: transparent;")
                    op_inner_layout.addWidget(ligne2_lbl)
                    
                    # Trait horizontal
                    sep = QFrame()
                    sep.setFrameShape(QFrame.HLine)
                    sep.setFrameShadow(QFrame.Plain)
                    sep.setStyleSheet("background-color: #222;")
                    sep.setFixedHeight(2)
                    sep.setMinimumWidth(60)
                    op_inner_layout.addWidget(sep)
                    
                    result_lbl = QLabel(op_data['ligne_resultat'])
                    result_lbl.setFont(QFont("Courier New", 24, QFont.Bold))
                    result_lbl.setAlignment(Qt.AlignRight)
                    result_lbl.setStyleSheet("color: #222; background: transparent;")
                    op_inner_layout.addWidget(result_lbl)
                    
                    op_col_layout.addWidget(op_widget)
                    op_col_layout.addSpacing(3)
                    
                    ops_layout.addWidget(op_col)
                
                self.operation_layout.addWidget(ops_container)
                self.operation_labels.append(ops_container)
                
                # Configurer les boutons radio avec les lettres (garder les boutons dans propositions_container)
                self.propositions_container.show()
                self.button_group.setExclusive(False)
                for i, r in enumerate(self.radio_buttons):
                    r.setChecked(False)
                    r.setText(letters[i])
                    r.setFont(QFont("Arial", 16, QFont.Bold))
                self.button_group.setExclusive(True)
                
                # Restaurer la réponse précédente si elle existe
                if self.user_answers[self.current_question] != -1:
                    self.radio_buttons[self.user_answers[self.current_question]].setChecked(True)
                
                # Gérer la navigation pour ce type de question
                self.prev_button.setEnabled(self.current_question > 0)
                if self.current_question == len(self.questions) - 1:
                    self.next_button.hide()
                    self.submit_button.show()
                else:
                    self.next_button.show()
                    self.submit_button.hide()
                
                return  # Sortir tôt
            
            # Affichage propositions normales
            self.propositions_container.show()
            self.button_group.setExclusive(False)
            for r in self.radio_buttons:
                r.setChecked(False)
                r.setFont(QFont("Arial", 16))  # Réinitialiser la police
            self.button_group.setExclusive(True)
            
            for i, (radio, option) in enumerate(zip(self.radio_buttons, question['propositions'])):
                radio.setText(str(option))
            
            # Restaurer la réponse précédente si elle existe
            if self.user_answers[self.current_question] != -1:
                self.radio_buttons[self.user_answers[self.current_question]].setChecked(True)
            
            # Navigation
            self.prev_button.setEnabled(self.current_question > 0)
            if self.current_question == len(self.questions) - 1:
                self.next_button.hide()
                self.submit_button.show()
            else:
                self.next_button.show()
                self.submit_button.hide()

        self.display_question = display_question

        def on_answer_selected(index):
            self.user_answers[self.current_question] = index

        self.on_answer_selected = on_answer_selected

        def previous_question():
            if self.current_question > 0:
                self.current_question -= 1
                self.display_question()

        self.previous_question = previous_question

        def next_question():
            if self.current_question < len(self.questions) - 1:
                self.current_question += 1
                self.display_question()

        self.next_question = next_question

        def submit_test():
            unanswered = [i+1 for i, ans in enumerate(self.user_answers) if ans == -1]
            if unanswered:
                QMessageBox.warning(self, "Questions non répondues", f"Veuillez répondre à toutes les questions avant de soumettre. Questions: {', '.join(map(str, unanswered))}")
                return
            # Arrêter le timer
            self.timer.stop()
            # Afficher page de remerciement
            self.stacked_widget.setCurrentWidget(self.thanks_page)
            # Générer le PDF automatiquement
            self.generate_pdf_report()

        self.submit_test = submit_test

        return page

    def create_thanks_page(self):
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
        
        # Espacement
        main_layout.addSpacing(30)
        
        # Message de remerciement
        thanks_msg = QLabel(
            "Merci d'avoir complété ce test de calcul numérique.\n\n"
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
        
        # Espacement
        main_layout.addSpacing(30)
        
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
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        report_btn.setCursor(Qt.PointingHandCursor)
        report_btn.clicked.connect(self.request_password)
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
                font-family: Arial, Helvetica, Segoe UI, sans-serif;
            }
            QPushButton:hover {
                background-color: #d1d1d1;
                border-color: #b1b1b1;
            }
        """)
        restart_btn.setCursor(Qt.PointingHandCursor)
        
        def restart_from_thanks():
            self.current_question = 0
            self.user_answers = [-1] * len(self.questions)
            self.nom_input.clear()
            self.prenom_input.clear()
            self.age_input.clear()
            self.homme_radio.setChecked(False)
            self.femme_radio.setChecked(False)
            self.stacked_widget.setCurrentWidget(self.form_page)
        
        restart_btn.clicked.connect(restart_from_thanks)
        buttons_layout.addWidget(restart_btn, alignment=Qt.AlignCenter)
        
        main_layout.addWidget(buttons_container)
        layout.addWidget(main_container, alignment=Qt.AlignCenter)
        
        return page

    def request_password(self):
        """Demander le mot de passe pour le rapport"""
        password, ok = QInputDialog.getText(self, "Mot de passe requis",
                                           "Entrez le mot de passe:", QLineEdit.Password)
        if ok:
            if password == "dadou76":
                self.show_report()
            else:
                QMessageBox.warning(self, "Mot de passe incorrect",
                                  "Le mot de passe est incorrect.")
                self.request_password()


def main():
    try:
        print("Démarrage de l'application...")
        app = QApplication(sys.argv)
        print("QApplication créée")
        window = TestNumeriqueModern()
        print("Fenêtre créée")
        window.showMaximized()
        print("Fenêtre affichée")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"ERREUR FATALE: {e}")
        traceback.print_exc()
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)

if __name__ == "__main__":
    main()
