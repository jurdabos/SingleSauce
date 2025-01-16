import pandas as pd

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

# Initialize a consolidated results dictionary
consolidated_results = {}

# Process each research study to calculate weighted averages
for research in research_data:
    weight = research["respondents"] / total_respondents
    for category, value in research["results"].items():
        if category not in consolidated_results:
            consolidated_results[category] = 0
        consolidated_results[category] += value * weight

# Convert consolidated results to a sorted DataFrame for better readability
consolidated_df = pd.DataFrame(
    consolidated_results.items(), columns=["Category", "Weighted Average"]
).sort_values(by="Weighted Average", ascending=False)

# Display the consolidated results table
print("Total Respondents:", total_respondents)
print(consolidated_df)

# Export the results to a CSV file
consolidated_df.to_csv("consolidated_recipe_sources.csv", index=False)
