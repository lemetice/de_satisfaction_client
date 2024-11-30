import pandas as pd
def process_and_join_data(df_entreprises, df_details):
    df_final = pd.merge(
        df_entreprises,
        df_details[['Commentaire', 'five_Star_Percentage']],
        left_on='company_name',
        right_on='Commentaire',
        how='left'
    )
    df_final.drop(columns=['Commentaire'], inplace=True)
    return df_final
