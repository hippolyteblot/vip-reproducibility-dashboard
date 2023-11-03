from dash import html
import dash_bootstrap_components as dbc

footer = html.Footer(
    dbc.Container(
        [

            html.A(
                'ReproVIP Project',
                href='https://www.creatis.insa-lyon.fr/reprovip/',
                target='_blank',
                className='ml-2',
            ),
            ' - ReproVIP reproducibility dashboard - v1.0 - ',
            html.A(
                'VIP platform',
                href='https://vip.creatis.insa-lyon.fr/',
                target='_blank',
                className='ml-2',
            ),
        ],
    ),
    style={'border-top': '2px solid #e5e5e5', 'padding': '1rem 0'},
)
