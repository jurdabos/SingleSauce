import pandas as pd
from tabulate import tabulate

# Data for user stories and tasks
data = {
    "User Story": [
        "As a user, I want to access recipes by category (e.g., meaty, fishy, allergen-free), so I can have a look at concrete options when I already decided on the meal type.",
        "As a user, I want to search recipes by single or multiple ingredients, so I can view what I can create from the ingredients at home.",
        "As a Spanish-speaking user, I want the app to support Spanish so I can interact with it easily.",
        "As a user living with disabilities, I want the app to be accessible in order for me to be able to use it on my own.",
        "As a user, I want to import recipes from external sources (e.g., Instagram) to have a centralized repo for all my recipes.",
        "As a new cook, I want beginner-friendly recipes with step-by-step guides to make it convenient for me to prepare meals.",
        "As a busy parent, I want quick and easy recipes to make sure I can cook and still be able to spend time with my kids.",
        "As a user, I want to share recipes with family, so everyone (the one getting groceries, prepping veggies, etc.) is in the know.",
        "As a part-time worker, I want recipe stories for inspiration so I can get to know more about what I am cooking.",
        "As a tester, I need a sandbox environment for beta testing."
    ],
    "Tasks": [
        "1. Design the hierarchical categorization schema for recipes (e.g., meal types, allergens).\n"
        "2. Implement a database schema to store category metadata.\n"
        "3. Develop the user interface for category-based recipe browsing.\n"
        "4. Integrate OLAP capabilities for querying recipe dimensions (e.g., filtering by allergen, meal type).\n"
        "5. Write unit and integration tests for category-based browsing functionality.",

        "1. Design the search interface for ingredient-based queries.\n"
        "2. Implement backend support for single-ingredient searches.\n"
        "3. Extend backend support to handle multi-ingredient searches with contextual recognition.\n"
        "4. Integrate AI-powered contextual ingredient recognition for ingredient substitution or combinations.\n"
        "5. Develop a mechanism to display search results ranked by relevance.\n"
        "6. Test the search functionality for edge cases (e.g., missing or incomplete ingredient data).",

        "1. Identify all text elements in the app that need translation.\n"
        "2. Integrate a localization framework to support multiple languages.\n"
        "3. Translate UI elements, error messages, and notifications into Spanish.\n"
        "4. Implement a language toggle feature in the app settings.\n"
        "5. Perform usability testing with Spanish-speaking users to ensure linguistic accuracy and cultural relevance.",

        "1. Research accessibility requirements and best practices (e.g., WCAG, European Accessibility Act).\n"
        "2. Implement visually accessible design elements (e.g., font size, color contrast).\n"
        "3. Add screen reader compatibility for all UI elements.\n"
        "4. Ensure keyboard navigation for all functionalities.\n"
        "5. Test the app with users living with disabilities and refine features based on feedback.",

        "1. Identify and document external sources to be supported (e.g., Instagram, blogs, recipe websites).\n"
        "2. Develop ETL pipelines to extract recipe data from external sources.\n"
        "3. Implement data transformation to align imported data with the app's database schema.\n"
        "4. Develop an interface for users to connect to external sources and initiate imports.\n"
        "5. Test the import functionality for various formats and sources.",

        "1. Add a 'beginner-friendly' dimension to the recipe categorization schema.\n"
        "2. Create a guided cooking mode for step-by-step instructions.\n"
        "3. Design visual indicators (e.g., 'Beginner-friendly' badges) for relevant recipes.\n"
        "4. Develop onboarding tutorials for new users.\n"
        "5. Conduct user testing with beginner cooks to ensure ease of use.",

        "1. Add a 'cooking time' property to the recipe metadata.\n"
        "2. Implement a feature to filter recipes by preparation time.\n"
        "3. Redesign the recipe list view to prominently display cooking times.\n"
        "4. Develop a 'Quick Recipes' section for frequently accessed short-prep recipes.\n"
        "5. Test the feature for usability and accuracy of cooking times.",

        "1. Design the schema for group/collaborative recipe libraries.\n"
        "2. Implement user group functionality with role-based access (e.g., view-only, edit permissions).\n"
        "3. Add the ability to share recipes via links or invites.\n"
        "4. Create a notification system to alert users about changes or updates to shared recipes.\n"
        "5. Test the sharing and collaboration features with mock user groups.",

        "1. Integrate an editorial design framework to support narrative elements (e.g., origin stories, chef tips).\n"
        "2. Develop a content management system (CMS) for creating and managing recipe stories.\n"
        "3. Design a section in the app to showcase recipe stories.\n"
        "4. Collaborate with content creators to populate the CMS with initial content.\n"
        "5. Test the feature with users to ensure engagement and inspiration.",

        "1. Set up a dedicated testing environment separate from the production environment.\n"
        "2. Develop mock data for testing various use cases.\n"
        "3. Implement logging and debugging tools for testers.\n"
        "4. Create a feedback submission interface for beta testers.\n"
        "5. Regularly review and act on feedback received from the sandbox environment."
    ]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save the table to a CSV file
file_path = "user_stories_tasks_table.csv"
df.to_csv(file_path, index=False)
# Pandas display options
pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.max_columns', None)
pd.options.display.float_format = '{: .2f}'.format
print(df)
