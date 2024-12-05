# Section 1: Importation des librairies
import dash
from dash import Dash, html, dcc, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import requests
from textblob import TextBlob
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import warnings

warnings.filterwarnings("ignore")

# Base URL de l'API Flask
BASE_URL = "http://flask_api:5000/api"

# Récupérer les données des entreprises via l'API
companies_response = requests.get(f"{BASE_URL}/companies")
if companies_response.status_code == 200:
    df = pd.DataFrame(companies_response.json())
else:
    print("Erreur lors de la récupération des entreprises :", companies_response.json())
    df = pd.DataFrame()  # DataFrame vide en cas d'erreur

# Récupérer les données des commentaires via l'API
comments_response = requests.get(f"{BASE_URL}/comments")
if comments_response.status_code == 200:
    df_comments = pd.DataFrame(comments_response.json())
else:
    print("Erreur lors de la récupération des commentaires :", comments_response.json())
    df_comments = pd.DataFrame()  # DataFrame vide en cas d'erreur


# Assurez-vous que 'date_experience' est bien une colonne dans df_comments
if 'date_experience' in df_comments.columns:
    df_comments['date_experience'] = pd.to_datetime(df_comments['date_experience'], errors='coerce')
    df_comments['year'] = df_comments['date_experience'].dt.year
else:
    print("Erreur : 'date_experience' n'est pas présent dans df_comments.")

# Vérifiez que la colonne year est bien ajoutée
print("Colonnes dans df_comments après ajout de 'year' :", df_comments.columns)

# Prétraitement des colonnes
df.rename(columns={'five_star_percentage': 'five_star_%', 'review': 'nombre_reviews'}, inplace=True)

# Convertir et formater `five_star_%`
df['five_star_%'] = df['five_star_%'].apply(
    lambda x: f"{x * 100:.0f}%" if pd.notna(x) and isinstance(x, (int, float)) else x
)

# Prétraitement des commentaires
def company_comment_processing(df_comments):
    #df_comments['company_name'] = df_comments['company_name'].apply(lambda x: str(x).strip()[:11] + "...")
    df_comments.rename(columns={'commentaire': 'text'}, inplace=True)
    df_comments['text'] = df_comments['text'].fillna('').astype(str)  # Remplacer NaN par une chaîne vide
    return df_comments[['text', 'company_name', 'year']]

# Nettoyage des textes pour le traitement des sentiments
stemmer = PorterStemmer()

def stemming(data):
    if not isinstance(data, str):
        return data
    text = [stemmer.stem(word) for word in data.split()]
    return " ".join(text)

def polarity(text):
    return TextBlob(text).sentiment.polarity

def sentiment(label):
    if label < 0:
        return "Negative"
    elif label == 0:
        return "Neutral"
    else:
        return "Positive"

# Analyse des sentiments
def compute_sentiment_analysis(df_comments):
    text_df = company_comment_processing(df_comments)
    text_df = text_df.drop_duplicates('text')  # Supprimer les doublons
    text_df['text'] = text_df['text'].apply(stemming)  # Appliquer le stemming
    text_df['polarity'] = text_df['text'].apply(polarity)
    text_df['sentiment'] = text_df['polarity'].apply(sentiment)
    return text_df

df_polarity = compute_sentiment_analysis(df_comments)

# Jointure pour regrouper les sentiments par entreprise et année
def get_company_sentiment_count_per_year(df_comments, df_polarity):
    # Harmonisation des colonnes clés

    # Appliquer un nettoyage strict et cohérent à text et company_name
    df_comments['text'] = df_comments['text'].str.lower().str.strip()
    df_polarity['text'] = df_polarity['text'].str.lower().str.strip()

    df_comments['company_name'] = df_comments['company_name'].str.lower().str.strip()
    df_polarity['company_name'] = df_polarity['company_name'].str.lower().str.strip()

    # Affichez les exemples pour confirmer le nettoyage
    print("Exemples dans df_comments['company_name'] après nettoyage :", df_comments['company_name'].unique()[:5])
    print("Exemples dans df_polarity['company_name'] après nettoyage :", df_polarity['company_name'].unique()[:5])
    print("Exemples dans df_comments['text'] après nettoyage :", df_comments['text'].unique()[:5])
    print("Exemples dans df_polarity['text'] après nettoyage :", df_polarity['text'].unique()[:5])


    print("Colonnes dans df_comments :", df_comments.columns)

    # Ajouter le stemming à df_comments['text']
    df_comments['text'] = df_comments['text'].apply(lambda x: stemming(x) if isinstance(x, str) else x)

    # Réimprimer les exemples pour vérifier
    print("Exemples dans df_comments['text'] après stemming :", df_comments['text'].unique()[:5])
    print("Exemples dans df_polarity['text'] :", df_polarity['text'].unique()[:5])


    # Merge avec l'indicateur pour analyse
    df_p = df_polarity.merge(
        df_comments[['year', 'company_name', 'text']],
        on=['text', 'company_name'],
        how='left',
        indicator=True
    )

    # Vérifiez les statistiques du merge
    print("Statistiques sur l'indicateur de merge (_merge) :", df_p['_merge'].value_counts())

    # Identifier les lignes sans correspondance
    no_match = df_p[df_p['_merge'] == 'left_only']
    print("Lignes sans correspondance après stemming :")
    print(no_match[['text', 'company_name']].head(10))


    # Utiliser `year_y` comme colonne pour le groupby
    if 'year_y' in df_p.columns:
        df_p['year'] = df_p['year_y']
    else:
        print("Erreur : la colonne 'year_y' est absente après le merge.")
        return pd.DataFrame()  # Retourne un DataFrame vide pour éviter des erreurs

    # Vérifiez les lignes manquantes

    # Group by company_name, year, and sentiment, puis compter les occurrences
    grouped_df = df_p.groupby(['company_name', 'year', 'sentiment']).size().unstack(fill_value=0).reset_index()

    print("Résultat final du groupby :", grouped_df.head())
    return grouped_df


df_comments['date_experience'] = pd.to_datetime(df_comments['date_experience'])
df_comments['year'] = df_comments['date_experience'].dt.year
grouped_df = get_company_sentiment_count_per_year(df_comments, df_polarity)
print("Contenu de grouped_df :", grouped_df)
missing_companies = set(df_comments['company_name'].unique()) - set(grouped_df['company_name'].unique())
print("Entreprises manquantes :", missing_companies)


# Dash App Layout
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Company Dashboard"), width=12),
        dbc.Col(dcc.Graph(figure=px.bar(df, y='company_name', x='trust_score', title="Trust Score by Company")), width=6),
        dbc.Col(dcc.Graph(figure=px.pie(df, names='institution_type', title="Institution Type Distribution")), width=6),
    ]),
    dbc.Row([
        dbc.Col(html.H1("Sentiment Analysis Dashboard"), width=12),
        dbc.Col(dcc.Dropdown(
            id='company-dropdown',
            options=[{'label': company, 'value': company} for company in grouped_df['company_name'].unique()],
            value=grouped_df['company_name'].unique()[0] if not grouped_df.empty else None,
            clearable=False
        ), width=6),
        dbc.Col(dcc.Graph(id='histogram'), width=12),
    ])
])

# Callback for sentiment histogram
@app.callback(
    Output('histogram', 'figure'),
    [Input('company-dropdown', 'value')]
)
def update_histogram(selected_company):
    if not grouped_df.empty and selected_company:
        filtered_df = grouped_df[grouped_df['company_name'] == selected_company]
        fig = px.bar(
            filtered_df.melt(id_vars=['company_name', 'year']),
            x='year', y='value', color='sentiment', barmode='group',
            title=f'Sentiment Types Trend for {selected_company} per Year'
        )
        return fig
    return px.bar(title="No data available")

# Lancer le serveur Dash
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8050, debug=True)
