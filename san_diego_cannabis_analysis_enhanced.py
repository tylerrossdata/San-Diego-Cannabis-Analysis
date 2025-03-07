import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium

# Load all datasets
sales_data = pd.read_csv('/Users/Admin/Desktop/enhanced_cannabis_sales_sandiego.csv')
strains_data = pd.read_csv('/Users/Admin/Desktop/cannabis_strains.csv')
shops_data = pd.read_csv('/Users/Admin/Desktop/enhanced_cannabis_shops_sandiego.csv')

# Debug: Print column names and sample data to verify
print("Sales Data Columns:", sales_data.columns.tolist())
print("Sample Sales Data (first 5 rows):\n", sales_data.head())
print("Unique Counties in Sales Data:", sales_data['County'].unique())

# Clean the sales data (focus on San Diego)
sales_data = sales_data.dropna(subset=['Total Taxable Sales', 'Excise Tax'])  # Drop rows with missing sales or excise tax
sales_data['total_sales'] = pd.to_numeric(sales_data['Total Taxable Sales'], errors='coerce')  # Convert to numeric, handle errors
sales_data['excise_tax'] = pd.to_numeric(sales_data['Excise Tax'], errors='coerce')  # Use Excise Tax instead of Total Tax
san_diego_sales = sales_data[sales_data['County'].str.strip().str.upper() == 'SAN DIEGO']  # Case-insensitive, strip whitespace

# Debug: Check San Diego sales data
print("San Diego Sales Data (first 5 rows):\n", san_diego_sales.head())
print("Number of San Diego records (2021-2024):", len(san_diego_sales[san_diego_sales['Calendar Year'].between(2021, 2024)]))

# Group by year for San Diego sales and excise tax trends (filter for 2021-2024)
yearly_sales = san_diego_sales[san_diego_sales['Calendar Year'].between(2021, 2024)].groupby('Calendar Year')['total_sales'].sum() / 1e6  # Convert to millions
yearly_excise = san_diego_sales[san_diego_sales['Calendar Year'].between(2021, 2024)].groupby('Calendar Year')['excise_tax'].sum() / 1e6  # Convert to millions

# Debug: Check grouped data
print("Yearly Sales (Millions):", yearly_sales.tolist())
print("Yearly Excise Tax (Millions):", yearly_excise.tolist())

# Analyze strain types (simulating San Diego popularity with California-wide estimates)
strain_types = pd.Series({'Hybrid': 45, 'Indica': 35, 'Sativa': 20})

# Filter shops for San Diego (approximate lat/lng bounds for San Diego: 32.5 to 33.2 N, -117.5 to -116.7 W)
san_diego_shops = shops_data[
    (shops_data['lat'].notna()) & 
    (shops_data['lng'].notna()) & 
    (shops_data['state'] == 'CA') & 
    (shops_data['lat'].between(32.5, 33.2)) & 
    (shops_data['lng'].between(-117.5, -116.7))
]

# Debug: Check if san_diego_shops is empty
print("Number of San Diego shops found:", len(san_diego_shops))
if len(san_diego_shops) == 0:
    print("Warning: No shops found in San Diego. Check the shops dataset or filter criteria.")

# Create visualizations
# 1. Yearly Sales and Excise Tax Trends Bar Chart with grid and labels
if not yearly_sales.empty and not yearly_excise.empty:  # Check if data exists
    plt.figure(figsize=(10, 6))  # Larger figure for two datasets
    bar_width = 0.35
    x = np.arange(len(yearly_sales))

    plt.bar(x - bar_width/2, yearly_sales, bar_width, color='green', label='Sales (Millions $)')
    plt.bar(x + bar_width/2, yearly_excise, bar_width, color='blue', label='Excise Tax (Millions $)')

    plt.title('Yearly Cannabis Sales and Excise Tax Trends in San Diego, CA (2021-2024)')
    plt.xlabel('Year')
    plt.ylabel('Amount (Millions $)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add horizontal grid lines
    plt.xticks(x, yearly_sales.index)
    plt.legend()
    # Add value labels on top of bars, adjusted for larger values
    for i, (sales, excise) in enumerate(zip(yearly_sales, yearly_excise)):
        plt.text(i - bar_width/2, sales + 10, f'{sales:.0f}M', ha='center', va='bottom')
        plt.text(i + bar_width/2, excise + 10, f'{excise:.0f}M', ha='center', va='bottom')
    plt.tight_layout()
    plt.show()
else:
    print("Warning: No data available for the bar graph. Check 'enhanced_cannabis_sales_sandiego.csv' and script logic.")

# 2. Strain Types Pie Chart
plt.figure(figsize=(6, 6))
strain_types.plot(kind='pie', autopct='%1.1f%%', colors=['#FF6B6B', '#4ECDC4', '#45B7D1'], 
                 startangle=90, labeldistance=1.1, wedgeprops={'edgecolor': 'white'})
plt.title('Estimated Strain Type Popularity in San Diego')
plt.axis('equal')  # Equal aspect ratio ensures a circular pie
plt.legend(strain_types.index, title="Strain Types", loc="center left", bbox_to_anchor=(1, 0.5))  # Move legend outside
plt.tight_layout()
plt.show()

# 3. Map of San Diego Cannabis Shops (reverted to default OpenStreetMap tiles)
try:
    if len(san_diego_shops) > 0:
        san_diego_map = folium.Map(location=[32.7157, -117.1611], zoom_start=10)  # Revert to default OpenStreetMap tiles

        # Add markers for each San Diego shop
        for index, row in san_diego_shops.iterrows():
            folium.Marker(
                location=[row['lat'], row['lng']],
                popup=row['name'],
                icon=folium.Icon(color='green', icon='leaf')  # Cannabis-themed icon
            ).add_to(san_diego_map)

        # Save the map as an HTML file (view in Chrome)
        san_diego_map.save('/Users/Admin/Desktop/san_diego_cannabis_shops_map_enhanced.html')
        print("Map saved successfully as 'san_diego_cannabis_shops_map_enhanced.html' on Desktop.")
    else:
        print("Error: No shops found to create the map. Check the shops dataset or filter criteria.")
except Exception as e:
    print(f"Error generating map: {e}")

print("Analysis complete! Check the bar chart, pie chart, and open 'san_diego_cannabis_shops_map_enhanced.html' in Chrome for the map if generated.")
