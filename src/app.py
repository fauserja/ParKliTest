

"""
This app creates an .....
"""



import dash
from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container


#PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

app = dash.Dash(
    __name__, 
    use_pages=True, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], 
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)
server = app.server


navbar = dbc.Navbar(
    
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Img(src="./assets/ParKli_400px.png", height="30")
                                #dbc.NavbarBrand("ParKli", className="ms-2")
                            ],
                            width={"size":"auto"}
                        )
                    ],
                align="center",
                className="g-0"
                ),
                href="/",
                style={"textDecoration": "none"},
                
            ),
            
            # dbc.Row(
            #     [
            #         dbc.Col(
            #             [
            #                 html.Img(src="./assets/ParKli_400px.png", height="30")
            #                 #dbc.NavbarBrand("ParKli", className="ms-2")
            #             ],
            #             width={"size":"auto"}
            #         )
            #     ],
            #     align="center",
            #     className="g-0"
            # ),
            
           
            
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Collapse(
                                [
                                 
                                    dbc.Nav(
                                        [   
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    [
                                                        html.Div(page["name"], className="ms-1"),
                                                    ],
                                                    href=page["path"],
                                                    active="exact",
                                                )
                                            )
                                            
                                            for page in dash.page_registry.values()
                        
                                            if page["module"] != "pages.not_found_404"
                                        
                                        ],                                    
                                    ),
                                   
                                ],
                                id="navbar-collapse",
                                is_open=False,
                                navbar=True,
                                
                                
                            )
                        
                        ],
                        width={"size":"auto"},
                        #style={'margin':{"r":0,"t":0,"l":0,"b":0}}
                    )
                    
                ],
                align="center",

              
            ),
        
         
            dbc.Col(dbc.NavbarToggler(id="navbar-toggler", n_clicks=0)),
            
        ],
        
        fluid=True

    ),
    color="#eaeeef",
    light = True
    #dark=False
    
)



app.layout = dbc.Container([
    
    
        
       navbar,
       
       html.Br(),
       html.Br(),
      
       
       dash.page_container,
       
        dcc.Store(id='memory-output',  storage_type='session', data={}),
        dcc.Store(id='selectedData-State',  storage_type='session', data={}),
        dcc.Store(id='stored-data', storage_type='session', data={}),     
        dcc.Store(id='cleanedEyeOnWater-Data', storage_type='session', data={}), 
        dcc.Store(id='unCleanedEyeOnWater-Data', storage_type='session', data={}), 
        dcc.Store(id='greenSpaceHack-Data', storage_type='session', data={}),
       
], fluid=True)


@dash.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":

    app.run_server(debug=False)

# PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
# # try running the app with one of the Bootswatch themes e.g.
# # app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
# # app = dash.Dash(external_stylesheets=[dbc.themes.SKETCHY])

# # make a reuseable navitem for the different examples
# nav_item = dbc.NavItem(dbc.NavLink("Link", href="#"))

# # make a reuseable dropdown for the different examples
# dropdown = dbc.DropdownMenu(
#     children=[
#         dbc.DropdownMenuItem("Entry 1"),
#         dbc.DropdownMenuItem("Entry 2"),
#         dbc.DropdownMenuItem(divider=True),
#         dbc.DropdownMenuItem("Entry 3"),
#     ],
#     nav=True,
#     in_navbar=True,
#     label="Menu",
# )




# # this example that adds a logo to the navbar brand
# logo = dbc.Navbar(
#     dbc.Container(
#         [
#             html.A(
#                 # Use row and col to control vertical alignment of logo / brand
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             [
#                                 html.Img(src=PLOTLY_LOGO, height="30px"),
#                                 dbc.Col(dbc.NavbarBrand("Logo", className="ms-2")),
#                             ],
#                             width={"size":"auto"}
#                         )
#                     ],
#                     align="center",
#                     className="g-0",
                   
#                 ),
#                 href="https://plotly.com",
#                 style={"textDecoration": "none"},
#             ),
#             dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
#             dbc.Collapse(
#                 dbc.Nav(
#                     [nav_item, dropdown],
#                     className="ms-auto",
#                     navbar=True,
                    
#                 ),
#                 id="navbar-collapse2",
#                 navbar=True,
#                 className="g-0",
                            
#             ),
#         ],
#     ),
#     color="dark",
#     dark=True,
#     className="mb-5",
# )


# app.layout = html.Div(
#      logo
# )





# # the same function (toggle_navbar_collapse) is used in all three callbacks
# @app.callback(
#      Output(f"navbar-collapse", "is_open"),
#     [Input(f"navbar-toggler", "n_clicks")],
#     [State(f"navbar-collapse", "is_open")],
#     )
# # we use a callback to toggle the collapse on small screens
# def toggle_navbar_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open

# if __name__ == "__main__":
#     app.run_server(debug=False)



# app = dash.Dash(
#     __name__, 
#     use_pages=True, 
#     external_stylesheets=[dbc.themes.BOOTSTRAP],
#     suppress_callback_exceptions=True,
#     meta_tags=[
#         {"name": "viewport", "content": "width=device-width, initial-scale=1"}
#     ],
# )
# server = app.server




# content = html.Div([dash.page_container],id="page-content")

# app.layout = dbc.Container([
    
#         dcc.Store(id='memory-output',  storage_type='session'),
#         dcc.Store(id='selectedData-State',  storage_type='session'),
        
#         [sidebar, content],
                
       
# ], fluid=True)


    
# @callback(
#     Output("sidebar", "className"),
#     [Input("sidebar-toggle", "n_clicks")],
#     [State("sidebar", "className")],
# )
# def toggle_classname(n, classname):
#     if n and classname == "":
#         return "collapsed"
#     return ""


# @callback(
#     Output("collapse", "is_open"),
#     [Input("navbar-toggle", "n_clicks")],
#     [State("collapse", "is_open")],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open



# app.layout = dbc.Container([
    
#     dcc.Store(id='memory-output',  storage_type='session'),
#     dcc.Store(id='selectedData-State',  storage_type='session'),
    
    
#     dbc.Row([
#         dbc.Col(html.Div("Python Multipage App with Dash",
#                          style={'fontSize':50, 'textAlign':'center'}))
#     ]),

#     html.Hr(),

#     dbc.Row(
#         [
#             dbc.Col(
#                 [
#                     sidebar
#                 ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),

#             dbc.Col(
#                 [
#                     dash.page_container
#                 ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)
#         ]
#     )
# ], fluid=True)


# if __name__ == "__main__":
#     app.run_server(debug=False)
    
    
    
    
    
# app = dash.Dash(
#     external_stylesheets=[dbc.themes.BOOTSTRAP],
#     # these meta_tags ensure content is scaled correctly on different devices
#     # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
#     meta_tags=[
#         {"name": "viewport", "content": "width=device-width, initial-scale=1"}
#     ],
# )

# # we use the Row and Col components to construct the sidebar header
# # it consists of a title, and a toggle, the latter is hidden on large screens
# sidebar_header = dbc.Row(
#     [
#         dbc.Col(html.H2("Sidebar", className="display-4")),
#         dbc.Col(
#             [
#                 html.Button(
#                     # use the Bootstrap navbar-toggler classes to style
#                     html.Span(className="navbar-toggler-icon"),
#                     className="navbar-toggler",
#                     # the navbar-toggler classes don't set color
#                     style={
#                         "color": "rgba(0,0,0,.5)",
#                         "border-color": "rgba(0,0,0,.1)",
#                     },
#                     id="navbar-toggle",
#                 ),
#                 html.Button(
#                     # use the Bootstrap navbar-toggler classes to style
#                     html.Span(className="navbar-toggler-icon"),
#                     className="navbar-toggler",
#                     # the navbar-toggler classes don't set color
#                     style={
#                         "color": "rgba(0,0,0,.5)",
#                         "border-color": "rgba(0,0,0,.1)",
#                     },
#                     id="sidebar-toggle",
#                 ),
#             ],
#             # the column containing the toggle will be only as wide as the
#             # toggle, resulting in the toggle being right aligned
#             width="auto",
#             # vertically align the toggle in the center
#             align="center",
#         ),
#     ]
# )

# sidebar = html.Div(
#     [
#         sidebar_header,
#         # we wrap the horizontal rule and short blurb in a div that can be
#         # hidden on a small screen
#         html.Div(
#             [
#                 html.Hr(),
#                 html.P(
#                     "A responsive sidebar layout with collapsible navigation "
#                     "links.",
#                     className="lead",
#                 ),
#             ],
#             id="blurb",
#         ),
#         # use the Collapse component to animate hiding / revealing links
#         dbc.Collapse(
#             dbc.Nav(
#                 [
#                     dbc.NavLink("Home", href="/", active="exact"),
#                     dbc.NavLink("Page 1", href="/page-1", active="exact"),
#                     dbc.NavLink("Page 2", href="/page-2", active="exact"),
#                 ],
#                 vertical=True,
#                 pills=True,
#             ),
#             id="collapse",
#         ),
#     ],
#     id="sidebar",
# )

# content = html.Div(id="page-content")

# app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# @app.callback(
#     Output("page-content", "children"), [Input("url", "pathname")])
# def render_page_content(pathname):
#     if pathname == "/":
#         return html.P("This is the content of the home page!")
#     elif pathname == "/page-1":
#         return html.P("This is the content of page 1. Yay!")
#     elif pathname == "/page-2":
#         return html.P("Oh cool, this is page 2!")
#     # If the user tries to reach a different page, return a 404 message
#     return html.Div(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The pathname {pathname} was not recognised..."),
#         ],
#         className="p-3 bg-light rounded-3",
#     )


# @app.callback(
#     Output("sidebar", "className"),
#     [Input("sidebar-toggle", "n_clicks")],
#     [State("sidebar", "className")],
# )
# def toggle_classname(n, classname):
#     if n and classname == "":
#         return "collapsed"
#     return ""


# @app.callback(
#     Output("collapse", "is_open"),
#     [Input("navbar-toggle", "n_clicks")],
#     [State("collapse", "is_open")],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open


# # Dash-Anwendung ausführen
# if __name__ == '__main__':
#     app.run_server(debug=True)


# import dash
# import dash_bootstrap_components as dbc
# from dash import Input, Output, dcc, html

# PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# app = dash.Dash(
#     external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
# )

# sidebar = html.Div(
#     [
#         html.Div(
#             [
#                 # width: 3rem ensures the logo is the exact width of the
#                 # collapsed sidebar (accounting for padding)
#                 html.Img(src=PLOTLY_LOGO, style={"width": "3rem"}),
#                 html.H2("Sidebar"),
#             ],
#             className="sidebar-header",
#         ),
#         html.Hr(),
#         dbc.Nav(
#             [
#                 dbc.NavLink(
#                     [html.I(className="fas fa-home me-2"), html.Span("Home")],
#                     href="/",
#                     active="exact",
#                 ),
#                 dbc.NavLink(
#                     [
#                         html.I(className="fas fa-calendar-alt me-2"),
#                         html.Span("Calendar"),
#                     ],
#                     href="/calendar",
#                     active="exact",
#                 ),
#                 dbc.NavLink(
#                     [
#                         html.I(className="fas fa-envelope-open-text me-2"),
#                         html.Span("Messages"),
#                     ],
#                     href="/messages",
#                     active="exact",
#                 ),
#             ],
#             vertical=True,
#             pills=True,
#         ),
#     ],
#     className="sidebar",
# )

# content = html.Div(id="page-content", className="content")

# app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# # set the content according to the current pathname
# @app.callback(Output("page-content", "children"), Input("url", "pathname"))
# def render_page_content(pathname):
#     if pathname == "/":
#         return html.P("This is the home page!")
#     elif pathname == "/calendar":
#         return html.P("This is your calendar... not much in the diary...")
#     elif pathname == "/messages":
#         return html.P("Here are all your messages")
#     # If the user tries to reach a different page, return a 404 message
#     return html.Div(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The pathname {pathname} was not recognised..."),
#         ],
#         className="p-3 bg-light rounded-3",
#     )


# if __name__ == "__main__":
#     app.run_server(debug=False)
