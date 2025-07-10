# -*- coding: utf-8 -*-
{
    'name': 'Flex Secure POS',
    'description': '',
    'summary': '',
    'version': '18.0.1.1',
    'license': 'LGPL-3',
    'category': '',
    'author': 'Hossam Zaki | Flex-Ops',
    'website': 'https://flex-ops.com',
    'depends': ['point_of_sale', 'pos_hr'],
    'data': [
        'views/pos_config.xml',
        'views/res_config_settings.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'flex_secure_pos/static/src/js/Chrome.js',
            # 'flex_secure_pos/static/src/js/ClosePosPopup.js',
            # 'flex_secure_pos/static/src/js/ProductInfoButton.js',

            'flex_secure_pos/static/src/xml/ClosePosPopup.xml',
            # 'flex_secure_pos/static/src/xml/ProductInfoButton.xml',
            # 'flex_secure_pos/static/src/xml/ProductItem.xml',
        ],
    },
}
