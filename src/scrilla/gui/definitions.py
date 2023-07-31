# using literal class here causes circular import

FUNC_WIDGETS = {
    'correlation': {
        'name': 'Correlation Matrix',
        'shortcut': 'Ctrl+1',
        'group': 'analysis'
    },
    'discount_dividend': {
        'name': 'Discount Dividend Model',
        'shortcut': 'Ctrl+2',
        'group': 'analysis'
    },
    'plot_return_dist': {
        'name': 'Distribution of Returns',
        'shortcut': 'Ctrl+7',
        'group': 'analysis'
    },
    'efficient_frontier': {
        'name': 'Efficient Frontiers',
        'shortcut': 'Ctrl+3',
        'group': 'analysis'
    },
    'moving_averages': {
        'name': 'Moving Averages',
        'shortcut': 'Ctrl+4',
        'group': 'analysis'
    },
    'optimize_portfolio': {
        'name': 'Portfolio Optimization',
        'shortcut': 'Ctrl+5',
        'group': 'allocation'
    },
    'risk_profile': {
        'name': 'Risk Profile',
        'shortcut': 'Ctrl+8',
        'group': 'analysis'

    },
    'yield_curve': {
        'name': 'Yield Curve',
        'shortcut': 'Ctrl+9',
        'group': 'prices'
    }
}

MENUBAR_WIDGET = {
    'Account': [
        {
            'name': 'Add API Key',
            'shortcut': 'Ctrl+A',
            'options': ['AlphaVantage', 'IEX', 'Quandl']
        }
    ],
    'View': [
        {
            'name': 'Function Menu',
            'shortcut': 'Ctrl+F'
        },
        {
            'name': 'Splash Menu',
            'shortcut': 'Ctrl+S'
        }
    ],
    'Functions': [
        {
            'name': FUNC_WIDGETS[func_widget]['name'],
            'shortcut': FUNC_WIDGETS[func_widget]['shortcut']
        } for func_widget in FUNC_WIDGETS
    ],
}

FACTORIES = {
    'ATOMIC': {
        'TYPES': ['widget', 'title', 'subtitle', 'heading', 'label', 'error', 'text',
                  'splash', 'figure', 'footer', 'calculate-button', 'clear-button', 'hide-button',
                  'download-button', 'source-button', 'package-button', 'documentation-button',
                  'okay-button', 'button', 'save-dialog', 'table', 'table-item', 'menu-bar'],
        'LABEL': ['title', 'subtitle', 'heading', 'label', 'error', 'text', 'splash', 'figure',
                  'footer'],
        'BUTTON':  ['calculate-button', 'clear-button', 'hide-button', 'download-button',
                    'source-button', 'package-button', 'documentation-button', 'okay-button', 'button'],
        'DIALOG': ['save-dialog'],
        'TABLE':  ['table'],
        'ITEM': ['table-item'],
        'MENU': ['menu-bar'],
        'SIZING': {
            'EXPANDEXPAND': ['figure'],
            'EXPANDMIN': ['table'],
<<<<<<< HEAD
            'MINMAX': ['splash', 'calculate-button', 'clear-button', 'package-button', 'documentation-button',
                       'okay-button', 'button'],
            'MAXMAX': ['hide-button', 'download-button', 'source-button', ],
=======
            'MINMAX': ['splash', 'hide-button', 'download-button', 'source-button'],
            'MAXMAX': ['calculate-button', 'clear-button', 'package-button', 'documentation-button',
                       'okay-button', 'button'],
>>>>>>> origin/deepsource-transform-a6cf521a
            'MINMIN': ['widget']
        },
        'ALIGN': {
            'TOP': ['title', 'subtitle', 'label'],
            'LEFT': ['heading'],
            'CENTER': ['figure'],
            'HCENTER': ['error'],
            'BOTTOM': ['text', 'footer']
        },
        'TEMPLATE': ['splash'],
<<<<<<< HEAD
        'TITLED': ['hide-button', 'download-button', 'source-button'],
        'UNTITLED': ['input-label']
=======
        'TITLED': ['hide-button', 'download-button', 'source-button']
>>>>>>> origin/deepsource-transform-a6cf521a
    },
    'ARGUMENTS': {
        'TYPES': ['date', 'decimal', 'currency', 'integer', 'flag', 'symbol', 'symbols'],
        'LINE': ['decimal', 'currency', 'integer', 'symbol', 'symbols'],
        'DATE': ['date'],
        'RADIO': ['flag'],
        'SIZING': {
            'MAXMAX': ['decimal', 'currency', 'integer', 'flag'],
            'MINMAX': ['symbol', 'symbols']
        },
        'CONSTRAINTS': {
            'LENGTH': ['symbol', 'symbols']
        },
        'DISABLED': ['date', 'decimal', 'currency', 'integer']
    }
}
