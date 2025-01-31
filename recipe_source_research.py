import db
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams

rcParams['font.family'] = 'Lucida Sans Unicode'

# Input data: Research IDs, number of respondents, and results
research_data = [
    {
        "id": 1,
        "respondents": 1014,
        "results": {
            "Children's requests": 0.75,
            "Family recommendations": 0.73,
            "Cooking shows/tutorials": 0.69,
            "Magazines": 0.68,
            "TV shows": 0.59
        }
    },
    {
        "id": 2,
        "respondents": 7708,
        "results": {
            "Recipe sites/apps": 0.496,
            "TV programs": 0.313,
            "Family opinions": 0.216,
            "Cookbooks": 0.178,
            "Family/friends recipes": 0.15,
            "Product ads (supermarkets)": 0.149,
            "Recipe on food packaging": 0.126,
            "Supermarket displays": 0.126,
            "Magazines": 0.089,
            "Menus at foodservice stores": 0.088,
            "Newspapers": 0.083,
            "TV commercials": 0.076,
            "Free PR magazines": 0.053,
            "Leaflets in newspapers": 0.05,
            "Cooking classes": 0.026,
            "Radio": 0.015,
            "Other": 0.035,
            "No reference info": 0.192,
            "No answer": 0.003
        }
    },
    {
        "id": 3,
        "respondents": 5336,
        "results": {
            "Friends/family": 0.54,
            "Cooking websites": 0.49,
            "Social media": 0.4,
            "TV cooking shows": 0.35,
            "Supermarket recipe cards": 0.34,
            "Magazines/newspapers": 0.3,
            "Product packaging": 0.22,
            "Commercials": 0.08
        }
    },
    {
        "id": 4,
        "respondents": 1349,
        "results": {
            "YouTube videos": 0.408,
            "Friends/acquaintances": 0.272,
            "Written recipes on blogs": 0.231,
            "Social media videos": 0.045,
            "Printed cookbooks": 0.017,
            "Cooking classes": 0.002,
            "Other": 0.024
        }
    },
    {
        "id": 5,
        "respondents": 10562,
        "results": {
            "Recipe websites/apps": 0.45,
            "Friends' posts on social media": 0.315,
            "Family recipes": 0.43,
            "TV shows": 0.35,
            "Restaurant meals": 0.31,
            "Online tutorials": 0.235,
            "Recipe books": 0.33,
            "Bloggers/vloggers": 0.175
        }
    }
]

# Total respondents across all research studies
total_respondents = sum([data["respondents"] for data in research_data])

# Initializing a consolidated results dictionary
consolidated_results = {}

# Processing each research study to calculate weighted averages
for research in research_data:
    weight = research["respondents"] / total_respondents
    for category, value in research["results"].items():
        if category not in consolidated_results:
            consolidated_results[category] = 0
        consolidated_results[category] += value * weight

# Defining mapping for consolidation
category_mapping = {
    "Online Recipe Sources": [
        "Recipe sites/apps", "Cooking websites", "Recipe websites/apps", "Written recipes on blogs"
    ],
    "Social Media": [
        "Friends' posts on social media", "Social media", "Social media videos"
    ],
    "Family and Friends": [
        "Family recipes", "Friends/family", "Family recommendations", "Family/friends recipes", "Family opinions",
        "Friends/acquaintances"
    ],
    "TV Shows": [
        "TV shows", "TV programs", "TV cooking shows"
    ],
    "Printed/Physical Materials": [
        "Magazines", "Magazines/newspapers", "Recipe books", "Cookbooks", "Printed cookbooks",
        "Supermarket recipe cards", "Newspapers", "Leaflets in newspapers"
    ],
    "Online Tutorials": [
        "Online tutorials", "Cooking shows/tutorials", "YouTube videos"
    ],
    "Restaurant/Commercial Sources": [
        "Restaurant meals", "Menus at foodservice stores", "Product packaging", "Product ads (supermarkets)",
        "Supermarket displays", "Commercials"
    ],
    "Other Sources": [
        "Children's requests", "Cooking classes", "Free PR magazines", "Radio", "Other"
    ]
}

# Consolidating results into meaningful clusters
final_consolidated_results = {}
for cluster, categories in category_mapping.items():
    final_consolidated_results[cluster] = sum(
        [consolidated_results.get(category, 0) for category in categories]
    )

# Converting final consolidated results to DataFrame
final_consolidated_df = pd.DataFrame(
    final_consolidated_results.items(), columns=["Category", "Weighted Average"]
).sort_values(by="Weighted Average", ascending=False)

# Displaying the final consolidated DataFrame
print(final_consolidated_df)

# Exporting the consolidated table to a CSV file
final_consolidated_df.to_csv("consolidated_recipe_sources.csv", index=False)

color_palette = [
    "#092D34",
    "#104A56",
    "#16697A",
    "#19778A",
    "#2095AC",
    "#36B3CF",
    "#41C2DC",
    "#64CDE3",
]


# Plot bar chart
def plot_bar_chart(data, colors):
    recipe_categories = [row[0] for row in data]
    percentages = [float(row[1].strip('%')) for row in data]  # Convert "xx.xx %" to float

    # Bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(recipe_categories, percentages, color=colors[:len(recipe_categories)])

    # Add value labels
    for bar in bars:
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{bar.get_height():.2f} %",
            ha="center",
            va="bottom",
            fontsize=10
        )

    # Customization
    plt.title("Recipe Sources", fontsize=14, weight="bold")
    plt.xlabel("", fontsize=12)
    plt.ylabel("", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.ylim(0, max(percentages) + 5)
    plt.tight_layout()
    plt.show()


table_name = "recipe_sources_percentage"
data = db.fetch_data_from_db(db.db_configuration, table_name)

plot_bar_chart(data, color_palette)
