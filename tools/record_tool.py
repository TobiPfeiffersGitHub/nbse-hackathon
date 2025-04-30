import pandas as pd

def update_kartei(scraped_data, kartei_path='data/kartei.csv'):
    """
    Takes in scraped HCP data (list of dicts), appends it to kartei.csv, and deduplicates based on hcp_id.
    """
    try:
        kartei_df = pd.read_csv(kartei_path)
    except FileNotFoundError:
        kartei_df = pd.DataFrame(columns=[
            'hcp_id', 'name', 'specialty', 'city', 'preferred_channel', 'contacted'
        ])

    new_data_df = pd.DataFrame(scraped_data)

    # Fill 'contacted' field in new data if missing
    if 'contacted' not in new_data_df.columns:
        new_data_df['contacted'] = False

    # Combine and deduplicate by 'hcp_id'
    combined_df = pd.concat([kartei_df, new_data_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset='hcp_id', keep='first')

    combined_df.to_csv(kartei_path, index=False)
    return f"Kartei updated with {len(new_data_df)} new entries."

def get_outreach_candidates(kartei_path='data/kartei.csv'):
    """
    Returns HCPs who have not been contacted yet.
    """
    df = pd.read_csv(kartei_path)
    candidates = df[df['contacted'] != True]
    return candidates.to_dict(orient='records')
