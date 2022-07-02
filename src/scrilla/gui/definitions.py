from scrilla.gui.widgets.functions import CorrelationWidget, DiscountDividendWidget, DistributionWidget, \
    EfficientFrontierWidget, MovingAverageWidget, OptimizerWidget, \
    RiskProfileWidget, YieldCurveWidget

FUNC_WIDGETS = {
    'correlation': {
        'name': 'Correlation Matrix',
        'class': CorrelationWidget,
        'shortcut': 'Ctrl+1',
        'group': 'analysis'
    },
    'dividend': {
        'name': 'Discount Dividend Model',
        'class': DiscountDividendWidget,
        'shortcut': 'Ctrl+2',
        'group': 'analysis'
    },
    'distribution': {
        'name': 'Distribution of Returns',
        'class': DistributionWidget,
        'shortcut': 'Ctrl+7',
        'group': 'analysis'
    },
    'frontier': {
        'name': 'Efficient Frontiers',
        'class': EfficientFrontierWidget,
        'shortcut': 'Ctrl+3',
        'group': 'analysis'
    },
    'averages': {
        'name': 'Moving Averages',
        'class': MovingAverageWidget,
        'shortcut': 'Ctrl+4',
        'group': 'analysis'
    },
    'optimize': {
        'name': 'Portfolio Optimization',
        'class': OptimizerWidget,
        'shortcut': 'Ctrl+5',
        'group': 'allocation'
    },
    'risk_profile': {
        'name': 'Risk Profile',
        'class': RiskProfileWidget,
        'shortcut': 'Ctrl+8',
        'group': 'analysis'

    },
    'yield_curve': {
        'name': 'Yield Curve',
        'class': YieldCurveWidget,
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
    'ATOMIC':{
        'TYPES': ['widget', 'title', 'subtitle', 'heading', 'label', 'error', 'text', 
            'splash', 'figure', 'footer','calculate-button', 'clear-button', 'hide-button', 
            'download-button', 'source-button', 'package-button', 'documentation-button', 
            'okay-button', 'button','save-dialog' , 'table', 'table-item', 'menu-bar'],
        'LABEL': ['title', 'subtitle', 'heading', 'label', 'error', 'text', 'splash', 'figure', 
            'footer'],
        'BUTTON':  [ 'calculate-button', 'clear-button', 'hide-button', 'download-button', 
            'source-button', 'package-button', 'documentation-button', 'okay-button', 'button'],
        'DIALOG': [ 'save-dialog' ],
        'TABLE':  [ 'table' ],
        'ITEM': [ 'table-item' ],
        'MENU': [ 'menu-bar' ],
        'SIZING':{
            'EXPANDEXPAND': [ 'figure' ],
            'EXPANDMIN': [ 'table' ],
            'MINMAX': [ 'splash', 'hide-button', 'download-button', 'source-button' ],
            'MAXMAX': [ 'calculate-button', 'clear-button', 'package-button', 'documentation-button', 
                'okay-button', 'button'],
            'MINMIN': [ 'widget' ]
        },
        'ALIGN': {
                'TOP': [ 'title', 'subtitle', 'label' ],
                'LEFT': [ 'heading' ],
                'CENTER': [ 'figure' ],
                'HCENTER': [ 'error' ],
                'BOTTOM': [ 'text', 'footer' ]
        },
        'TEMPLATE': [ 'splash' ],
        'TITLED': [ 'hide-button', 'download-button', 'source-button']
    },
    'ARGUMENTS': {
        'TYPES': [ 'date', 'decimal', 'currency', 'integer', 'flag', 'symbol', 'symbols'],
        'LINE': [ 'decimal', 'currency', 'integer', 'symbol', 'symbols'],
        'DATE': [ 'date' ],
        'RADIO': [ 'flag' ],
        'SIZING':{
            'MAXMAX': [ 'decimal', 'currency', 'integer', 'flag' ],
            'MINMAX': [ 'symbol', 'symbols' ]
        },
        'CONSTRAINTS': {
            'LENGTH': ['symbol', 'symbols']
        },
        'DISABLED': [ 'date', 'decimal', 'currency', 'integer']
    }
}
