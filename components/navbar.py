import dash_bootstrap_components as dbc
import dash_html_components as html

def Navbar():
    XCOUTER_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    navbar = dbc.Navbar(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=XCOUTER_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("XCouter", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://plot.ly",
            ),
            dbc.NavItem(dbc.NavLink("Teams", href="#")),
            dbc.NavItem(dbc.NavLink("Players", href="#")),
            dbc.NavItem(dbc.NavLink("Scouting", href="#")),
            dbc.NavItem(dbc.NavLink("Match Review", href="#")),
        ],
        color="dark",
        dark=True,
    )

    return navbar