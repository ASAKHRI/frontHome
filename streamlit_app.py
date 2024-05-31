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
    #response = requests.post("http://localhost:5000/login", json={'username': username, 'password': password})

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
    page = st.sidebar.selectbox("Choisissez la page", ["Prédiction", "Informations sur les Tables", "Historique des Requêtes"])
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

            st.subheader('Revenus total')
            AMT_INCOME_TOTAL = st.number_input("Revenus total", min_value=0, max_value=1000000000)

            st.subheader('Montant Credit')
            AMT_CREDIT_x = st.number_input("Montant du crédit", min_value=1000, max_value=1000000000)

            st.subheader('Période de crédit')
            periode_credit = st.number_input("Période de crédit", min_value=1, max_value=60, step=1)

            st.subheader('Annuité')
            AMT_ANNUITY_x = AMT_CREDIT_x / periode_credit

            st.subheader('Montant bien voulu')
            AMT_GOODS_PRICE = st.number_input("Montant bien voulu", min_value=1000.0, max_value=100000000.0, step=500.0)

            st.subheader('Âge')
            DAYS_BIRTH = st.number_input("Âge client", min_value=18, max_value=90, step=1)

            st.subheader('Ancienneté professionnelle')
            DAYS_EMPLOYED = st.number_input("Ancienneté professionnelle", min_value=0, max_value=50, step=1)

            st.subheader("COT1")
            EXT_SOURCE_1 = st.number_input("COT1", min_value=0.0, max_value=1.0, step=0.001)

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
                'EXT_SOURCE_1': EXT_SOURCE_1
            }

            response = requests.post("https://backhome-gs1u.onrender.com/predict", json=data)
            result = response.json()

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

    elif page == "Informations sur les Tables":
        st.title("Informations sur les Tables")

        # Récupérer les informations sur les tables
        response = requests.get("https://backhome-gs1u.onrender.com/table_info")
        if response.status_code == 200:
            tables_info = response.json()

            for table_name, table_info in tables_info.items():
                st.subheader(f"Informations sur la table {table_name}")
                st.write(f"Nombre de lignes : {table_info['rows']}")
                st.write(f"Nombre de colonnes : {table_info['columns']}")
                
                st.write(f"10 premières lignes de la table {table_name}:")
                df = pd.DataFrame(table_info['data'][:10], columns=table_info['columns_names'])
                st.dataframe(df)
        else:
            st.error("Erreur lors de la récupération des informations sur les tables.")



    elif page == "Historique des Requêtes":
        st.title("Historique des Requêtes")

        response = requests.get("https://backhome-gs1u.onrender.com/requests")
        if response.status_code == 200:
            requests_data = response.json()
            df = pd.DataFrame(requests_data, columns=['ID', 'Type de contrat', 'Véhiculé', 'Patrimoine', 'Nombre d\'enfants', 'Revenus total', 'Montant Credit', 'Période de crédit', 'Montant bien voulu', 'Âge', 'Ancienneté professionnelle', 'COT1', 'Prediction', 'Decision'])
            st.dataframe(df)
        else:
            st.error("Erreur lors de la récupération des données.")
