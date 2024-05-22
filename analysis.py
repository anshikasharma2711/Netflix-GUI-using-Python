import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Load the Netflix data
df = pd.read_csv("netflix_data.csv")

# Define login credentials
LOGIN_ID = 'netflix'
PASSWORD = 'anshika'

# Main function to create Streamlit app
def main():
    st.set_page_config(page_title='Netflix App', page_icon='🎬', layout='wide')

    # Initialize session state if not already present
    if 'is_logged_in' not in st.session_state:
        st.session_state.is_logged_in = False

    # Display login page if not logged in
    if not st.session_state.is_logged_in:
        login_success = login()

        if login_success:
            st.session_state.is_logged_in = True
            st.success('Login Successful!')

    # Display main content if logged in
    if st.session_state.is_logged_in:
        st.title('Welcome to Netflix App')
        st.image('netflix_logo.png', width=200)

        # Display tabs for navigation
        selected_tab = display_tabs()
        
        if selected_tab == 'Home':
            display_home_content()
        elif selected_tab == 'Movies & TV Shows':
            display_movies_content()
        elif selected_tab == 'EDA':
            display_EDA_content() # type: ignore
        elif selected_tab == 'Suggestions':
            display_suggestions()

# Function to display login page and authenticate user
def login():
    st.title('Netflix App - Login')

    login_id = st.text_input('Enter ID:')
    password = st.text_input('Enter Password:', type='password')

    if st.button('Login'):
        if login_id == LOGIN_ID and password == PASSWORD:
            return True
        else:
            st.error('Invalid ID or Password. Please try again.')
    return False

# Function to display tabs for navigation
def display_tabs():
    selected_tab = ui.tabs(options=['Home', 'Movies & TV Shows', 'EDA', 'Suggestions'], default_value='Home', key="kanaries")
    return selected_tab

# Function to display content for Home tab
def display_home_content():
    st.header('Netflix - Home')

    # Genre Exploration Section
    explore_genres()

# Function to display genre exploration section and interactive bar graph
def explore_genres():
    st.subheader('Explore Genres')

    # Define the desired genres for the dropdown
    desired_genres = [
        'Documentaries',
        'International Movies',
        'Comedies',
        'Dramas',
        'Independent Movies',
        'Thrillers',
        'Action & Adventure',
        'Children & Family Movies',
        'Stand-Up Comedy',
        'Cult Movies'
    ]

    # Dropdown to select a genre
    selected_genre = st.selectbox('Select Genre', options=desired_genres)

    # Filter dataset by selected genre and display top 5 movies
    genre_content = df[df['listed_in'].str.contains(selected_genre) & (df['type'] == 'Movie')]

    # Display top 5 movies for the selected genre
    if not genre_content.empty:
        st.write(f"**Top 5 {selected_genre} Movies**")
        for _, content in genre_content.head(5).iterrows():
            st.write(f"- **{content['title']}** ({content['release_year']})")
    else:
        st.write(f"No movies found for {selected_genre}")

    # Calculate top 10 genres by count
    top_genres = df['listed_in'].str.split(', ', expand=True).stack().value_counts().head(10)

    # Create an interactive horizontal bar chart using Plotly
    fig = px.bar(top_genres, x=top_genres.values, y=top_genres.index, orientation='h',
                 labels={'x': 'Count', 'y': 'Genre'}, title='Top 10 Genres by Count')

    # Display the bar chart
    st.plotly_chart(fig)

# Function to display content for Movies & TV Shows tab
def display_movies_content():
    st.header('Netflix - Movies & TV Shows')
    st.write('Browse our extensive collection of Movies & TV Shows.')

    # Define options for dropdown selection
    plot_options = [
        'Distribution of Content',
        'Cumulative Number of Movies & TV Shows Over Years',
        'Top 10 Countries Producing Movies',
        'Top 10 Countries Producing TV Shows'
    ]

    # Dropdown to select the plot
    selected_plot = st.selectbox('Select Plot', plot_options)

    # Calculate content type distribution
    content_type_counts = df['type'].value_counts()

    # Create a stacked area plot with Netflix-like colors
    movies_cumulative = df[df['type'] == 'Movie']['release_year'].value_counts().sort_index().cumsum()
    tv_shows_cumulative = df[df['type'] == 'TV Show']['release_year'].value_counts().sort_index().cumsum()
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(x=movies_cumulative.index, y=movies_cumulative,
                                   mode='lines', name='Movies', fill='tozeroy', line=dict(color='#E50914')))
    fig_area.add_trace(go.Scatter(x=tv_shows_cumulative.index, y=tv_shows_cumulative,
                                   mode='lines', name='TV Shows', fill='tozeroy', line=dict(color='#000000')))
    fig_area.update_layout(xaxis_title='Release Year', yaxis_title='Cumulative Count',
                           legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

    # Plot selection based on dropdown value
    if selected_plot == 'Distribution of Content':
        # Create an interactive pie chart using Plotly
        fig = px.pie(content_type_counts, values=content_type_counts.values, names=content_type_counts.index,
                     color_discrete_sequence=['#E50914', '#221f1f'])
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.subheader('Distribution of Content')
        st.plotly_chart(fig)

    elif selected_plot == 'Cumulative Number of Movies & TV Shows Over Years':
        st.subheader('Cumulative Number of Movies & TV Shows Over Years')
        st.plotly_chart(fig_area)

    elif selected_plot == 'Top 10 Countries Producing Movies':
        # Filter the dataset to include only movies
        movies = df[df['type'] == 'Movie']
        movie_countries = movies['country'].value_counts().head(10)
        fig = px.bar(
            movie_countries,
            orientation='h',
            labels={'index': 'Country', 'value': 'Number of Movies'}
        )
        fig.update_traces(marker_color='black')
        fig.update_layout(
            xaxis_title='Number of Movies',
            yaxis_title='Country',
            yaxis=dict(autorange='reversed'),
            margin=dict(l=100)
        )
        st.subheader('Top 10 Countries Producing Movies')
        st.plotly_chart(fig)

    elif selected_plot == 'Top 10 Countries Producing TV Shows':
        # Filter the dataset to include only TV shows
        tv_shows = df[df['type'] == 'TV Show']
        tv_show_countries = tv_shows['country'].value_counts().head(10)
        fig = px.bar(
            tv_show_countries,
            orientation='h',
            labels={'index': 'Country', 'value': 'Number of TV Shows'}
        )
        fig.update_traces(marker_color='#E50914')
        fig.update_layout(
            xaxis_title='Number of TV Shows',
            yaxis_title='Country',
            yaxis=dict(autorange='reversed'),
            margin=dict(l=100)
        )
        st.subheader('Top 10 Countries Producing TV Shows')
        st.plotly_chart(fig)


# Function to display content for EDA tab
def display_EDA_content():
    st.header('Netflix - EDA')
    st.write('Some more visualization of the data')


    # Create a dropdown menu to select the type of analysis
    analysis_type = st.selectbox('Select Analysis', ['Content Added Over Month', 'Top 10 Countries Adding Content',
                                                      'Content Addition Over Time', 'Distribution of Movie Ratings'])

    if analysis_type == 'Content Added Over Month':
        display_content_added_over_month()
    elif analysis_type == 'Top 10 Countries Adding Content':
        display_top_10_countries_content()
    elif analysis_type == 'Content Addition Over Time':
        display_content_addition_over_time()
    elif analysis_type == 'Distribution of Movie Ratings':
        display_movie_ratings_distribution()
    

# Function to display content added over month 
def display_content_added_over_month():
    st.subheader('Content Added Over Month')

    # Convert 'date_added' column to datetime format
    df['date_added'] = pd.to_datetime(df['date_added'])

    # Extract month from 'date_added' and count the number of titles added in each month
    df['added_month'] = df['date_added'].dt.month
    monthly_counts = df['added_month'].value_counts().sort_index()

    # Map month numbers to month names for better readability
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_counts.index = [month_names[int(month)-1] for month in monthly_counts.index]

    # Create a bar chart using Plotly Express with custom color settings
    fig = px.bar(x=monthly_counts.index, y=monthly_counts.values,
                 labels={'x': 'Month', 'y': 'Number of Titles Added'},
                 title='Content Added Over Month',
                 color_discrete_sequence=['#000000'])

    # Customize layout and display the plot
    fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': month_names},
                      yaxis_title='Number of Titles Added')

    # Display the plot within Streamlit
    st.plotly_chart(fig)

# Function to remove rows with missing 'country' values and plot top 10 countries
def display_top_10_countries_content(): # type: ignore
    st.subheader('Top 10 Countries Adding Content')

    # Remove rows with missing 'country' values
    netflix_filtered = df.dropna(subset=['country'])

    # Count the number of titles from each country
    country_counts = netflix_filtered['country'].value_counts().sort_values(ascending=False)

    # Select the top 10 countries with the most content
    top_countries = country_counts.head(10)

    # Create a horizontal bar chart using Plotly
    fig = px.bar(x=top_countries.values[::-1], y=top_countries.index[::-1],
                 orientation='h', labels={'x': 'Number of Titles', 'y': 'Country'},
                 title='Top 10 Countries with the Most Netflix Content',
                 color_discrete_sequence=['#E50914', '#221f1f']*10)

    # Customize the layout
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    # Display the bar chart
    st.plotly_chart(fig)

# Parse the 'date_added' column with the correct format
df['date_added'] = pd.to_datetime(df['date_added'], format='%d-%b-%y', errors='coerce')

# Adding a 'month_year_added' column for aggregation
df['month_year_added'] = df['date_added'].dt.to_period('M')

# Prepare data for visualizations
# Content Addition Over Time
addition_trends = df.groupby('month_year_added').size().reset_index(name='Count')
addition_trends['month_year_added'] = addition_trends['month_year_added'].dt.strftime('%Y-%m')  # Format for better visualization

# Function to display Content Addition Over Time 
def display_content_addition_over_time():
    st.subheader('Content Addition Over Time')

    # Create the area chart using Plotly Express
    fig = px.area(addition_trends, x='month_year_added', y='Count', title='Content Added Over Time')
    fig.update_layout(xaxis_title='Year', yaxis_title='Number of Titles')

    # Display the area chart within Streamlit
    st.plotly_chart(fig)

# Filter the dataset to include only movies
movies = df[df['type'] == 'Movie']

# Count the number of movies in each rating category
rating_counts = movies['rating'].value_counts()

# Function to display Distribution of Movie Ratings
def display_movie_ratings_distribution():
    st.subheader('Distribution of Movie Ratings on Netflix')

    # Create a bar plot using Plotly Express with red and black colors
    fig = px.bar(x=rating_counts.index, y=rating_counts.values, 
                 labels={'x': 'Rating', 'y': 'Number of Movies'},
                 title='Distribution of Movie Ratings on Netflix',
                 color_discrete_sequence=['#E50914', '#221f1f'])  # Red and black colors

    # Rotate x-axis labels for better readability
    fig.update_layout(xaxis_tickangle=-45)

    # Display the plot within Streamlit
    st.plotly_chart(fig)   


# Function to display content for Suggestions tab
def display_suggestions():
    st.header('Netflix - Suggestions')
    st.write("Discover personalized recommendations based on your preferences.")

    # User input widgets for preferences
    preferred_genres = st.multiselect("Select Preferred Genres", df['listed_in'].unique())
    min_release_year, max_release_year = st.slider("Select Release Year Range",
                                                   min_value=int(df['release_year'].min()),
                                                   max_value=int(df['release_year'].max()),
                                                   value=(int(df['release_year'].min()), int(df['release_year'].max())))

    # Filter data based on user preferences (genres and release year range)
    filtered_data = df[(df['listed_in'].isin(preferred_genres)) &
                       (df['release_year'] >= min_release_year) &
                       (df['release_year'] <= max_release_year)]

    if len(filtered_data) == 0:
        st.warning("No content matching the selected criteria.")
    else:
        st.subheader("Recommended Content")
        st.write("Here are some recommendations based on your preferences:")
        st.write(filtered_data[['title', 'listed_in', 'release_year', 'rating']])

        # Display interactive visualization based on filtered data (e.g., genre distribution)
        fig = px.histogram(filtered_data, x='listed_in', title='Genre Distribution of Recommended Content')
        st.plotly_chart(fig)

# Run the app
if __name__ == '__main__':
    main()
