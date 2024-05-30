import streamlit as st
import requests
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title=":bank: Prédiction de solvabilité client",
    page_icon=":bank:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gestion de la connexion
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login(username, password):
    response = requests.post("https://backhome-gs1u.onrender.com/login", json={'username': username, 'password': password})
    if response.status_code == 200:
        st.session_state.logged_in = True
        st.session_state.username = username
    else:
        st.error("Nom d'utilisateur ou mot de passe incorrect")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None

# Page de connexion
if not st.session_state.logged_in:
    st.title("Page de connexion")
    with st.form(key='login_form'):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        login_button = st.form_submit_button(label='Se connecter')

    if login_button:
        login(username, password)

else:
    # Gestion de la navigation
    page = st.sidebar.selectbox("Choisissez la page", ["Prédiction", "Détails de la Requête", "Historique des Requêtes"])
    st.sidebar.button("Se déconnecter", on_click=logout)

  


    if page == "Prédiction":
        st.title(":classical_building: Prédiction de solvabilité")

        with st.form(key='my_form'):
            st.subheader('Type de contrat')
            NAME_CONTRACT_TYPE = st.selectbox('Sélectionnez le type de contrat:', ['Cash Loans', 'Revolving Loans'])

            st.subheader('Véhiculé')
            FLAG_OWN_CAR = st.selectbox('Êtes-vous le propriétaire de votre véhicule ?', ['Oui', 'Non'])

            st.subheader('Patrimoine')
            FLAG_OWN_REALTY = st.selectbox('Êtes-vous propriétaire ?', ['Oui','Non'])

            st.subheader("Nombre d'enfants")
            CNT_CHILDREN = st.number_input("Nombre d'enfants", min_value=0, max_value=10, step=1)
            st.write("Nombre d'enfants", CNT_CHILDREN)

            st.subheader('Revenus total')
            AMT_INCOME_TOTAL = st.number_input("Revenus total", min_value=0, max_value=1000000000)
            st.write("Revenu total", AMT_INCOME_TOTAL)

            st.subheader('Montant Credit')
            AMT_CREDIT_x = st.number_input("Montant du crédit", min_value=1000, max_value=1000000000)
            st.write("Montant du crédit", AMT_CREDIT_x)

            st.subheader('Période de crédit')
            periode_credit = st.number_input("Période de crédit", min_value=1, max_value=60, step=1)
            st.write("Période de crédit", periode_credit)

            st.subheader('Annuité')
            AMT_ANNUITY_x = AMT_CREDIT_x / periode_credit
            st.write("Montant de l'annuité", AMT_ANNUITY_x)

            st.subheader('Montant bien voulu')
            AMT_GOODS_PRICE = st.number_input("Montant bien voulu", min_value=1000.0, max_value=100000000.0, step=500.0)
            st.write("Montant du bien voulu", AMT_GOODS_PRICE)

            st.subheader('Âge')
            DAYS_BIRTH = st.number_input("Âge client", min_value=18, max_value=90, step=1)
            st.write("Âge", DAYS_BIRTH)

            st.subheader('Ancienneté professionnelle')
            DAYS_EMPLOYED = st.number_input("Ancienneté professionnelle", min_value=0, max_value=50, step=1)
            st.write("Ancienneté professionnelle", DAYS_EMPLOYED)

           # st.subheader("Famille")
           # CNT_FAM_MEMBERS = st.number_input("Membre foyer", min_value=0, max_value=10, step=1)
           # st.write("Nombre de personnes dans le foyer", CNT_FAM_MEMBERS)

            st.subheader("COT1")
            EXT_SOURCE_1 = st.number_input("COT1", min_value=0.0, max_value=1.0, step=0.001)
            st.write("COT1", EXT_SOURCE_1)

            #st.subheader("COT2")
            #EXT_SOURCE_2 = st.number_input("COT2", min_value=0.0, max_value=1.0, step=0.001)
            #st.write("COT2", EXT_SOURCE_2)

           # st.subheader("COT3")
           # EXT_SOURCE_3 = st.number_input("COT3", min_value=0.00000, max_value=1.00000, step=0.00001)
           # st.write("COT3", EXT_SOURCE_3)

            submit_button = st.form_submit_button(label='Prédire')

        if submit_button:
            data = {
                'NAME_CONTRACT_TYPE': NAME_CONTRACT_TYPE,
                'FLAG_OWN_CAR': FLAG_OWN_CAR,
                'FLAG_OWN_REALTY': FLAG_OWN_REALTY,
                'CNT_CHILDREN':CNT_CHILDREN,
                'AMT_INCOME_TOTAL': AMT_INCOME_TOTAL,
                'AMT_CREDIT_x': AMT_CREDIT_x,
                'AMT_ANNUITY_x': AMT_ANNUITY_x,
                'AMT_GOODS_PRICE': AMT_GOODS_PRICE,
                'DAYS_BIRTH': DAYS_BIRTH,
                'DAYS_EMPLOYED': DAYS_EMPLOYED,
                #'CNT_FAM_MEMBERS': CNT_FAM_MEMBERS,
                'EXT_SOURCE_1': EXT_SOURCE_1,
                #'EXT_SOURCE_2': EXT_SOURCE_2,
                #'EXT_SOURCE_3': EXT_SOURCE_3
            }

            # Afficher la requête JSON envoyée
            st.session_state.request_data = data

            response = requests.post("https://backhome-gs1u.onrender.com/predict", json=data)
            result = response.json()

            # Afficher la réponse JSON reçue
            st.session_state.response_data = result

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Probabilité de Remboursement")
                rounded_prediction = round(result['probability'] * 100, 2)
                st.metric("", f"{rounded_prediction}%")

            with col2:
                if result['decision'] == 'approved':
                    prediction_text = "Crédit accordé"
                    st.success(prediction_text)
                else:
                    prediction_text = "Crédit refusé"
                    st.error(prediction_text)

    elif page == "Détails de la Requête":
        st.title("Détails de la Requête et de la Réponse")

        if 'request_data' in st.session_state:
            st.subheader("Requête JSON envoyée")
            st.json(st.session_state.request_data)
        else:
            st.warning("Aucune requête envoyée.")

        if 'response_data' in st.session_state:
            st.subheader("Réponse JSON reçue")
            st.json(st.session_state.response_data)
        else:
            st.warning("Aucune réponse reçue.")

    elif page == "Historique des Requêtes":
        st.title("Historique des Requêtes")

        response = requests.get("https://backhome-gs1u.onrender.com/requests")
        if response.status_code == 200:
            requests_data = response.json()
            df = pd.DataFrame(requests_data, columns=['ID', 'Request Data', 'Prediction', 'Decision'])
            st.dataframe(df)
        else:
            st.error("Erreur lors de la récupération des données.")
