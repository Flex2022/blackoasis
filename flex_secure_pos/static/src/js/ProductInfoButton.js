/** @odoo-module **/

import { ProductInfoButton } from 'point_of_sale.ProductInfoButton';
import { patch } from '@web/core/utils/patch';

patch(ProductInfoButton.prototype, {
    async onClick() {

    }
});
