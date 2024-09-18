# Section 1: Importation des librairies
import dash
from dash import Dash, html, dcc, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from pymongo import MongoClient
import sqlite3
import warnings
from textblob import TextBlob
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re


# Section 2: Chargement des bases de données avec Python
# Connexion à SQLite
conn = sqlite3.connect('../src/trustscore.db')
df = pd.read_sql_query("SELECT * FROM companies_infos", conn)
conn.close()

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['trustscore']
collection = db['commentaires']
df_comments = pd.DataFrame(list(collection.find()))
client.close()

# Renommer la colonne 'five_star_percentage' en 'five_star_%'
df.rename(columns={'five_star_percentage': 'five_star_%'}, inplace=True)

# Concaténer '%' aux valeurs et ignorer les NaN
df['five_star_%'] = df['five_star_%'].apply(lambda x: f"{x * 100:.0f}%" if pd.notna(x) and isinstance(x, (int, float)) else x)

def company_comment_processing(df_comments):

    df_comments['company_name']= df_comments['company_name'].apply(lambda x: str(x).strip()[:11] + "...")

    text_df = df_comments.drop(['User', 'localisation', 'Titre','nombre_reviews', 'date_experience', 'reply'
           ], axis=1)
           
    text_df.rename(columns={'commentaire': 'text'}, inplace=True)
    #text_df.head()

    return text_df

#Comment processing
def comments_preprocessing(text):
    text = text.lower()
    text = re.sub(r"https\S+|www\S+https\S+", '',text, flags=re.MULTILINE)
    text = re.sub(r'\@w+|\#','',text)
    text = re.sub(r'[^\w\s]','',text)
    text_tokens = word_tokenize(text)
    filtered_text = [w for w in text_tokens if not w in stop_words]

    return " ".join(filtered_text)

#Stream word

stemmer = PorterStemmer()
def stemming(data):
    text = [stemmer.stem(word) for word in data]
    return data

#Polarity fxn
def polarity(text):
    return TextBlob(text).sentiment.polarity

#Comment status
def sentiment(label):
    if label <0:
        return "Negative"
    elif label ==0:
        return "Neutral"
    elif label>0:
        return "Positive"


def comment_polarity(text_df):
    
    #text_df.text = text_df['text'].apply(comments_preprocessing)
    text_df = text_df.drop_duplicates('text')

    #apply streamer
    text_df['text'] = text_df['text'].apply(lambda x: stemming(x))

    #compute polarity
    text_df['polarity'] = text_df['text'].apply(polarity)

    #Detect comment polarity
    text_df['sentiment'] = text_df['polarity'].apply(sentiment)

    return text_df


def compute_sentiment_analysis(df_comments):

    text_df = company_comment_processing(df_comments)

    df_polarity =pd.DataFrame()

    for company in text_df.company_name.unique():
        text_df[text_df.company_name==company]
        comp_pol =comment_polarity(text_df[text_df.company_name==company])
        comp_pol['company_name']= company
        df_polarity= pd.concat([df_polarity,comp_pol])

    #fig = plt.figure(figsize=(5,5))
    #sns.countplot(x='sentiment', data = df_polarity)
    return df_polarity


def get_company_sentiment_count_per_year(df_comments, df_polarity):

    df_comments.rename(columns={"commentaire": "text"}, inplace=True)
    df_p = df_polarity.merge(df_comments[['year', 'company_name','text']], on=['text', 'company_name'], how='left')
    
    # Group by company_name, year, and sentiment, then count the occurrences
    grouped_df = df_p.groupby(['company_name', 'year', 'sentiment']).size().unstack(fill_value=0)
    
    # Reset the index to make the DataFrame more readable
    grouped_df = grouped_df.reset_index()

    #print(grouped_df.head())

    return grouped_df

warnings.filterwarnings("ignore")
# Load data
#df = pd.read_csv('atm_company_info.csv')

# Initialize Dash app

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


################################################################################################################
###### Company Analysis Figures
################################################################################################################
# Map Visualization
#map_fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', hover_name='company_name',
#                            color='trust_score', size='trust_score',
#                            mapbox_style="carto-positron", zoom=3, height=500)

# Company Trust Score Bar Chart
trust_fig = px.bar(df, y='company_name', x='trust_score', color='trust_score', title="Trust Score by Company")
trust_fig.update_layout(barmode='stack', yaxis={'categoryorder':'total ascending'}, height=500)

# Institution Type Pie Chart
institution_fig = px.pie(df, names='institution_type', title="Institution Type Distribution")

# Review Distribution Histogram
# Remove the '%' sign and convert to numeric type
df['five_star_%'] = df['five_star_%'].str.rstrip('%').astype('float')
df = df.sort_values('five_star_%')
df['five_star_%'] = df['five_star_%'].astype(str) + '%'
review_dist_fig = px.histogram(df, x='five_star_%', title="Review Distribution", color='five_star_%')

# Top Reviewed Companies
top_companies_fig = px.bar(df.sort_values(by='nombre_reviews', ascending=False).head(10), 
                           x='company_name', y='nombre_reviews', title="Top Reviewed Companies")

# Company Comparison Radar Chart (trust_score vs five_star_%)
#df_melt = pd.melt(df, id_vars=['company_name'], value_vars=['trust_score', 'five_star_%'])
#comparison_fig = px.line_polar(df_melt, r='value', theta='variable', color='company_name', 
#                               line_close=True, title="Company Comparison")




################################################################################################################
###### Comment Sentiment Analysis 
################################################################################################################
#print(" Comment Sentiment Analysis")


# Example sentiment analysis - dummy data
#df_comments['sentiment'] = df_comments['commentaire'].apply(lambda x: 'Positive' if 'good' in x else 'Negative')

df_polarity = compute_sentiment_analysis(df_comments)
# Sentiment Analysis Bar Chart
sentiment_fig = px.bar(df_polarity, x='company_name', color='sentiment', title="Sentiment Analysis per company")

# Comments Over Time Line Chart
df_comments['date_experience'] = pd.to_datetime(df_comments['date_experience'])
df_comments['year'] = df_comments.date_experience.dt.year
df_g = df_comments.groupby(['year', 'company_name']).size().reset_index()
df_g.rename(columns={0: 'nbr_comments'}, inplace=True)
comments_over_time_fig = px.line(df_g, x='year', y='nbr_comments', title="Number of Comments Over Time", color='company_name', markers=True)

# Sentiment Analysis Histogram per year per company
grouped_df = get_company_sentiment_count_per_year(df_comments,df_polarity)

################################################################################################################
###### Dashboards/layouts 
################################################################################################################
app.layout = dbc.Container([
    dbc.Row([        
        ############### Add filters
        #dbc.Col([dcc.Graph(figure=map_fig)], width=12),
        dbc.Col([html.H4("Company Dashboard")], width=12),
        dbc.Col([dcc.Dropdown(
            id='dropdown-town',
            options=[{'label': x, 'value': x} for x in df['town'].unique()],
            multi=True,
            placeholder="Select a town"
        )], width=6),
        dbc.Col([ dcc.Dropdown(
            id='filter-country',
            options=[{'label': x, 'value': x} for x in df['country'].unique()],
            multi=False,
            placeholder="Select a Country"
        )], width=6),
        dbc.Col([dcc.Graph( id = 'filter-town',figure=trust_fig)], width=6),
        dbc.Col([dcc.Graph(figure=institution_fig)], width=6),
        dbc.Col([dcc.Graph(figure=top_companies_fig)], width=6),
        dbc.Col([dcc.Graph(figure=review_dist_fig)], width=6),
        #dbc.Col([dcc.Graph(figure=comparison_fig)], width=6),
        #dbc.Col([dcc.Graph(id='filtered-graph')], width=6),
    ]),
    dbc.Row([        
        dbc.Col([html.H4("User Feedback Dashboard")], width=12),
        dbc.Col([dcc.Graph(figure=sentiment_fig)], width=6),
        dbc.Col([dcc.Graph(figure=comments_over_time_fig)], width=6), 

        html.H1("Sentiment Analysis Histogram per year per company"),
        # Dropdown for selecting a company
        dcc.Dropdown(
            id='company-dropdown',
            options=[{'label': company, 'value': company} for company in grouped_df['company_name'].unique()],
            value=grouped_df['company_name'].unique()[0],  # Default to the first company
            clearable=False,
            style={'width': '50%'}
        ),
    
    # Graph to display the histogram
    dcc.Graph(id='histogram'),
    ]),
])

# Filtered Trust Score Chart
"""@app.callback(
    dash.dependencies.Output('filtered-graph', 'figure'),
    [dash.dependencies.Input('dropdown-town', 'value')]
)"""

def update_graph(selected_town):
    if selected_town:
        filtered_df = df[df['town'].isin(selected_town)]
    else:
        filtered_df = df
    
    fig = px.bar(filtered_df, x='company_name', y='trust_score', color='trust_score', title="Filtered Trust Score")
    fig.update_layout(xaxis_title="Year", yaxis_title="Count")
    return fig

# Define the callback to update the graph based on the selected company
@app.callback(
    Output('histogram', 'figure'),
    [Input('company-dropdown', 'value')]
)
def update_histogram(selected_company):
    # Filter the DataFrame for the selected company
    filtered_df = grouped_df[grouped_df['company_name'] == selected_company]
    
    # Create a histogram using Plotly Express
    fig = px.bar(
        filtered_df.melt(id_vars=['company_name', 'year']),
        x='year',
        y='value',
        color='sentiment',
        barmode='group',
        title=f'Sentiment Types Trend for {selected_company} per Year'
    )
    fig.update_layout(xaxis_title="Year", yaxis_title="Count")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)


