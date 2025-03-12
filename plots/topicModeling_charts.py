from bertopic import BERTopic  # Ensure you have BERTopic installed
import plotly.graph_objects as go  # BERTopic visualization uses Plotly
import plotly.colors as pc
import plotly.express as px

xaxis_font_size=14
ticks_size=14


def topicDistribution(topic_model, top_n_topics=6, n_words=5):
    content_topics_barchart = topic_model.visualize_barchart(top_n_topics=top_n_topics, n_words=n_words)
    colors = pc.qualitative.Plotly
    for i, trace in enumerate(content_topics_barchart.data):
        trace.marker.color = colors[i % len(colors)]  # Cycle through colors

    content_topics_barchart.update_layout(title_text="")  # Remove the title

    return content_topics_barchart


####################
# TOPIC FREQUENCY
###################


def create_topicFreq_chart(topics_df):

    # Create a new column "top_words" that holds the top 5 words for each topic.
    # `topic_model.get_topic(topic)` returns a list of (word, score) tuples.
    topics_df['top_5_words'] = topics_df.iloc[:,3].apply(lambda x: ', '.join(x[:5]) if isinstance(x, list) else x)
    # Create the bar chart using Plotly Express.
    # Pass the "top_words" column as custom data for use in the hover template.
    topicFreq_barchart = px.bar(
        topics_df,
        x="Topic Name",
        y="Count",
        custom_data=["top_5_words"],
        title=None,
        labels={"Count": "Frequency", "Topic": "CutomName"},
    )

    # Update traces to include custom hover text showing the top 5 words.
    topicFreq_barchart.update_traces(
        marker_color='#646DEF',
        textposition='outside',
        hovertemplate=(
            'Frequency: %{y}<br>'
            'Top 5 words: %{customdata[0]}<extra></extra>'
        )
    )

    topicFreq_barchart.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        xaxis_title="Topic Name",
        yaxis_title="Frequency",
        height=650,
        xaxis=dict(title_font=dict(size=xaxis_font_size), tickfont=dict(size=ticks_size)),

    )

    return topicFreq_barchart

###############################
# Stacked Topic Freq Per Class
###############################

def create_stacked_topics_per_class(df, title, height=550):
    df['top_5_words'] = df['Words'].apply(lambda x: ', '.join(x[:5]) if isinstance(x, list) else x)

    topics_per_class_chart = px.bar(
                df,
                x="CustomName",        # Classes on the x-axis
                y="Frequency",        # Count of documents per topic
                custom_data=['top_5_words'],
                color='Class',    # Different colors for different topics
                title=title,
                barmode="stack",   # Stacked bars
                labels={"Count": "Frequency", "Topics":"CustomName"},
                color_discrete_sequence=px.colors.qualitative.Plotly  # Ensures different colors

                )

    topics_per_class_chart.update_traces(
            hovertemplate=(
                'Frequency: %{y}<br>'
                'Top 5 words: %{customdata[0]}<extra></extra>'
                )
            )
 
    topics_per_class_chart.update_layout(
        xaxis_title="Topic Name",
        yaxis_title="Frequency",
        height=height,
        margin=dict(l=50, r=50, t=50, b=150),
   )

    return topics_per_class_chart

#######################
# Intertopic Distance
#######################

def intertopicDistanceMap(topic_model, color="orangered"):
    # Generate the base figure
    fig = topic_model.visualize_topics(
            title="")

    # Update trace colors
    for trace in fig.data:
        trace.marker.color = color 
        trace.marker.line.width = 0

    fig.update_layout(
            margin=dict(r=50)
            )

    return fig



##########################
# Topics Over Time
#########################

def create_topics_overtime_chart(topics_overtime_df, title):
    topics_overtime_chart = px.line(
            topics_overtime_df,
            x="Timestamp",
            y="Frequency",
            color="CustomName",
            markers=True,
            title=title,
            labels={"Timestamp": "Time", "Frequency": "Topic Frequency", "Name": "CustomName"},
            color_discrete_sequence=px.colors.qualitative.Plotly  # Ensures different colors
        )

    topics_overtime_chart.update_layout(
        xaxis_title="Time",
        yaxis_title="Frequency",
        legend_title="Topics",
        height=700,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.5,  # Adjust this value as needed to move the legend further down
            xanchor="center",
            x=0.5
        )
    )

    return topics_overtime_chart
