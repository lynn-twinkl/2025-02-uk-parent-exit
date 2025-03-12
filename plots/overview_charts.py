import plotly.express as px

legend_font_size=14
xaxis_font_size=16
ticks_size=14

## -- WORD COUNT PLOT

def create_word_count_histogram(df, nbins=40, height=550):

    fig = px.histogram(
        df,
        x='word-count',
        nbins=nbins,
        title=None,
        color_discrete_sequence=['#646DEF']
    )
    
    fig.update_layout(
        height=height,
        margin=dict(t=30),
    )
    
    return fig

## -- SENTIMENT PLOT

def create_sentiment_pie(df, height=450):

    sentiment_pie = px.pie(
        df, 
        names='sentiment',
        color='sentiment',
        color_discrete_map={ 'Positive':'darkturquoise', 'Neutral':'#646DEF', 'Negative':'red'},
        hole=0.45,
        title=None
    )

    sentiment_pie.update_traces(hovertemplate='%{label}<extra></extra>')

    sentiment_pie.update_layout(
            showlegend=False,
            margin=dict(r=50),
            legend=dict(
                font=dict(size=legend_font_size),
                orientation="h",  # Vertical orientation
                x=0.5,
                xanchor="center",
        )
    )
    return sentiment_pie

## -- CANCELLATION REASONS

def create_cancellation_reasons_plot(cancellation_overview):

    reasons_bar = px.bar(
    cancellation_overview,
    x='Category',
    y='Count',
    color_discrete_sequence=['#646DEF'],
    color_discrete_map={'Low':'darkturquoise', 'Medium':'orangered', 'High':'red'},
)

    reasons_bar.update_traces(
        customdata=cancellation_overview['Percentage'],
        hovertemplate='Count = %{y}<br>Percentage = %{customdata}%'
        )

    reasons_bar.update_layout(
        height=600,
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(title_font=dict(size=xaxis_font_size), tickfont=dict(size=ticks_size)), 
        # yaxis=dict(title_font=dict(size=xaxis_font_size), tickfont=dict(size=ticks_size)),
        # yaxis_title=None,
        # margin=dict(r=70),
        # legend=dict(
        #    font=dict(size=legend_font_size),
         #   orientation='h',  # Makes the legend horizontal
          #  yanchor='bottom',  # Aligns the bottom of the legend box
           # y=1.05,  # Places the legend slightly above the plot
            #)
        )

    return reasons_bar

############# Grouped By Career ############

def create_grouped_chart(grouped_df, group_name_col, color_col, title, height='500'):

    grouped_chart = px.bar(
    grouped_df,
    x=group_name_col,
    y='count',
    color= color_col,
    color_discrete_map={'Positive':'darkturquoise', 'Neutral':'#646DEF', 'Negative':'red'},
    title=title,
    barmode="stack")

    grouped_chart.update_layout(
        height=height,
    )

    return grouped_chart
