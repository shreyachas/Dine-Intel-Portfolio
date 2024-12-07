import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key='YOUR-API-KEY-HERE')

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

def verify_business_email_and_restaurant(email, restaurant):
    try:
        file_path = 'verified_emails.xlsx'
        verified_emails_df = pd.read_excel(file_path, engine='openpyxl')

        # Check if the email and restaurant are on the same row
        match = verified_emails_df[(verified_emails_df['Emails'] == email) & 
                                    (verified_emails_df['Business Name'] == restaurant)]
        return not match.empty  # True if a match is found
    except FileNotFoundError:
        st.error("Verified emails database not found. Please contact support.")
        return False
    except Exception as e:
        st.error(f"Error checking email verification: {e}")
        return False


def save_feedback(new_data):
    try:
        file_path = 'restaurant_names.csv'

        # Try reading the file with UTF-8 encoding, fallback to Latin-1 if it fails
        try:
            existing_df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            existing_df = pd.read_csv(file_path, encoding='latin1')

        # Check if the business already exists
        business_idx = existing_df[existing_df['Business Name'] == new_data['Business Name']].index
        if len(business_idx) > 0:
            # Update the existing row
            day_column = new_data['Day of Week']
            existing_df.loc[business_idx, day_column] = new_data['Traffic Status']
        else:
            # Add a new row for the business
            new_row = pd.DataFrame({
                'Business Name': [new_data['Business Name']],
                new_data['Day of Week']: [new_data['Traffic Status']],
                'Website URL': [new_data['Website URL']]
            })
            existing_df = pd.concat([existing_df, new_row], ignore_index=True)

        # Save the updated dataframe
        existing_df.to_csv(file_path, index=False, encoding='utf-8')
        return True
    except Exception as e:
        st.error(f"Error saving feedback: {e}")
        return False



def get_web_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        web_content = ""
        
        article_tags = soup.find_all('article')
        for article in article_tags:
            paragraphs = article.find_all('p')
            for p in paragraphs:
                web_content += str(p.get_text()) + '\n'
                
        return web_content, soup.title.string
    except Exception as e:
        return str(e), "Error fetching content"

def get_completion(prompt, model="gpt-3.5-turbo"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a business analysis expert providing specific, data-driven recommendations."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating completion: {e}"

# Set page configuration
st.set_page_config(
    page_title="Business Optimization",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling
st.markdown("""
    <style>
        .main-header {
            font-size: 4em;
            text-align: center;
            color: #6D4C91;  # Dark purple color
            font-weight: bold;
        }
        .sub-header {
            font-size: 2em;
            text-align: center;
            color: #6A3D9B;  # Darker purple color for sub-headers
            margin-bottom: 10px;
        }
        .tagline {
            font-style: italic;
            color: #5D6D7E;
            text-align: center;
        }
        .auth-form {
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)


# Sidebar configuration
st.sidebar.image("final logo.png", use_container_width=True)
#st.sidebar.title("DINE-INTEL")
#st.sidebar.write("DTSJ Business Optimization")

# Authentication section in sidebar
if not st.session_state.authenticated:
    available_pages = ["Home", "Foot Traffic Analysis"]
    if st.session_state.current_page not in available_pages:
        st.session_state.current_page = "Home"
else:
    available_pages = ["Home", "Foot Traffic Analysis", "Business Insights", "Foot Traffic Feedback"]

sidebar_choice = st.sidebar.radio("Navigate", available_pages)

if not st.session_state.authenticated:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Business Authentication")
    st.sidebar.markdown("Verify your business email to access premium features:")

    # Load verified emails file to populate restaurant dropdown
    try:
        file_path = 'verified_emails.xlsx'
        verified_emails_df = pd.read_excel(file_path, engine='openpyxl')
        restaurant_options = verified_emails_df['Business Name'].unique()
    except Exception as e:
        restaurant_options = []

    business_email = st.sidebar.text_input("Business email")
    selected_restaurant = st.sidebar.selectbox("Select an option", restaurant_options)

    if st.sidebar.button("Verify Email"):
        if verify_business_email_and_restaurant(business_email, selected_restaurant):
            st.session_state.authenticated = True
            st.session_state.restaurant = selected_restaurant
            st.sidebar.success("Successfully verified!")
            st.rerun()
        else:
            st.sidebar.error("Email and restaurant do not match our records.")


# Business Name
# Header
st.markdown('<div class="main-header">Dine-Intel</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">DTSJ Business Optimization</div>', unsafe_allow_html=True)
#   st.markdown('<div class="tagline">One stop shop to keep your downtown San Jose business booming</div>', unsafe_allow_html=True)

# Page Content
if sidebar_choice == "Home":
    st.write(" ")
    st.write("""
        
             
        We provide foot traffic insights for everyone—and verified Downtown SJ businesses gain exclusive access to advanced features, including:
       
        📈 Smarter Foot Traffic Insights – Attract more customers with data-backed strategies.
    
        💬 Customer Review Analysis – Decode Yelp feedback to understand your audience better.
    
        🎯 Strategic Decision-Making – Empower your business with actionable, AI-driven insights.

        🛠️ Real-Time Data – Upload feedback, spot inconsistencies in foot traffic data, and receive prompt updates to keep your insights accurate and up-to-date.

        🌟 Optimize. 🚀 Evolve. 💼 Thrive.
             
        Currently serving all Downtown San Jose eateries! More businesses to come soon...
    """)
 
 #   st.image("https://via.placeholder.com/800x300", caption="Optimize your business with AI!", use_container_width=True)

elif sidebar_choice == "Foot Traffic Analysis":
    st.write("## Foot Traffic Analysis")
    

    # URL of the webpage
    url = "https://sjdowntown.com/eat-drink/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract business info with name and cuisine type
    business_data = []
    for business in soup.find_all("div", class_="sforc-header Business_Name__c"):
        name = business.get_text(strip=True)
        cuisine = business.find_next("span", class_="sforc-description Business_Directory_Category__c").get_text(strip=True)
        business_data.append({"name": name.strip().title(), "cuisine": cuisine})


    # Extract unique cuisine options, removing any empty or whitespace-only entries
    cuisine_options = sorted({biz['cuisine'].strip() for biz in business_data if biz['cuisine'].strip()})


    # Add "Select an option" as the placeholder
    cuisine_options = ["Select an option"] + cuisine_options

    day_options = ["Select an option", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Dropdowns for cuisine and day selection
    select_cuisine = st.selectbox("Choice of Cuisine", cuisine_options)
    select_day = st.selectbox("Day of the Week", day_options)

    file_path = r'restaurant_names.csv'
    try:
        # Attempt to read the file with UTF-8 encoding
        with open(file_path, encoding='utf-8', errors='replace') as f:
            foot_traffic_df = pd.read_csv(f)
    except UnicodeDecodeError:
        # Fallback to a different encoding if UTF-8 fails
        foot_traffic_df = pd.read_csv(file_path, encoding='latin-1')
    except Exception as e:
        st.error(f"An error occurred while reading the CSV file: {e}")
    # Preprocess foot traffic data
    foot_traffic_df['Business Name'] = foot_traffic_df['Business Name'].str.strip().str.title()

    if select_cuisine != "Select an option":
        # Filter businesses by selected cuisine
        filtered_businesses = [biz for biz in business_data if biz['cuisine'] == select_cuisine]
        business_names = [biz['name'].strip().title() for biz in filtered_businesses]

        # Filter traffic data for matching businesses
        filtered_traffic_df = foot_traffic_df[foot_traffic_df['Business Name'].isin(business_names)]

        if not filtered_traffic_df.empty:
            required_columns = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            if all(col in filtered_traffic_df.columns for col in required_columns):
                # Plot based on selected day
                if select_day != "Select an option":
                    st.write(f"Foot Traffic for Businesses under '{select_cuisine}' Cuisine on {select_day}")
                    filtered_traffic_df.set_index('Business Name')[select_day].plot(kind='barh', color='pink', figsize=(10, 6))
                    plt.title(f"Foot Traffic on {select_day} for Businesses under '{select_cuisine}' Cuisine")
                    plt.xlabel('Foot Traffic')
                    plt.ylabel('Business Name')
                    plt.xticks(rotation=0)
                    st.pyplot(plt)
                else:
                    # Default bar chart for all days
                    st.write(f"Foot Traffic for Businesses under '{select_cuisine}' Cuisine")
                    filtered_traffic_df.set_index('Business Name')[required_columns].plot(kind='bar', figsize=(10, 6))
                    plt.title(f"Foot Traffic by Day for Businesses under '{select_cuisine}' Cuisine")
                    plt.ylabel('Foot Traffic')
                    plt.xlabel('Business Name')
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(plt)
            else:
                st.write("Required columns for plotting are missing.")
        else:
            st.write("No data available for the selected cuisine.")
   

elif sidebar_choice == "Business Insights" and st.session_state.authenticated:
    st.write(f"## Business Intelligence Dashboard for {st.session_state.restaurant}")

    # Load the CSV file containing foot traffic data
    file_path = 'restaurant_names_BI.csv'
    try:
        foot_traffic_df = pd.read_csv(file_path, encoding='utf-8')

        # Filter data for the authenticated restaurant
        filtered_data = foot_traffic_df[foot_traffic_df['Business Name'] == st.session_state.restaurant]

        if filtered_data.empty:
            st.error("No data available for your restaurant.")
        else:
            # Ask for Yelp URL
            st.write("### Yelp Insights")
            yelp_url = st.text_input(f"Enter Yelp URL for {st.session_state.restaurant}:")

            if st.button("Generate Insights"):
                if not yelp_url:
                    st.warning("Please provide a Yelp URL to generate insights.")
                else:
                    # Generate insights using OpenAI
                    def generate_summary_and_insights(business_name, yelp_url):
                        prompt = (
                            f"Summarize the Yelp page for the business {business_name}. "
                            f"Include the following details in your summary: "
                            f"1. The overall Yelp rating (out of 5 stars) and the total number of reviews on the {yelp_url} page. "
                            f"2. Key themes in customer feedback, such as what customers like most (e.g., service, food quality, ambiance) and common complaints (e.g., wait times, price, specific issues). "
                            f"3. Highlight any recurring phrases or sentiments found in the reviews. "
                            f"Ensure the summary is concise for the business owner."                        )
                        return get_completion(prompt)

                    def get_completion(prompt, model="gpt-3.5-turbo"):
                        client = OpenAI(api_key='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')
                        completion = client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "system", "content": "You are an AI business consultant focused on providing specific, actionable insights for small businesses. You should generate recommendations based on market trends, foot traffic data, Yelp reviews, and the business's unique background."\
                                "Your insights should be concise, actionable, and focused on delivering value to the business owner. Recommendations should be clear, structured, and aligned with industry best practices."\
                                "Each recommendation should have a direct impact on customer satisfaction, revenue growth, or operational efficiency."\
                                "Structure each recommendation as numbered lists to improve readability"},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        return completion.choices[0].message.content

                    summary = generate_summary_and_insights(st.session_state.restaurant, yelp_url)
                    st.subheader("Yelp Business Summary")
                    st.write(summary)

                    # Display other insights in tabs
                    st.subheader("Detailed Insights")
                    tab1, tab2, tab3 = st.tabs(["🍽️ Menu", "👩‍🍳 Staffing", "📣 Advertising"])

                    # Menu Insights Tab
                    with tab1:
                        st.write(f"Menu recommendations for {st.session_state.restaurant}.")
                        menu_prompt = (
                            f"Provide three personalized menu recommendations for {st.session_state.restaurant}. "
                            f"You are a business consultant tasked with creating personalized menu recommendations for the business {st.session_state.restaurant}. "
                            f"Browse the web for relevant customer reviews, menu details, and trends specific to {st.session_state.restaurant} cuisine to ensure tailored suggestions. "
                            f"Provide 3 recommendations, each with concise actionable sentences and relevant emojis for sub-bullet points to emphasize specific steps. "
                            f"Use phrases like 'We recommend adding...' or 'We suggest optimizing...' to make the recommendations practical for a small business." )
                        menu_insights = get_completion(menu_prompt)
                        st.write(menu_insights)

                    # Staffing Insights Tab
                    with tab2:
                        st.write(f"Staffing recommendations based on foot traffic for {st.session_state.restaurant}.")
                        if not filtered_data.empty:
                            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                            traffic_data = filtered_data.iloc[0][days]
                            highest_traffic_day = traffic_data.idxmax()
                            highest_traffic_value = traffic_data.max()

                            st.write(f"**Highest Traffic Day:** {highest_traffic_day}")
                            st.write(f"**Visitor Count:** {highest_traffic_value}")

                            staffing_prompt = (
                                      f"Provide 3 actionable staffing recommendations for the business {st.session_state.restaurant}, "
                                    f"focusing on the day with the highest foot traffic: {highest_traffic_day} "
                                    f"(with {highest_traffic_value} visitors). "
                                    f"Each recommendation should be concise, straight to the point, and actionable for small businesses. "
                                    f"Use relevant emojis for sub-bullet points to emphasize specific steps."
                                    f"Tailor the recommendations uniquely to the nature of the business based on its name and foot traffic data."
                                    f"Use phrases like 'We recommend adding...' or 'We suggest optimizing...' to make the recommendations practical for a small business."
                                            )
                            staffing_insights = get_completion(staffing_prompt)
                            st.write(staffing_insights)

                    # Advertising Insights Tab
                    with tab3:
                        st.write(f"Advertising strategies for {st.session_state.restaurant}.")
                        advertising_prompt = (

                            f"For the business  {st.session_state.restaurant}, create 3 tailored advertising strategies. "
                            f"Leverage web research, reviews, and industry trends to suggest ideas that stand out for this specific business. "
                            f"Each recommendation should be concise, actionable, and include relevant emojis for sub-bullet points to emphasize specific steps. "
                            f"Use phrases like 'We recommend collaborating with...' or 'We suggest running...' to make each suggestion clear and implementable for a small business."
                        )
                        advertising_insights = get_completion(advertising_prompt)
                        st.write(advertising_insights)

    except Exception as e:
        st.error(f"Error loading business insights: {e}")




elif sidebar_choice == "Foot Traffic Feedback" and st.session_state.authenticated:
    st.write(f"## Provide Foot Traffic Feedback for {st.session_state.restaurant}")

    try:
        # Select the day of the week and traffic status
        day_of_week = st.radio('What day are you providing input for:', 
                                ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        traffic_status = st.slider(
            'How crowded is this place? (0 = very empty, 5 = very crowded)',
            min_value=0,
            max_value=5,
            value=2,
            step=1
        )
        #website_url = st.text_input('Business website URL (optional):')

        # Submit feedback button
        if st.button('Submit Feedback'):
            feedback_data = {
                'Business Name': st.session_state.restaurant,
                'Day of Week': day_of_week,
                'Traffic Status': traffic_status,
                #'Website URL': website_url
            }

            if save_feedback(feedback_data):
                st.success("Thank you for your feedback! The foot traffic data has been updated.")

                # Show current data for the restaurant
                st.write(f"### Current Foot Traffic Data for {st.session_state.restaurant}")
                updated_df = pd.read_csv('restaurant_names.csv')
                business_data = updated_df[updated_df['Business Name'] == st.session_state.restaurant]

                if not business_data.empty:
                    traffic_data = business_data.iloc[0][['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
                    
                    # Plot the traffic data
                    plt.figure(figsize=(10, 6))
                    plt.bar(traffic_data.index, traffic_data.values, color='lightcoral')
                    plt.title(f"Weekly Foot Traffic - {st.session_state.restaurant}")
                    plt.xlabel("Day of the Week")
                    plt.ylabel("Traffic Level (0-5)")
                    plt.xticks(rotation=45)
                    st.pyplot(plt)
                else:
                    st.warning("No feedback data available for your restaurant yet.")
    except Exception as e:
        st.error(f"Error loading or submitting feedback: {e}")


# Footer
st.markdown("---")
st.markdown("""
    <style>
        .footer {
            text-align: center;
            color: #888;
            font-size: 0.8em;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown('<div class="footer">© 2024 Dine-Intel. All rights reserved.</div>', unsafe_allow_html=True)