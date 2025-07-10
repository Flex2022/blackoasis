import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(ControlButtons.prototype, {
     setup() {
        super.setup(...arguments);
        this.report = useService("report");
    },
    get printZReportAllowed() {
        return this.pos.get_cashier().pos_print_session_report && this.pos.config.enable_session_report;
    },
    async clickPrintZReport() {
        return this.report.doAction("bi_pos_closed_session_reports.action_report_session_z", [this.pos.session.id]);
    },

});
