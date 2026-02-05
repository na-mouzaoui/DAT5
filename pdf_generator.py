"""Module pour générer les rapports PDF des tests"""
import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def get_classification(percentage):
    """Déterminer la classification selon le pourcentage"""
    if percentage >= 90:
        return "Excellent", colors.HexColor("#4CAF50")
    elif percentage >= 75:
        return "Bon", colors.HexColor("#8BC34A")
    elif percentage >= 60:
        return "Moyen", colors.HexColor("#FFC107")
    elif percentage >= 40:
        return "Mauvais", colors.HexColor("#FF9800")
    else:
        return "Médiocre", colors.HexColor("#f44336")

def generate_test_report_pdf(candidat_info, score, total_questions, test_type="Calcul Numérique", output_dir=None):
    """Générer un rapport PDF simplifié"""
    # Créer le nom du fichier
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier = f"Rapport_{candidat_info['nom']}_{candidat_info['prenom']}_{timestamp}.pdf"
    target_dir = output_dir or os.getcwd()
    os.makedirs(target_dir, exist_ok=True)
    chemin_fichier = os.path.join(target_dir, nom_fichier)
    
    # Créer le PDF
    c = canvas.Canvas(chemin_fichier, pagesize=A4)
    width, height = A4
    
    # Titre
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 2*cm, f"Rapport de Test de {test_type}")
    
    # Ligne de séparation
    c.setStrokeColor(colors.HexColor("#222"))
    c.setLineWidth(2)
    c.line(2*cm, height - 2.8*cm, width - 2*cm, height - 2.8*cm)
    
    # Informations du candidat
    y = height - 4.5*cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, "Informations du Candidat")
    
    y -= 1*cm
    c.setFont("Helvetica", 12)
    c.drawString(2.5*cm, y, f"Nom: {candidat_info['nom']}")
    y -= 0.7*cm
    c.drawString(2.5*cm, y, f"Prénom: {candidat_info['prenom']}")
    y -= 0.7*cm
    c.drawString(2.5*cm, y, f"Âge: {candidat_info['age']}")
    y -= 0.7*cm
    c.drawString(2.5*cm, y, f"Sexe: {candidat_info['sexe']}")
    y -= 0.7*cm
    c.drawString(2.5*cm, y, f"Date: {candidat_info['date']}")
    
    # Résultats
    y -= 1.5*cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, "Résultats")
    
    # Calculer le pourcentage
    percentage = (score / total_questions) * 100
    classification, color = get_classification(percentage)
    
    y -= 1.2*cm
    c.setFont("Helvetica", 14)
    c.drawString(2.5*cm, y, f"Score: {score} / {total_questions}")
    
    y -= 0.9*cm
    c.drawString(2.5*cm, y, f"Pourcentage: {percentage:.1f}%")
    
    # Classification avec couleur
    y -= 1.2*cm
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(color)
    c.drawString(2.5*cm, y, f"Classification: {classification}")
    
    # Pied de page
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(width/2, 1.5*cm, f"Rapport généré le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
    c.drawCentredString(width/2, 1*cm, "Document confidentiel - Ne pas divulguer sans autorisation")
    
    # Sauvegarder le PDF
    c.save()
    
    return chemin_fichier
