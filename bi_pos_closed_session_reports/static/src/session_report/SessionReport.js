/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {useService} from "@web/core/utils/hooks";
import {Component} from "@odoo/owl";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {SelectionPopup} from "@point_of_sale/app/utils/input_popups/selection_popup";


export class SessionReportButton extends Component {
    static template = "bi_pos_closed_session_reports.SessionReportButton";

    setup() {
        this.report = useService("report");
        this.pos = usePos();
    }

    printSessionReportAllowed() {
        return this.pos.get_cashier().print_session_report_allowed;
    }

    async click() {
        return this.report.doAction("bi_pos_closed_session_reports.action_report_session_z", [this.pos.pos_session.id]);
    }
}

ProductScreen.addControlButton({
    component: SessionReportButton,
    condition: function () {
        return this.pos.config.enable_session_report;
    },
});
