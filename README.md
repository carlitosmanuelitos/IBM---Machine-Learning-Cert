
def preprocess_data_for_graphs(current_df, combined_df):
    # Common preprocessing steps for current_df
    print(f"Initial DataFrame shape for current visualization: {current_df.shape}")
    current_df['UPDATE DATE'] = pd.to_datetime(current_df['UPDATE DATE'].str.split().str[0], format='%d/%m/%Y', errors='coerce')
    current_df.dropna(subset=['UPDATE DATE'], inplace=True)
    current_df.sort_values('UPDATE DATE', inplace=True)
    current_df.drop_duplicates(subset='ORDER CODE', keep='last', inplace=True)
    print(f"DataFrame shape after preprocessing for current visualization: {current_df.shape}")

    # Drop rows based on ORDER TYPE CODE
    order_type_to_drop = ["ZL2", "ZL3", "ZDE", "ZBC"]
    current_df = current_df[~current_df['ORDER TYPE CODE'].isin(order_type_to_drop)]
    print(f"DataFrame shape after removing ZBC, ZDE, ZL2 & ZL3 for current visualization: {current_df.shape}")


    # Drop rows based on BASE STORE containing specific substrings
    substrings_to_drop = ['retailpos', 'indirectretailer', 'fieldCoach']
    current_df = current_df[~current_df['BASE STORE'].str.contains('|'.join(substrings_to_drop), case=False, na=False)]
    print(f"DataFrame shape after removing FieldCoach, indirectretailer, retailpos for current visualization: {current_df.shape}")


    # Calculate 'ORDER AGE' and 'AGE CATEGORY' for Graph 2 using current_df
    current_date = datetime.now()
    current_df['ORDER AGE'] = (current_date.date() - current_df['UPDATE DATE'].dt.date).apply(lambda x: x.days)
    current_df['AGE CATEGORY'] = current_df['ORDER AGE'].apply(lambda x: 'Under 30 days' if x < 30 else 'Over 30 days')

    # Prepare Data for Graph 1
    relevant_statuses = ['CREATED', 'PROCESSED', 'RECEIVED', 'SHIPPED']
    grouped_data = current_df.groupby(['COUNTRY', 'PMI ORDER STATUS'])['ORDER CODE'].nunique().reset_index()
    filtered_data_g1 = grouped_data[grouped_data['PMI ORDER STATUS'].isin(relevant_statuses)]
    print(f"DataFrame shape for Graph 1: {filtered_data_g1.shape}")

    # Prepare Data for Graph 2
    grouped_data_vs = current_df.groupby(['COUNTRY', 'PMI ORDER STATUS', 'AGE CATEGORY'])['ORDER CODE'].nunique().reset_index()
    filtered_data_g2 = grouped_data_vs[grouped_data_vs['PMI ORDER STATUS'].isin(relevant_statuses)]
    print(f"DataFrame shape for Graph 2: {filtered_data_g2.shape}")

    # Prepare Data for Graph 3    
    print(f"Initial DataFrame shape for trend analysis: {combined_df.shape}")
    filtered_data_g3 = combined_df.groupby(["COUNTRY", "PMI ORDER STATUS", "Extraction Date"])["ORDER CODE"].count().reset_index()
    print(f"DataFrame shape for Graph 3: {filtered_data_g3.shape}")


def visualize_graph_2(filtered_data_g2, output_path):
    # Total orders across all statuses for percentage calculation
    total_orders_g2 = filtered_data_g2['ORDER CODE'].sum()
    fig, axes = plt.subplots(2, 2, figsize=(14, 8.5))
    fig.suptitle('Over vs Under 30 days Per Country Per Status')
    relevant_statuses = ['CREATED', 'PROCESSED', 'RECEIVED', 'SHIPPED']

    for i, status in enumerate(relevant_statuses):
        filtered_status_data_vs = filtered_data_g2[filtered_data_g2['PMI ORDER STATUS'] == status].copy()
        filtered_status_data_vs.sort_values(by='ORDER CODE', ascending=False, inplace=True)
        total_orders_current_status_vs = filtered_status_data_vs['ORDER CODE'].sum()
        percentage_of_total_vs = (total_orders_current_status_vs / total_orders_g2) * 100

        row, col = divmod(i, 2)
        ax = sns.barplot(x='COUNTRY', y='ORDER CODE', hue='AGE CATEGORY', data=filtered_status_data_vs, ax=axes[row, col], palette='coolwarm')
        ax.set_title(f'Orders in {status} Status ({percentage_of_total_vs:.1f}% of all orders)')
        ax.set_xlabel('Country')
        ax.set_ylabel('Unique Order Count')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'Over_Under_30_days.png'))
    plt.show()



I want to make the following changes. 
need the output of preprocessor to produce a new graph. with more details on the AGE CATEGORY. 

My recommendation would be to save a copy of the current_df before applying over under 30 days. 
The goal would be two retrieve an extra dataframe with the following requirements. Only orders in SHIPPED status, AGE CATEGORY should track
- under 10 D
- under 20 D
- under 30 D
- under 40 D
- over 40 D

this df should then also be groupped based on the below conditions  

 # Prepare Data for Graph 4
    grouped_data_vs_2 = current_df_2.groupby(['COUNTRY', 'PMI ORDER STATUS', 'AGE CATEGORY'])['ORDER CODE'].nunique().reset_index()
    filtered_data_g4 = grouped_data_vs_2[grouped_data_vs['PMI ORDER STATUS'].isin(relevant_statuses)]
    print(f"DataFrame shape for Graph 2: {filtered_data_g4.shape}")


Then I would like to adapt visualize_graph_2 to visualize the data. new requirements are that only 1 graph should be displayed. And the country should be a input parameter of the graph
