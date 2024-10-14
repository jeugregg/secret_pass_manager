import streamlit as st

# Fonction à appeler lors du clic sur le bouton de soumission


def handle_form_submission():
    if accepte_conditions:
        st.write(f"Merci {nom} pour votre message : {message}")
        st.write(f"Genre : {genre}")
    else:
        st.error("Veuillez accepter les conditions avant de soumettre le formulaire.")


# Créer un formulaire
with st.form(key='my_form'):
    # Titre du formulaire
    st.title("Mon Formulaire")

    # Champ de texte simple
    nom = st.text_input("Votre nom : ")

    # Zone de texte multiligne
    message = st.text_area("Votre message : ", height=100)

    # Sélecteur déroulant
    genre = st.selectbox(
        "Genre",
        ("Homme", "Femme", "Autre")
    )

    # Checkbox
    global accepte_conditions
    accepte_conditions = st.checkbox('J\'accepte les conditions')

    # Ajouter un bouton pour soumettre le formulaire
    submit_button = st.form_submit_button(label='Soumettre')

# Appeler la fonction de gestionnaire de clic si le bouton est cliqué
if submit_button:
    handle_form_submission()
