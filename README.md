def visualize_age_category_distribution(filtered_data_g4, country, output_path):
    # Filter data for the specified country
    country_data = filtered_data_g4[filtered_data_g4['COUNTRY'] == country]
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='AGE CATEGORY', y='ORDER CODE', data=country_data, palette='coolwarm')
    plt.title(f'Order Age Distribution in {country}')
    plt.xlabel('Age Category')
    plt.ylabel('Unique Order Count')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, f'{country}_Age_Distribution.png'))
    plt.show()



    # Save a copy of current_df before applying the final age categories
    current_df_2 = current_df.copy()
    current_df_2 = current_df_2[current_df_2['PMI ORDER STATUS'] == 'SHIPPED']
    current_date = datetime.now()
    current_df_2['ORDER AGE'] = (current_date.date() - current_df_2['UPDATE DATE'].dt.date).apply(lambda x: x.days)
    current_df_2['AGE CATEGORY'] = pd.cut(current_df_2['ORDER AGE'], bins=[-np.inf, 10, 20, 30, 40, np.inf], labels=['Under 10 D', 'Under 20 D', 'Under 30 D', 'Under 40 D', 'Over 40 D'])

    # Prepare Data for Graph 4
    grouped_data_vs_2 = current_df_2.groupby(['COUNTRY', 'AGE CATEGORY'])['ORDER CODE'].nunique().reset_index()
    print(f"DataFrame shape for Graph 4: {grouped_data_vs_2.shape}")

