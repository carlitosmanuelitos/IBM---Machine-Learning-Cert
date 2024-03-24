import os
import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def setup_paths(date_str, specific_dates):
    """
    Set up input and output file paths based on the given date string, load the data into a DataFrame for current visualization,
    and prepare a combined DataFrame for trend analysis based on specific dates.
    
    :param date_str: A string representing the date in the format "dd-mm-yyyy" for current visualization.
    :param specific_dates: A list of strings representing dates for trend analysis.
    :return: DataFrame for current visualization, DataFrame for trend analysis, and the output path for saving visualizations.
    """
    data_folder = "Work/Visualization/Data/Orders"
    output_folder_base = "Work/Visualization/Graphs/Orders"
    
    # For current visualization
    input_file_name = f"Order_Monitoring_{date_str}.csv"
    output_folder = os.path.join(output_folder_base, date_str)
    input_file_path = os.path.join(data_folder, input_file_name)
    output_path = os.path.join(output_folder)
    
    # Create the output directory if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    print(f"Input file path for current visualization: {input_file_path}")
    print(f"Output path for current visualization: {output_path}")
    
    # Load the data into a DataFrame for current visualization
    current_df = pd.read_csv(input_file_path, sep=";")
    print(f"Initial DataFrame shape for current visualization: {current_df.shape}")

    # For trend analysis
    specific_dates_dt = pd.to_datetime(specific_dates, format="%d-%m-%Y")  # Correct format specification
    combined_df = pd.DataFrame()

    # Read data from each CSV file and append to combined_df for trend analysis
    for file in os.listdir(data_folder):
        if file.lower().endswith(".csv"):
            file_date_str = file.split("_")[-1].split('.')[0]
            extraction_date = pd.to_datetime(file_date_str, format="%d-%m-%Y")  # Ensure this matches the format in the filenames
            if extraction_date in specific_dates_dt:
                df = pd.read_csv(os.path.join(data_folder, file), sep=";")
                df["Extraction Date"] = extraction_date
                combined_df = combined_df._append(df, ignore_index=True)

    print(f"Combined DataFrame shape for trend analysis: {combined_df.shape}")

    return current_df, combined_df, output_path

def preprocess_data_for_graphs(current_df, combined_df):
    # Common preprocessing steps for current_df
    print(f"Initial DataFrame shape for current visualization: {current_df.shape}")
    current_df['UPDATE DATE'] = pd.to_datetime(current_df['UPDATE DATE'].str.split().str[0], format='%d/%m/%Y', errors='coerce')
    current_df.dropna(subset=['UPDATE DATE'], inplace=True)
    current_df.sort_values('UPDATE DATE', inplace=True)
    current_df.drop_duplicates(subset='ORDER CODE', keep='last', inplace=True)
    print(f"DataFrame shape after preprocessing for current visualization: {current_df.shape}")

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

    return filtered_data_g1, filtered_data_g2, filtered_data_g3

def visualize_graph_1(filtered_data_g1, output_path):
    # Total orders across all statuses for percentage calculation
    total_orders_g1 = filtered_data_g1['ORDER CODE'].sum()
    fig, axes = plt.subplots(2, 2, figsize=(14, 8.5))
    fig.suptitle('Count of Order Per Country Per Status')
    relevant_statuses = ['CREATED', 'PROCESSED', 'RECEIVED', 'SHIPPED']

    for i, status in enumerate(relevant_statuses):
        filtered_status_data = filtered_data_g1[filtered_data_g1['PMI ORDER STATUS'] == status].copy()
        filtered_status_data.sort_values(by='ORDER CODE', ascending=False, inplace=True)
        total_orders_current_status = filtered_status_data['ORDER CODE'].sum()
        percentage_of_total = (total_orders_current_status / total_orders_g1) * 100

        row, col = divmod(i, 2)
        ax = sns.barplot(x='COUNTRY', y='ORDER CODE', data=filtered_status_data, ax=axes[row, col], palette='viridis')
        ax.set_title(f'Orders in {status} Status ({percentage_of_total:.1f}% of all orders)')
        ax.set_xlabel('Country')
        ax.set_ylabel('Unique Order Count')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'Order_Status_Count.png'))
    plt.show()

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

def visualize_graph_3(filtered_data_g3, specific_dates, output_path):
    # Ensure Matplotlib recognizes the specific_dates as dates for plotting
    specific_dates_dt = pd.to_datetime(specific_dates, format='%d-%m-%Y')
    
    # Plotting
    fig, axes = plt.subplots(2, 2, figsize=(14, 8.5))
    fig.suptitle('Order Trend by Status')

    order_statuses = ["CREATED", "RECEIVED", "PROCESSED", "SHIPPED"]
    for i, status in enumerate(order_statuses):
        status_data = filtered_data_g3[filtered_data_g3["PMI ORDER STATUS"] == status]
        agg_data = status_data.groupby(['COUNTRY', 'Extraction Date'])['ORDER CODE'].sum().reset_index()
        
        row, col = divmod(i, 2)
        for country in agg_data["COUNTRY"].unique():
            country_data = agg_data[agg_data["COUNTRY"] == country]
            axes[row, col].plot(country_data["Extraction Date"], country_data["ORDER CODE"], marker="o", label=country)
            
        axes[row, col].yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        axes[row, col].set_title(f'Orders in {status} Status')
        axes[row, col].set_xlabel('Extraction Date')
        axes[row, col].set_ylabel('Order Count')
        axes[row, col].set_xticks(specific_dates_dt)
        axes[row, col].set_xticklabels(specific_dates_dt.strftime('%Y-%m-%d'), rotation=45, ha="right")
        axes[row, col].legend(title="Country")
        axes[row, col].grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'Order Trend Analysis.png'))
    plt.show()
    print(f"File saved successfully at: {output_path}")

# Setup paths and load data
date_str = "22-03-2024"
specific_dates = ["08-03-2024", "15-03-2024", "22-03-2024"]

current_df, combined_df, output_path = setup_paths(date_str, specific_dates)
filtered_data_g1, filtered_data_g2, filtered_data_g3 = preprocess_data_for_graphs(current_df, combined_df)
visualize_graph_1(filtered_data_g1, output_path)
visualize_graph_2(filtered_data_g2, output_path)
visualize_graph_3(filtered_data_g3, specific_dates, output_path)
