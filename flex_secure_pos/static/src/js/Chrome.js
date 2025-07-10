/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { Navbar } from '@point_of_sale/app/navbar/navbar';

patch(Navbar.prototype, {
    get showCashMoveButton() {
        return Boolean(this.pos.config.use_cash_in_out);
    },
});
