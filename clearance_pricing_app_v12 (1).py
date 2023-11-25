# Clearance Pricing Toolkit Code

# setting working directory to script location
# import os
# script_location = os.path.split(os.path.realpath(__file__))[0]
# os.chdir(script_location)


# Importing required libraries

import pandas as pd
import numpy as np
import datetime
import base64
import io
import plotly.express as px
# import html
# from ortools.linear_solver import pywraplp
# import statsmodels.api as sm
import dash
from dash import dcc, html, dash_table
# import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html
# import dash_table
# import plotly.express as px
import plotly.graph_objs as go
from dash.dash_table.Format import Format, Scheme
from dash_table import DataTable, FormatTemplate
from plotly.subplots import make_subplots
import dash_daq as daq
from dash_extensions.enrich import dcc as enrich_dcc
Download = enrich_dcc.Download
send_file = enrich_dcc.send_file
send_bytes = enrich_dcc.send_bytes

# Importing helper functions
# from md_calc_functions import create_md_recommendations,create_md_summary
# from md_calc_functions import create_seasonality_output,create_exec_summary,create_exec_summary2,create_exec_summary3,create_exec_summary4,clean_md_recommendations,clean_md_summary
# from md_calc_functions import sku_level_wos, human_format, parse_data, parse_excel_data,update_real_time_tab
# from md_calc_functions import opt,elast_data


###########################


line0 = "Based on the selected parameters,"
line1 = "The program will be of " + " weeks, starting from "
line2 = "Current inventory on hand is " + " units & the cost of inventory is $"
line3 = "Expected sell-through for the program is "
exec_summary = [line0, line1, line2, line3]


def sku_level_wos(sales_data, inv_data):
    sku_level_weekly_sales = sales_data.groupby('sku').agg({"salesqty": "sum"}).reset_index()
    sku_level_inv = inv_data.groupby('sku').agg({"inventory": "sum"}).reset_index()
    sku_level_wos = pd.merge(sku_level_inv, sku_level_weekly_sales, how="left", on="sku")
    sku_level_wos["weekly_sales"] = sku_level_wos["salesqty"] / 52
    sku_level_wos["wos"] = sku_level_wos["inventory"] / sku_level_wos["weekly_sales"]
    sku_level_wos = sku_level_wos[["sku", "wos"]]
    sku_level_wos["sku"] = sku_level_wos["sku"].astype(str)
    sku_level_wos = sku_level_wos.round({'wos': 1})
    sku_level_wos = sku_level_wos.sort_values('wos')
    return(sku_level_wos)


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', ' K', ' Mn', 'G', 'T', 'P'][magnitude])


def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


def parse_excel_data(contents, filename, sheet_name):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), sheet_name=sheet_name)
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


def expand_grid(x, y, z):
    xG, yG, zG = np.meshgrid(x, y, z)  # create the actual grid
    xG = xG.flatten()  # make the grid 1d
    yG = yG.flatten()  # same
    zG = zG.flatten()
    return pd.DataFrame({'x': xG, 'y': yG, "z": zG})  # return a dataframe


################################


# Global Variables and Data
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': '3rem',
    'left': 0,
    'bottom': 0,
    'width': '25%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}
ACN_LOGO = "./assets/acn_logo.png"


# fiscal_calendar = pd.read_csv("./data/fiscal_calendar.csv")
# changed for exe
fiscal_calendar = pd.read_csv("./data/fiscal_calendar.csv")
fiscal_calendar["date"] = pd.to_datetime(fiscal_calendar["date"])


# Initialize the app
app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=True)


#### NAV BAR #################################################################
search_bar = dbc.Row(
    [
        dbc.Col(
            dbc.Button("About", color="primary", className="ml-2", id="open"),
            width="auto",
        ),
        dbc.Col(
            dbc.Button("Home", color="primary", className="ml-2", id="home"),
            width="auto",
        ),
    ],
    # no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=ACN_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand(html.B("United Way BC"), className="ml-2")),
                ],
                align="center",
                # no_gutters=True,
            ),
            href="https://uwbc.ca",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="primary",
    dark=True, style={"height": "3rem"}
)


modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("About"),
                dbc.ModalBody([html.P(["Clearance pricing toolkit enables you to design markdowns with maximum flexibility.",
                                      html.Br(),
                                      "User uploads the sales & inventory data. ",
                                       html.Br(), "Pricing recommendations are then calculated on the basis of seasonality, elasticity, weeks of supply for each store product combination.",
                                       # html.Img(src=app.get_asset_url(r'Clearance App.jpg'))
                                       html.Br(), "Click on the following to download respective files for reference"]),
                               html.Div([dbc.Button("Complete User Guide", id="btn1", className="ml-auto", style={"width": 250, "margin-top": "5px"}),
                                         html.Br(),
                                         dbc.Button("Collection Data Template", id="btn2", className="ml-auto", style={"width": 250, "margin-top": "5px"}),
                                         html.Br(),
                                         dbc.Button("Distribution Data Template", id="btn3", className="ml-auto", style={"width": 250, "margin-top": "5px"}),
                                         html.Br(),
                                         dbc.Button("Real Time Sales Template", id="btn4", className="ml-auto", style={"width": 250, "margin-top": "5px"}),
                                         ])
                               ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            ],
            id="modal", style={"width": "1400px"}
        ),
    ]
)
###############################################################################


###### TOOL TIP ICON ##########################################################
tooltipIcon = dash_dangerously_set_inner_html.DangerouslySetInnerHTML("&#9432;")
###############################################################################


###### ALGORITHM SELECTION ####################################################
algo_select = dbc.FormGroup(
    [
        dbc.Label(html.B(
            html.Span(dash_dangerously_set_inner_html.DangerouslySetInnerHTML('Select Algorithm <span id="tooltip-target-1">&#9432;</span>'))
        ), html_for="example-email-row", width=6, style={"font-size": '70%'}),
        dbc.Col(
            dcc.Dropdown(
                id="algo_select_dropdown",
                options=[
                    {"label": "Heuristics Based Algorithm", "value": 1},
                    {"label": "Elasticity Based Algorithm", "value": 2},
                ], value=1, style={'height': '30px', 'font-size': '85%', 'display': 'form-inline'}
            ),
            width=6,
        ),
        dbc.Tooltip("Based on data availability, select an algorithm for calculations. Refer documentation in the'About' section  for further details.",
                    target="tooltip-target-1")
    ],
    row=True,
)
###############################################################################


###### PLANNING MODE ##########################################################
planning_mode = dbc.Button(html.P(html.B('Planning Phase'), style={"font-size": "70%"}),
                           style={"width": "100%", 'margin': 5, "height": "30px"}, id="planning_mode")
###############################################################################


###### REAL TIME TRACKING MODE ################################################
real_time_mode = dbc.Button(html.P(html.B('Go To Real Time Tracking'), style={"font-size": "70%"}),
                            style={"width": "100%", 'margin': 5, "height": "30px"}, id="real_time_mode")
###############################################################################


###### PLANNING MODE ##########################################################
real_time_toggle = daq.ToggleSwitch(id='my-toggle-switch', value=False, label="Real Time Tracking")
###############################################################################


###### SALES DATA UPLOAD ######################################################
du_sales_data_upload = dcc.Upload(dbc.Button(html.P(html.B('Collection Data'), style={"font-size": "70%"}),  # sales
                                             style={"width": "100%", 'margin': 5, "height": "30px"}), id="sales_upload_file")
###############################################################################


###### INVENTORY DATA UPLOAD ##################################################

du_inv_data_upload = dcc.Upload(dbc.Button(html.P(html.B('Distribution Data'), style={"font-size": "70%"}),  # inv
                                           style={"width": "100%", 'margin': 5, "height": "30px"}), id="inv_upload_file")
###############################################################################


###### PROGRAM NAME ###########################################################
prg_name = dbc.FormGroup(
    [
        dbc.Label(html.B(dash_dangerously_set_inner_html.DangerouslySetInnerHTML('Program Name <span id="tooltip-target-2">&#9432;</span>'),
                  id="tooltip-target-2"), html_for="example-email-row", width=6, style={"font-size": '70%'}),
        dbc.Col(
            dbc.Input(
                type="text", value="Markdown Test 1", id="prg_name", style={'height': '30px', 'display': 'inline-block', 'font-size': '70%'}
            ),
            width=6,
        ),
        dbc.Tooltip("Assign a name to the program. This name will be a unique identifier throughout program lifecycle.",
                    target="tooltip-target-2")
    ],
    row=True,
)
###############################################################################


###### MD DURATION IN WEEKS ###################################################
md_duration = dbc.FormGroup(
    [
        dbc.Label(html.B(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("MD Duration(Weeks) &#9432;"),
                  id="tooltip-target-3"), html_for="example-email-row", width=6, style={"font-size": '70%'}),
        dbc.Col(
            dbc.Input(
                type="number", min=3, max=24, step=1, value=12, id="md_duration", style={'height': '30px', 'display': 'inline-block', 'font-size': '70%'}
            ),
            width=6,
        ),
        dbc.Tooltip("Total duration for which program will run",
                    target="tooltip-target-3")
    ],
    row=True,
)
###############################################################################


###### EVAL PERIOD IN WEEKS ###################################################
eval_period = dbc.FormGroup(
    [
        dbc.Label(html.B(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("Eval. Period(Weeks) &#9432;"),
                  id="tooltip-target-4"), html_for="example-email-row", width=6, style={"font-size": '70%'}),
        dbc.Col(
            dbc.Input(
                type="number", min=2, max=6, step=1, value=4, id="eval_period", style={'height': '30px', 'display': 'inline-block', 'font-size': '70%'}
            ),
            width=6,
        ),
        dbc.Tooltip("Select when and how often should program be recaliberated based on real time execution",
                    target="tooltip-target-4")
    ],
    row=True,
)
###############################################################################


###### UPPER BOUND ############################################################
upper_bound = dbc.FormGroup(
    [
        dbc.Label(html.B(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("Upper Bound &#9432;"),
                  id="tooltip-target-5"), html_for="example-email-row", width=6, style={"font-size": '70%'}),
        dbc.Col(
            dbc.Input(
                type="number", min=0.2, max=1.0, step=0.05, value=0.8, id="upper_bound", style={'height': '30px', 'display': 'inline-block', 'font-size': '70%'}
            ),
            width=6,
        ),
        dbc.Tooltip("Maximum allowable discount percentage",
                    target="tooltip-target-5")
    ],
    row=True,
)
###############################################################################


#### LOWER BOUND #############################################################
lower_bound = dbc.FormGroup(
    [
        dbc.Label(html.B(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
            "Lower Bound &#9432;"), id="tooltip-target-6"), width=6, style={"font-size": '70%'}),
        dbc.Col(
            dbc.Input(
                type="number", min=0, max=0.6, step=0.05, value=0, id="lower_bound", style={'height': '30px', 'display': 'inline-block', 'font-size': '70%'}
            ),
            width=6,
        ),
        dbc.Tooltip("Minimum required discount percentage",
                    target="tooltip-target-6")
    ],
    row=True,
)
###############################################################################


#### MD DELTA  ################################################################
md_delta = dbc.FormGroup(
    [
        dbc.Label(html.B(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
            "Minimum Delta &#9432;"), id="tooltip-target-7"), width=6, style={"font-size": '70%'}),
        dbc.Col(
            dbc.Input(
                type="number", min=0, max=0.3, step=0.025, value=0.1, id="md_delta", style={'height': '30px', 'display': 'inline-block', 'font-size': '70%'}
            ),
            width=6,
        ),
        dbc.Tooltip("Minimum required percentage difference amongst consecutive rounds",
                    target="tooltip-target-7")
    ],
    row=True,
)
###############################################################################


#### FIRST ROUND UPPER BOUND  #################################################
first_r_ub = dbc.FormGroup(
    [
        dbc.Label(html.B(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
            "R1 Upper Bound &#9432;"), id="tooltip-target-8"), width=6, style={"font-size": '70%'}),
        dbc.Col(
            dbc.Input(
                type="number", min=0.2, max=0.8, step=0.05, value=0.4, id="first_r_ub", style={'height': '30px', 'display': 'inline-block', 'font-size': '70%'}
            ),
            width=6,
        ),
        dbc.Tooltip("Maximum allowable discount percentage for first round",
                    target="tooltip-target-8")
    ],
    row=True,
)
###############################################################################


#### START DATE  ##############################################################
md_start_date = dbc.FormGroup(
    [
        dbc.Label(html.B(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
            "MD Start Date &#9432;"), id="tooltip-target-9"), width=6, style={"font-size": '70%'}),
        dbc.Col(
            dcc.DatePickerSingle(date=datetime.date(2021, 1, 1), display_format='MM/DD/YYYY', id="start_date", style={"fontsize": "70%", 'display': 'inline-block'}
                                 ),
            width=6,
        ),
        dbc.Tooltip("Start date for the program",
                    target="tooltip-target-9")
    ],
    row=True,
)
###############################################################################


#### GENERATE RECOMMENDATIONS BUTTON ##########################################
generate_reco = dbc.Button(html.P(html.B('Calculate Distribution Recommendation'), style={"font-size": '70%'}),
                           id='generate_reco', style={"width": "100%", "height": "30px"})
###############################################################################


#### LEFT SIDEBAR ELEMENTS ####################################################
col1 = dbc.Col([
    dbc.Row([
        dbc.Col(html.H5(html.B("Algorithm Selection")), width=12)
    ]),
    dbc.Row([
        dbc.Col(algo_select, width=12)
    ]),
    dbc.Row([
        dbc.Col(html.Hr(style={"borderColor": "black"}), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.H5(html.B("Real Time Tracking Mode")), width=12)
    ]),
    dbc.Row([
        # dbc.Col(real_time_toggle, width=6),
        dbc.Col(real_time_mode, width={"size": 10, "offset": 1})
    ]),
    dbc.Row([
        dbc.Col(html.Hr(style={"borderColor": "black"}), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.H5(html.B("Planning Mode")), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.Hr(), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.H6("Data Upload"), width=12)
    ]),
    dbc.Row([
        dbc.Col(du_sales_data_upload, width=6),
        dbc.Col(du_inv_data_upload, width=6)
    ]),
    dbc.Row([
        dbc.Col(html.Hr(), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.H6("Inventory Details Input"), width=12)
    ]),
    dbc.Row([
        dbc.Col(prg_name, width=12),
        dbc.Col(md_duration, width=12),
        dbc.Col(eval_period, width=12),
        dbc.Col(lower_bound, width=12),
        dbc.Col(upper_bound, width=12),
        dbc.Col(md_delta, width=12),
        dbc.Col(first_r_ub, width=12),
        dbc.Col(md_start_date, width=12)
    ]),
    dbc.Row([
        dbc.Col(html.Hr(), width=12)
    ]),
    dbc.Row([
        dbc.Col(generate_reco, width={"size": 10, "offset": 1})
    ]),
    dbc.Row([
        dbc.Col(html.Hr(style={"borderColor": "black"}), width=12)
    ])
], style=SIDEBAR_STYLE)

container2 = html.Div(id="main_container")
###############################################################################


#### CALLBACK FOR MAIN CONTAINER ##############################################
@app.callback(Output('main_container', 'children'),
              [Input('sales_upload_file', 'contents'),
               Input('sales_upload_file', 'filename'),
               Input('inv_upload_file', 'contents'),
               Input('inv_upload_file', 'filename'),
               Input('generate_reco', 'n_clicks'),
               Input('prg_name', 'value'),
               Input('home', 'n_clicks'),
               Input('real_time_mode', 'n_clicks')],
              [State('md_duration', 'value'),
              State('eval_period', 'value'),
              State('lower_bound', 'value'),
              State('upper_bound', 'value'),
              State('md_delta', 'value'),
              State('first_r_ub', 'value'),
              State('start_date', 'date'),
              State('algo_select_dropdown', 'value')])
def update_main_container(contents_sales, filename_sales, content_inv, filename_inv, n_clicks, prg_name,
                          home_nclicks,
                          real_time_mode_nclicks,
                          md_duration, eval_period, lower_bound, upper_bound, md_delta, first_r_ub, start_date, algo_select):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    print(changed_id)
    if "home.n_clicks" in changed_id:
        return html.Div([
            html.Img(src=app.get_asset_url('Clearance App.png'))
        ])

    elif "real_time_mode.n_clicks" in changed_id:

        # real time tracking
        report_upload = dcc.Upload(dbc.Button(html.P(html.B('Upload Report'), style={"font-size": "70%"}),
                                              style={"width": "100%", 'margin': 5, "height": "30px"}), id="report_upload_file")

        actual_sales_upload = dcc.Upload(dbc.Button(html.P(html.B('Upload Actual Sales'), style={"font-size": "70%"}),
                                                    style={"width": "100%", 'margin': 5, "height": "30px"}), id="actual_sales_upload_file")
        rtt_tab_top = dbc.Row([
            dbc.Col(report_upload, width=3),
            dbc.Col(actual_sales_upload, width=3),
            dbc.Col(dbc.Button(html.P(html.B('Export Updated Markdowns'), style={"font-size": "70%"}),
                               style={"width": "100%", 'margin': 5, "height": "30px"}, id="updated_md_export",), width=3),
            Download(id="download-text2")
        ])

        return html.Div([
            dbc.Col([
                dbc.Row([
                    dbc.Col(html.H6("Results", style={"marginLeft": 2, "marginRight": 2, "marginTop": 2}))]),
                dbc.Row([
                    dbc.Col(
                        dbc.Tabs(
                            [
                                dbc.Tab([
                                    html.Br(),
                                    rtt_tab_top,
                                    html.Br(),
                                    DataTable(id="rtt_table", data=[], style_table={"width": "95%"}, style_cell={"width": "20%", "textAlign": "center"})
                                ], label="Real Time Tracking", tab_id="real_time_table")
                            ],
                            id="tabs", active_tab="real_time_table"), style={"marginLeft": 2, "marginRight": 2, "marginTop": 5}
                    )
                ])
            ], width=12)
        ], style={"marginLeft": 5, "marginRight": 5, "marginTop": 5})

    elif ("sales_upload_file.contents" in changed_id) or ("inv_upload_file.contents" in changed_id) or ("generate_reco.n_clicks" in changed_id):
        if (not (pd.isnull(filename_inv))) and (not (pd.isnull(filename_sales))):
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
            print(changed_id)
            print("entered update main container if condition")
            sales_df = parse_data(contents_sales, filename_sales)
            inv_df = parse_data(content_inv, filename_inv)

            # For Overview Tab
            store_sales_data = sales_df.groupby(['Donation Year'], as_index=False).agg({
                "PADS": "sum",
                "TAMPONS": "sum",
                "LINERS/WIPES": "sum",
                "REUSABLE PADS/Underwear": "sum",
                "MENSTRUAL CUPS": "sum",
                "Pads Value": "sum",
                "Tampons Value": "sum",
                "Liners/Wipes Value": "sum",
                "Reusable Pads/Underwear Value": "sum",
                "Menstrual Cups Value": "sum",
                "TOTAL #": "sum",
                "Total $": "sum"
            })
            print(store_sales_data)
            #store_sales_data = pd.merge(store_sales_data, sales_df.groupby(['Donation Year']).Donations.nunique(), how="left", on="Donation Year")
            print(store_sales_data)
            #store_sales_data.columns= ['Store','Total $ Sales','No Of SKUs']
            store_sales_data = store_sales_data.sort_values(['TOTAL #'], ascending=[False])
            store_sales_data_table = dash_table.DataTable(id='bl_store_table',
                                                          columns=[{"name": "Donation Year", "id": "Donation Year", "type": "numeric"},
                                                                   {"name": "Total Donation in Kind", "id": "Total $",
                                                                       'type': "numeric", 'format': FormatTemplate.money(0)},
                                                                   {"name": "Total Products Donated in Kind", "id": "TOTAL #", 'type': 'numeric', 'format': Format(precision=0, scheme=Scheme.fixed)}],
                                                          style_cell={'textAlign': 'center', 'minWidth': '33.33%', 'width': '33.33%', 'maxWidth': '33.33%', 'fontSize': '1.1rem'}, data=store_sales_data.to_dict('records'))
            table2 = html.Div([html.Div("Donation Insights", style={"font-weight": "bolder",
                              "text-align": "center", "padding": "5px"}), store_sales_data_table])

            sku_sales_data = inv_df.groupby(['Distribution Year'], as_index=False).agg({
                "PADS": "sum",
                "DISTRIBUTION": pd.Series.nunique,
                "TAMPONS": "sum",
                "LINERS/WIPES": "sum",
                "REUSABLE PADS/Underwear": "sum",
                "MENSTRUAL CUPS": "sum",
                "TOTAL #": "sum"
            })
            # sku_sales_data = pd.merge(sku_sales_data, sales_df.groupby(['Donation Year','Donations']).agg({
            #     "PADS":"mean",
            #     "TAMPONS":"mean",
            #     "LINERS/WIPES":"mean",
            #     "REUSABLE PADS/Underwear":"mean",
            #     "MENSTRUAL CUPS":"mean",
            #     "TOTAL #":"mean"
            #     }), how="left", on="['Donation Year','Donations']")
            #sku_sales_data.columns= ['SKU','Max Sales','Avg Weekly Sales']
            sku_sales_data = sku_sales_data.sort_values(['TOTAL #'], ascending=[False]).head(5)
            sku_sales_data_table = dash_table.DataTable(id='bl_sales_table',
                                                        columns=[{"name": "Distribution Year", "id": "Distribution Year", "type": "numeric"},
                                                                 {"name": "Total Communities Touched", "id": "DISTRIBUTION"},
                                                                 {"name": "Total Products Distributed", "id": "TOTAL #", 'type': 'numeric', 'format': Format(precision=1, scheme=Scheme.fixed)}],
                                                        style_cell={'textAlign': 'center', 'minWidth': '33.33%', 'width': '33.33%', 'maxWidth': '33.33%', 'fontSize': '1.1rem'}, data=sku_sales_data.to_dict('records'))

            table1 = html.Div([html.Div("Top 5 SKUs by Sales", style={"font-weight": "bolder", "text-align": "center", "padding": "5px"}), sku_sales_data_table])

            #wos_data = sku_level_wos(sales_df, inv_df)

            # Time Series Plot for Monthly Distribution

            wos_data = inv_df.groupby(['Distribution Date'], as_index=False).agg({
                "TOTAL #": "sum"
            })
            print(wos_data)
            wos_graph = html.Div([dcc.Graph(id='example-graph',
                                            figure=px.line(wos_data, x='Distribution Date', y='TOTAL #', text='TOTAL #', title="<b>Monthly Distribution of Products</b>"))], style={"margin-top": "10px", "border": "1px dashed #636efa"})

           # For SKU Deepdive Tab
            options = sales_df['Donation Year'].unique()
            stores = sales_df['Donation Year'].unique()
            sku_dropdown = html.Div(
                [
                    html.Label("Select a SKU"),
                    dcc.Dropdown(
                        id='sku-dropdown',
                        options=[{'label': i, 'value': i} for i in options],
                        placeholder="Select a SKU",
                        value=options[0])], className="col-md-12 sku-dropdown", style={"margin-top": "10px", "padding-left": "0px"})

            store_dropdown = html.Div(
                [
                    html.Label("Select a Store"),
                    dcc.Dropdown(
                        id='store-dropdown',
                        options=[{'label': i, 'value': i} for i in stores],
                        placeholder="Select a Store",
                        value=stores[0])], className="col-md-12 store-dropdown", style={"margin": "10px"})

            filters_row = dbc.Row(
                [
                    dbc.Col(sku_dropdown, width=6),
                    dbc.Col(store_dropdown, width=6)])

            new_inv_df = inv_df
            inv_df['hasinv'] = np.where(inv_df['TOTAL #'] > 0, 1, 0)

            # SKU Summary Tab

            print("1111111111111111111111111111111111111111")
            print(algo_select)
            if n_clicks:
                pass

            else:
                sku_summ_page = "Please Click on Calculate MD Recommendations to generate markdowns"

            # SKU Store Recommendations Tab
            if n_clicks:
                pass

            else:
                md_recomm_page = "Please Click on Calculate MD Recommendations to generate markdowns"

            # ### real time tracking

            if n_clicks:
                exec_summary_card = dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Executive Summary", className="card-title"),
                            html.H5(prg_name),
                            html.Ul([html.Li(exec_summary[0]),
                                     html.Li(exec_summary[1]),
                                     html.Li(exec_summary[2]),
                                     html.Li(exec_summary[3])]),

                            dbc.Button("Export Details", color="primary", id="exec_summ_export"),
                            Download(id="download-text")
                        ]
                    ), style={"padding": "5px"})
            else:
                exec_summary_card = dbc.Card(
                    dbc.CardBody(
                        [

                            html.H5("Executive Summary", className="card-title"),
                            html.H5(prg_name),
                            html.Li(["Please generate markdown recommendations"])
                        ]
                    ), style={"padding": "5px"}
                )

            return html.Div([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.H6("Results", style={"marginLeft": 2, "marginRight": 2, "marginTop": 2}))]),
                    dbc.Row([
                        dbc.Col(
                            dbc.Tabs(
                                [
                                    dbc.Tab([
                                        html.Div(
                                            [
                                                dbc.CardDeck(
                                                    [
                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody(
                                                                    [
                                                                        html.H4("Total Product Donations", className="card-title"),
                                                                        html.P(str(sales_df['TOTAL #'].sum()), className="card-value")], className="data-overview-card-body")]),
                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody(
                                                                    [
                                                                        html.H4("Communitites Touched", className="card-title"),
                                                                        html.P(str(inv_df['DISTRIBUTION'].nunique()), className="card-value")], className="data-overview-card-body")]),

                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody(
                                                                    [
                                                                        html.H4("Total Product Distributions", className="card-title"),
                                                                        html.P(str(round(inv_df['TOTAL #'].sum(), 0)), className="card-value")], className="data-overview-card-body")]),

                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody(
                                                                    [
                                                                        html.H4("Sales Units (Total)", className="card-title"),
                                                                        html.P(human_format(sales_df['PADS'].sum()), className="card-value")], className="data-overview-card-body")]),

                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody([
                                                                    html.H4("Gross Margin", className="card-title"),
                                                                    html.P(str((((inv_df['PADS'] - inv_df["PADS"]).sum()) / (inv_df['PADS'].sum())) * 100)[0:4] + "%", className="card-value")], className="data-overview-card-body")])]),

                                                html.Hr(),
                                                html.Div(
                                                    [
                                                        html.Div(table1, className="col s6"),
                                                        html.Div(table2, className="col s12"),
                                                    ], className="row"),

                                                wos_graph
                                            ], style={'padding-top': '10px'})

                                    ], label="Data Overview", tab_id="data_overview"),

                                    dbc.Tab([
                                        html.Div([
                                            # filters_row,
                                            html.Hr(),
                                            html.P("Overall Chain Level SKU Metrics", style={
                                                   "font-weight": "bolder", "text-align": "center", "padding": "5px"}),
                                            dbc.CardDeck(
                                                [
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.H4("Gross Margin", className="card-title"),
                                                                    html.P(str((((sales_df['PADS'] - sales_df["PADS"]).sum()) / ((sales_df["PADS"]).sum()) * 100))[0:4] + " %",
                                                                           className="card-value", id="gm-value-skudd")],
                                                                className="sku-deep-dive-card-body")]),


                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.H4("Inv. On Hand Units", className="card-title"),
                                                                    html.P(round(inv_df['PADS'].sum(), 0), className="card-value", id="IOH-value-skudd")],
                                                                className="sku-deep-dive-card-body")]),
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.H4("Sales Units (Total)", className="card-title"),
                                                                    html.P(human_format(sales_df["PADS"].sum()), className="card-value", id="total-sales-value-skudd")],
                                                                className="sku-deep-dive-card-body")]),
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.H4("Weeks Of Supply", className="card-title"),
                                                                    html.P((round(((inv_df['PADS'].sum()) / (sales_df["PADS"].sum())) * 52, 2)), className="card-value", id="WOS-value-skudd")],
                                                                className="sku-deep-dive-card-body")]),


                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.H4("Cost Of IOH ($)", className="card-title"),
                                                                    html.P(
                                                                        human_format(sum(inv_df['PADS'] * inv_df['PADS'])), className="card-value", id="cost-of-ioh-skudd")],
                                                                className="sku-deep-dive-card-body")])

                                                ]
                                            ),
                                            html.Br(),
                                            # filters_row2,
                                            html.Div([
                                                dcc.Graph(id='plot')], style={"margin-top": "10px", "border": "1px dashed #636efa"})

                                        ])

                                    ], label="SKU Deep Dive", tab_id="sku_dd"),


                                    dbc.Tab([
                                        html.Br(), sku_summ_page,
                                    ], label="SKU Summary", tab_id="sku_summ"),

                                    dbc.Tab([
                                        html.Br(), md_recomm_page
                                    ], label="SKU-Store Recommendations", tab_id="sku_store_recos"),
                                    dbc.Tab([
                                        html.Br(),
                                        exec_summary_card

                                    ], label="Executive Summary", tab_id="exec_summ"),

                                    # dbc.Tab([
                                    #     html.Br(),
                                    #     rtt_tab_top,
                                    #     html.Br(),
                                    #     DataTable(id = "rtt_table", data =[],style_table={"width":"95%"},style_cell={"width": "20%","textAlign":"center"})
                                    #     ],label="Real Time Tracking", tab_id="real_time_table")



                                ],
                                id="tabs", active_tab="data_overview"), style={"marginLeft": 2, "marginRight": 2, "marginTop": 5}
                        )
                    ])
                ], width=12)
            ], style={"marginLeft": 5, "marginRight": 5, "marginTop": 5})

        else:
            return html.Div([
                html.Img(src=app.get_asset_url('Clearance App.png'))
            ])
    else:
        return html.Div([html.Img(src=app.get_asset_url('Clearance App.png'))])


###############################################################################


#### CALLBACK FOR SKU-STORE PLOT ##############################################
@app.callback([Output('plot', 'figure'),
               Output('gm-value-skudd', 'children'),
               Output("IOH-value-skudd", 'children'),
               Output("total-sales-value-skudd", 'children'),
               Output("WOS-value-skudd", 'children'),
               Output("cost-of-ioh-skudd", "children")],
              [Input('sales_upload_file', 'contents'),
               Input('sales_upload_file', 'filename'),
               Input('inv_upload_file', 'contents'),
               Input('inv_upload_file', 'filename'),
               Input('sku-dropdown', 'value'),
               Input('store-dropdown', 'value')])
def update_sku_dd_trend(contents_sales, filename_sales, content_inv, filename_inv,
                        sku_dropdown_value, store_dropdown_value):
    sales_df = parse_data(contents_sales, filename_sales)
    inv_df = parse_data(content_inv, filename_inv)

    sales_df["PADS"] = sales_df["PADS"] / sales_df["PADS"]
    sales_df["PADS"].fillna(0, inplace=True)
    print(sales_df)
    if store_dropdown_value is None:
        new_sku_sales_df = sales_df.groupby(['PADS', 'TOTAL #'], as_index=False).agg({"PADS": 'sum', "TAMPONS": "mean"})
        layout = go.Layout(title={
            'text': "SKU Sales Plot",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            hovermode='closest')
    else:
        new_sku_sales_df = sales_df.loc[sales_df["PADS"] == store_dropdown_value]
        print("For Graph")
        print(new_sku_sales_df)
        layout = go.Layout(title={
            'text': "SKU Store Sales Plot",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            hovermode='closest')

    final_sku_sales_df = new_sku_sales_df.loc[new_sku_sales_df["sku"] == sku_dropdown_value]
    final_sku_sales_df['date'] = pd.to_datetime(final_sku_sales_df['date'])
    st2 = final_sku_sales_df.sort_values(['date'])

    # trace_1 = go.Scatter(x = st2.date, y = st2["salesqty"],
    #                     name = 'AAPL HIGH',
    #                     line = dict(width = 2,
    #                                 color = 'rgb(99, 110, 250)'))

    # trace_2 = go.Scatter(x = st2.date, y = st2["price"],
    #                 name = 'AAPL HIGH',
    #                 line = dict(width = 2,
    #                             color = 'rgb(99, 110, 110)'))
    # fig = go.Figure(data = [trace_1], layout = layout)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=st2.date, y=st2["salesqty"], name="Sales Units"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=st2.date, y=st2["price"], name="Sales Price"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="<b>Sales vs. Price Trend</b>"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="Sales Units", secondary_y=False)
    fig.update_yaxes(title_text="Price($)", secondary_y=True)

    # fig.add_trace(go.Figure(data = [trace_2], layout = layout),secondary_y = True)
    # print(fig)
    print("reached end for graph")

    inv_df_sku = inv_df[inv_df["sku"] == sku_dropdown_value]
    sales_df_sku = sales_df[sales_df['sku'] == sku_dropdown_value]
    sales_df_sku_weekly = sales_df_sku.groupby('date').agg({"salesqty": "sum"})
    gm_card = str((((inv_df_sku['price'] - inv_df_sku["cost"]).sum()) / ((inv_df_sku["price"]).sum()) * 100))[0:4] + " %"
    ioh_card = round(inv_df_sku['inventory'].sum(), 0)
    sales_card = human_format(sales_df_sku["salesqty"].sum())
    wos_card = round(((inv_df_sku['inventory'].sum()) / (sales_df_sku_weekly["salesqty"].mean())), 2)
    cost_ioh_card = human_format(sum(inv_df_sku["inventory"] * inv_df_sku["cost"]))

    return fig, gm_card, ioh_card, sales_card, wos_card, cost_ioh_card
###############################################################################


#### CALLBACK FOR DATA DOWNLOAD ###############################################
@app.callback(Output("download-text", "data"),
              [Input('sales_upload_file', 'contents'),
               Input('sales_upload_file', 'filename'),
               Input('inv_upload_file', 'contents'),
               Input('inv_upload_file', 'filename'),
               Input('exec_summ_export', 'n_clicks')],
              [State('md_duration', 'value'),
              State('eval_period', 'value'),
              State('lower_bound', 'value'),
              State('upper_bound', 'value'),
              State('md_delta', 'value'),
              State('first_r_ub', 'value'),
              State('start_date', 'date'),
              State('algo_select_dropdown', 'valu    e')])
def download_exec_summ(contents_sales, filename_sales, content_inv, filename_inv,
                       n_clicks, md_duration, eval_period, lower_bound, upper_bound, md_delta,
                       first_r_ub, start_date, algo_select):

    if n_clicks:
        sales_df = parse_data(contents_sales, filename_sales)
        inv_df = parse_data(content_inv, filename_inv)

        parameters = pd.DataFrame(columns=["parameter", "value"])
        parameters = parameters.append({"parameter": "md_duration", "value": md_duration}, ignore_index=True)
        parameters = parameters.append({"parameter": "eval_period", "value": eval_period}, ignore_index=True)
        parameters = parameters.append({"parameter": "md_delta", "value": md_delta}, ignore_index=True)
        parameters = parameters.append({"parameter": "start_date", "value": start_date}, ignore_index=True)
        parameters = parameters.append({"parameter": "upper_bound", "value": upper_bound}, ignore_index=True)
        parameters = parameters.append({"parameter": "lower_bound", "value": lower_bound}, ignore_index=True)
        parameters = parameters.append({"parameter": "multiplier", "value": 0.7}, ignore_index=True)
        parameters = parameters.append({"parameter": "fixed_fr_ub", "value": first_r_ub}, ignore_index=True)

        if algo_select == 1:
            pass

            def to_xlsx(bytes_io):
                xslx_writer = pd.ExcelWriter(bytes_io)
                exec_summary.to_excel(xslx_writer, index=False, sheet_name="Exec_Summary")
                sales_df.to_excel(xslx_writer, index=False, sheet_name="Historical_Sales")
                inv_df.to_excel(xslx_writer, index=False, sheet_name="Starting_Inventory")
                parameters.to_excel(xslx_writer, index=False, sheet_name="Parameters")
                # xslx_writer = xslx_writer.sheets['MD_Recommendations'].hide()
                # worksheet.hide()
                xslx_writer.save()
            return send_bytes(to_xlsx, "Report.xlsx")

        if algo_select == 2:
            pass

            def to_xlsx(bytes_io):
                xslx_writer = pd.ExcelWriter(bytes_io)
                sales_df.to_excel(xslx_writer, index=False, sheet_name="Historical_Sales")
                inv_df.to_excel(xslx_writer, index=False, sheet_name="Starting_Inventory")
                parameters.to_excel(xslx_writer, index=False, sheet_name="Parameters")
                xslx_writer.save()
            return send_bytes(to_xlsx, "Report.xlsx")
###############################################################################


#### CALLBACK FOR REAL TIME TRACKING TAB ######################################

###############################################################################


#### CALLBACK FOR MODAL #######################################################
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    print('modal callback called')
    if n1 or n2:
        return not is_open
    return is_open
###############################################################################


#### CALLBACK FOR MODAL #######################################################
@app.callback(Output("download-text2", "data"),
              [Input('report_upload_file', 'contents'),
               Input('report_upload_file', 'filename'),
               Input('actual_sales_upload_file', 'contents'),
               Input('actual_sales_upload_file', 'filename'),
               Input('updated_md_export', 'n_clicks')])
def download_updated_md(contents_report, filename_report, content_act_sales, filename_act_sales, n_clicks):

    if n_clicks:
        sales_data = parse_excel_data(contents_report, filename_report, sheet_name="Historical_Sales")
        inv_data = parse_excel_data(contents_report, filename_report, sheet_name="Starting_Inventory")
        parameters = parse_excel_data(contents_report, filename_report, sheet_name="Parameters")

        prg_sales_data = parse_data(content_act_sales, filename_act_sales)

        def to_xlsx(bytes_io):
            xslx_writer = pd.ExcelWriter(bytes_io)
            xslx_writer.save()
        return send_bytes(to_xlsx, "Report2.xlsx")
###############################################################################


@app.callback(Output("download_ug", "data"), [Input("btn1", "n_clicks")])
def downoad_user_guide(n_clicks):
    return send_file("./assets/User Guide.pdf")


@app.callback(Output("download_hst", "data"), [Input("btn2", "n_clicks")])
def download_hist_sales_templt(n_clicks):
    return send_file("./assets/Historical_Sales_Template.csv")


@app.callback(Output("download_ist", "data"), [Input("btn3", "n_clicks")])
def download_inv_snap_templt(n_clicks):
    return send_file("./assets/Inventory_Snapshot_Template.csv")


@app.callback(Output("download_rst", "data"), [Input("btn4", "n_clicks")])
def download_rt_sales_templt(n_clicks):
    return send_file("./assets/Real_Sales_Template.csv")


#### CALLBACK FOR DISABLING INPUTS BASED ON ALGO ##############################
@app.callback([Output('eval_period', 'disabled'),
               Output('md_delta', 'disabled'),
               Output('first_r_ub', 'disabled')],
              [Input('algo_select_dropdown', 'value')])
def set_button_enabled_state(algo_selected):
    if algo_selected == 2:
        flag = True
    else:
        flag = False
    return flag, flag, flag
###############################################################################


container1 = html.Div([
    dbc.Row([
        dbc.Col(col1, width=3),
        dbc.Col(container2, width=9),
    ])
], style={"marginTop": 5, "height": "50%"})


app.layout = html.Div(children=[
    navbar,
    modal,
    container1
])


if __name__ == "__main__":
    app.run_server(port=8051, use_reloader=False, debug=True)
