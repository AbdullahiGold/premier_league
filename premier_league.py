import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# API Key
api_key = 'b26ecbfb77544826a22d66df0f654ef1'


# Function to fetch Premier League standings data
def get_standings():
    url = f"https://api.football-data.org/v4/competitions/PL/standings"
    headers = {'X-Auth-Token': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        standings = data['standings'][0]['table']
        return standings
    else:
        st.error("Failed to fetch standings.")
        return None


# Function to create a DataFrame for the standings
def create_standings_df(standings_data):
    teams_data = []
    for team in standings_data:
        teams_data.append({
            'Team Name': team['team']['name'],
            'Played': team['playedGames'],
            'Won': team['won'],
            'Draw': team['draw'],
            'Lost': team['lost'],
            'Points': team['points'],
            'Goals Scored': team['goalsFor'],
            'Goals Conceded': team['goalsAgainst'],
            'Goal Difference': team['goalDifference']
        })

    standings_df = pd.DataFrame(teams_data)
    return standings_df


# Function to fetch Premier League top scorers data
def get_top_scorers():
    url = f"https://api.football-data.org/v4/competitions/PL/scorers"
    headers = {'X-Auth-Token': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()['scorers']
        return data
    else:
        st.error("Failed to fetch top scorers data.")
        return None


# Function to create a DataFrame for the top scorers
def create_scorers_df(scorers_data):
    players_data = []
    for scorer in scorers_data:
        players_data.append({
            'Player Name': scorer['player']['name'],
            'Team': scorer['team']['name'],
            'Goals': scorer['goals']
        })

    scorers_df = pd.DataFrame(players_data)
    return scorers_df


# Function to plot a sunburst chart for teams and top scorers with custom hover text
def plot_sunburst_chart(df):
    df = df[df['Goals'] > 0]  # Ensure we have goals > 0

    if df.empty:
        st.error("No data available for players with goals.")
        return None

    fig = px.sunburst(
        df,
        path=['Team', 'Player Name'],
        values='Goals',
        color='Goals',
        color_continuous_scale='RdYlGn',
        custom_data=['Player Name', 'Team', 'Goals']  # Define custom data for hover
    )

    fig.update_traces(
        hovertemplate="<br>Player = %{customdata[0]}<br>Club = %{customdata[1]}<br>Goals = %{customdata[2]}"
    )

    fig.update_layout(
        title='Top Scorers and Their Teams'
    )

    return fig


# Function to plot the win/draw/loss distribution as a stacked bar chart
def plot_win_draw_loss_distribution(df):
    df['Win'] = df['Won']
    df['Draw'] = df['Draw']
    df['Loss'] = df['Lost']
    df = df[['Team Name', 'Win', 'Draw', 'Loss']]

    fig = px.bar(
        df,
        x='Team Name',
        y=['Win', 'Draw', 'Loss'],
        labels={'value': 'Matches', 'Team Name': 'Team'},
        color_discrete_map={'Win': 'green', 'Draw': 'gray', 'Loss': 'red'}
    )

    fig.update_layout(
        title='Win/Draw/Loss Distribution by Team'
    )

    return fig


# Function to plot goals scored vs. goals conceded as a scatter plot
def plot_goals_scored_vs_conceded(df):
    fig = px.scatter(
        df,
        x='Goals Scored',
        y='Goals Conceded',
        color='Team Name',
        size='Points',
        title='Goals Scored vs. Goals Conceded',
        labels={'Goals Scored': 'Goals Scored', 'Goals Conceded': 'Goals Conceded'}
    )

    return fig


# Main Streamlit app
def main():
    st.set_page_config(layout="wide")

    # Title of the dashboard
    st.markdown("## Premier League Dashboard")

    # Fetch Premier League standings
    standings = get_standings()
    if standings is not None:
        standings_df = create_standings_df(standings)

        # Sidebar: Display Premier League standings table
        st.sidebar.markdown("### Premier League Standings")
        st.sidebar.dataframe(standings_df)
        st.sidebar.header("Purpose")
        info = st.sidebar.info(
            "This dashboard offers insights into Premier League standings and top scorers. It features visualizations of team performance, win/loss distributions, and detailed top scorer stats to help users easily grasp the league's dynamics.")

        # Fetch actual top scorers data
        top_scorers = get_top_scorers()
        if top_scorers is not None:
            top_scorers_df = create_scorers_df(top_scorers)

            # Create and display charts
            col1, col2 = st.columns(2)

            with col1:
                goals_scored_vs_conceded_fig = plot_goals_scored_vs_conceded(standings_df)
                st.plotly_chart(goals_scored_vs_conceded_fig)

            with col2:
                sunburst_fig = plot_sunburst_chart(top_scorers_df)
                if sunburst_fig:
                    st.plotly_chart(sunburst_fig)

            # Win/Draw/Loss Distribution Chart
            win_draw_loss_fig = plot_win_draw_loss_distribution(standings_df)
            st.plotly_chart(win_draw_loss_fig)




# Run the app
if __name__ == "__main__":
    main()
