import plotly.graph_objects as go

def build_level_step(level_ranges, color_scale=None):
    steps = []
    
    for item in level_ranges:
        # Determine the appropriate color based on the level
        if item["level"] in color_scale:
            color = color_scale[item["level"]]
        else:
            # white color
            color = "#FFFFFF"
        
        steps.append({'range': [item["min"], 100], 'color': color})
    return steps

# plot_skill_level
# plot chart with score and level ranges
# a progress bar chart with score and level ranges
def plot_skill_level(score, level_ranges, title="Skill Level"):
    # Define the color scale
    #00876c
    #439a72
    #6aad78
    #8fbf80
    #b4d18b
    #d9e398
    #fff4a8
    #fbd88a
    #f7bc72
    #f19f60
    #eb8055
    #e16050
    #d43d51
    color_scale = {
        "Intern": "#008728",
        "Fresher-": "#00876c",
        "Fresher": "#439a72",
        "Fresher+": "#6aad78",
        "Junior-": "#8fbf80",
        "Junior": "#b4d18b",
        "Junior+": "#d9e398",
        "Middle-": "#fff4a8",
        "Middle": "#fbd88a",
        "Middle+": "#f7bc72",
        "Senior-": "#f19f60",
        "Senior": "#eb8055",
        "Senior+": "#e16050",
        "Principal": "#d43d51",
    }
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': title},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100]},
            'steps' : build_level_step(level_ranges, color_scale),
            'threshold' : {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            },
            'bar': {
                'color': "black",
                'thickness': 0.05
            }
        }
    ))
    
    level_ranges_reversed = level_ranges[::-1]
    
    # adding legend for level ranges
    for item in level_ranges_reversed:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color_scale[item["level"]]),
            name=item["level"]
        ))
        
    # remove x and y axis
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    
    return fig
