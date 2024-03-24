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
    data_folder = "Work/Visualization/Data/Not Exported"
    output_folder_base = "Work/Visualization/Graphs/Not Exported"
    
    # For current visualization
    input_file_name = f"Order_Not_Exported_{date_str}.csv"
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

def preprocess_data_for_not_exported(current_df, combined_df):
    """
    Preprocess the data for visualizations of "Not Exported" orders.
    - current_df: DataFrame for the current date visualization.
    - combined_df: DataFrame for trend analysis across multiple dates.
    """
    print(f"Initial DataFrame shape for current visualization: {current_df.shape}")
    # Preprocess current_df
    current_df['UPDATE DATE'] = pd.to_datetime(current_df['UPDATE DATE'].str.split().str[0], format='%d/%m/%Y', errors='coerce')
    current_df.dropna(subset=['UPDATE DATE'], inplace=True)
    current_df.sort_values('UPDATE DATE', inplace=True)
    current_df.drop_duplicates(subset='ORDER CODE', keep='last', inplace=True)
    # Calculate 'ORDER AGE' and 'AGE CATEGORY' for Over Under Analysis with a 5-day threshold
    current_date = datetime.now()
    current_df['ORDER AGE'] = (current_date.date() - current_df['UPDATE DATE'].dt.date).apply(lambda x: x.days)
    current_df['AGE CATEGORY'] = current_df['ORDER AGE'].apply(lambda x: 'Under 5 days' if x < 5 else 'Over 5 days')

    print(f"DataFrame shape after preprocessing for current visualization: {current_df.shape}")

    # For Graph 1: Simple count by country
    simple_count_by_country = current_df.groupby(['COUNTRY'])['ORDER CODE'].nunique().reset_index()
    print(f"DataFrame shape for Graph 1 (Simple count by country): {simple_count_by_country.shape}")

    # For Graph 2: Over Under Analysis
    over_under_analysis = current_df.groupby(['COUNTRY', 'AGE CATEGORY'])['ORDER CODE'].nunique().reset_index()
    print(f"DataFrame shape for Graph 2 (Over Under Analysis): {over_under_analysis.shape}")

    # For Graph 3: Trend analysis, no further preprocessing needed here for combined_df
    print(f"Initial DataFrame shape for trend analysis: {combined_df.shape}")
    trend_analysis = combined_df.groupby(["COUNTRY", "Extraction Date"])["ORDER CODE"].count().reset_index()
    print(f"DataFrame shape for Graph 3 (Trend Analysis): {trend_analysis.shape}")

    return simple_count_by_country, over_under_analysis, trend_analysis

def visualize_graph_1(simple_count_by_country, output_path):
    """
    Visualize the simple count of "Not Exported" orders per country.
    
    :param simple_count_by_country: DataFrame with the count of orders per country.
    :param output_path: Path where the visualization should be saved.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle('Not Exported Orders Per Country')

    # Since all orders are in 'CREATED' status, we directly visualize without status distinction
    sns.barplot(x='COUNTRY', y='ORDER CODE', data=simple_count_by_country, ax=ax, palette='viridis')
    ax.set_xlabel('Country')
    ax.set_ylabel('Unique Order Count')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Annotate bars with the count of orders
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')

    plt.tight_layout()
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(os.path.join(output_path, 'Not_Exported_Orders_Count.png'))
    plt.show()
    print(f"File saved successfully at: {output_path}")

def visualize_graph_2(filtered_data_g2, output_path):
    """
    Visualize the Over vs Under 5 days analysis for "Not Exported" orders per country.
    
    :param filtered_data_g2: DataFrame with the count of orders per country, including 'AGE CATEGORY'.
    :param output_path: Path where the visualization should be saved.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle('Over vs Under 5 Days Per Country')

    sns.barplot(x='COUNTRY', y='ORDER CODE', hue='AGE CATEGORY', data=filtered_data_g2, palette='coolwarm', ax=ax)
    ax.set_xlabel('Country')
    ax.set_ylabel('Unique Order Count')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')

    plt.tight_layout()
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(os.path.join(output_path, 'Not_Exported_Over_Under_5_days.png'))
    plt.show()
    print(f"File saved successfully at: {output_path}")

def visualize_graph_3(filtered_data_g3, specific_dates, output_path):
    """
    Visualize the trend analysis for "Not Exported" orders over time.
    
    :param filtered_data_g3: DataFrame with aggregated order counts per country over time.
    :param specific_dates: List of specific dates for trend analysis.
    :param output_path: Path where the visualization should be saved.
    """
    specific_dates_dt = pd.to_datetime(specific_dates, format='%d-%m-%Y')
    
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle('Order Trend Analysis')

    for country in filtered_data_g3["COUNTRY"].unique():
        country_data = filtered_data_g3[filtered_data_g3["COUNTRY"] == country]
        ax.plot(country_data["Extraction Date"], country_data["ORDER CODE"], marker="o", label=country)
        
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_xlabel('Extraction Date')
    ax.set_ylabel('Order Count')
    ax.set_xticks(specific_dates_dt)
    ax.set_xticklabels(specific_dates_dt.strftime('%Y-%m-%d'), rotation=45, ha="right")
    ax.legend(title="Country")
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'Not_Exported_Trend_Analysis.png'))
    plt.show()
    print(f"File saved successfully at: {output_path}")

def visualize_all_graphs_together(filtered_data_g1, filtered_data_g2, filtered_data_g3, specific_dates, output_path):
    """
    Visualizes all three graphs (Trend Analysis, Over & Under, Simple Count) side by side in a single figure.
    
    :param filtered_data_g1: DataFrame for simple count by country.
    :param filtered_data_g2: DataFrame for Over & Under analysis.
    :param filtered_data_g3: DataFrame for trend analysis.
    :param specific_dates: List of specific dates for trend analysis.
    :param output_path: Path where the combined visualization should be saved.
    """
    # Convert specific dates for plotting
    specific_dates_dt = pd.to_datetime(specific_dates, format='%d-%m-%Y')
    
    # Create figure and subplots
    fig, axes = plt.subplots(1, 3, figsize=(20, 6), sharey='row')
    fig.suptitle('Not Exported - Order Analysis')
    
    # Trend Analysis on the first subplot
    for country in filtered_data_g3["COUNTRY"].unique():
        country_data = filtered_data_g3[filtered_data_g3["COUNTRY"] == country]
        axes[0].plot(country_data["Extraction Date"], country_data["ORDER CODE"], marker="o", label=country)
    axes[0].set_title('Trend Analysis')
    axes[0].set_xlabel('Extraction Date')
    axes[0].set_ylabel('Order Count')
    axes[0].set_xticks(specific_dates_dt)
    axes[0].set_xticklabels(specific_dates_dt.strftime('%Y-%m-%d'), rotation=45, ha="right")
    axes[0].legend(title="Country")
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)

    # Over & Under Analysis on the second subplot
    sns.barplot(x='COUNTRY', y='ORDER CODE', hue='AGE CATEGORY', data=filtered_data_g2, palette='coolwarm', ax=axes[1])
    axes[1].set_title('Over & Under 5 Days')
    axes[1].set_xlabel('Country')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(axis='y', linestyle='--', alpha=0.7)

    # Simple Count by Country on the third subplot
    sns.barplot(x='COUNTRY', y='ORDER CODE', data=filtered_data_g1, palette='viridis', ax=axes[2])
    axes[2].set_title('Count by Country')
    axes[2].set_xlabel('Country')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'Not Exported Analysis.png'))
    plt.show()
    print(f"File saved successfully at: {output_path}")

# Setup paths and load data
date_str = "26-03-2024"
specific_dates = ["24-03-2024", "26-03-2024"]

current_df, combined_df, output_path = setup_paths(date_str, specific_dates)
filtered_data_g1, filtered_data_g2, filtered_data_g3 = preprocess_data_for_not_exported(current_df, combined_df)
visualize_graph_1(filtered_data_g1, output_path)
visualize_graph_2(filtered_data_g2, output_path)
visualize_graph_3(filtered_data_g3, specific_dates, output_path)
visualize_all_graphs_together(filtered_data_g1, filtered_data_g2, filtered_data_g3, specific_dates, output_path)
