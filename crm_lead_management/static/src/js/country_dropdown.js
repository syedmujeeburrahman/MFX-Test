/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { ControlPanel } from "@web/search/control_panel/control_panel";

const FILTER_DEFINITIONS = [
    {
        key: "country",
        field: "country_id",
        label: "Countries",
        allLabel: "All Countries",
        icon: "fa-globe",
        optionIcon: "fa-flag-o",
        supportedModels: ["crm.lead", "x_erp.prospect"],
    },
    {
        key: "lead_level",
        field: "x_lead_type",
        label: "Lead Level",
        allLabel: "All Lead Levels",
        icon: "fa-fire",
        optionIcon: "fa-circle",
        supportedModels: ["crm.lead"],
        selectionLabels: {
            hot: "Hot",
            warm: "Warm",
            cold: "Cold",
        },
    },
    {
        key: "erp",
        field: "x_erp_system_id",
        label: "ERP",
        allLabel: "All ERP",
        icon: "fa-cogs",
        optionIcon: "fa-cog",
        supportedModels: ["crm.lead"],
    },
    {
        key: "contact_type",
        field: "x_contact_type_id",
        label: "Contact Type",
        allLabel: "All Contact Types",
        icon: "fa-address-card",
        optionIcon: "fa-user-o",
        supportedModels: ["crm.lead"],
    },
];

export class CountryDropdown extends Component {
    static template = "crm_lead_management.CountryDropdown";
    static components = { Dropdown, DropdownItem };
    static supportedModels = [...new Set(FILTER_DEFINITIONS.flatMap((filter) => filter.supportedModels))];

    setup() {
        this.orm = useService("orm");
        this.filters = FILTER_DEFINITIONS;
        this.state = useState({
            options: {},
            selectedIds: {},
            labels: {},
            open: {},
        });
        this._currentGroupIds = {};

        for (const filter of this.filters) {
            this.state.options[filter.key] = [];
            this.state.selectedIds[filter.key] = false;
            this.state.labels[filter.key] = filter.label;
            this.state.open[filter.key] = false;
        }

        const searchModel = this.env.searchModel;
        if (searchModel) {
            searchModel.addEventListener("update", () => this._loadAllOptions());
        }

        onWillStart(() => this._loadAllOptions());
    }

    _isFilterSupported(filter) {
        return filter.supportedModels.includes(this.env.searchModel?.resModel);
    }

    _visibleFilters() {
        return this.filters.filter((filter) => this._isFilterSupported(filter));
    }

    _getActiveDomain(excludedField) {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return [];
        }
        let domain = [];
        try {
            domain = searchModel.domain || [];
        } catch {
            return [];
        }
        return domain.filter((clause) => {
            return !(Array.isArray(clause) && clause.length === 3 && clause[0] === excludedField);
        });
    }

    async _loadAllOptions() {
        await Promise.all(this._visibleFilters().map((filter) => this._loadOptions(filter)));
    }

    async _loadOptions(filter) {
        try {
            const resModel = this.env.searchModel?.resModel;
            if (!this._isFilterSupported(filter)) {
                this.state.options[filter.key] = [];
                return;
            }

            const activeDomain = this._getActiveDomain(filter.field);
            const combinedDomain = [...activeDomain, [filter.field, "!=", false]];
            const groups = await this.orm.call(
                resModel,
                "read_group",
                [combinedDomain, [filter.field], [filter.field]]
            );
            const options = [];
            for (const group of groups) {
                const rawValue = group[filter.field];
                if (!rawValue) {
                    continue;
                }
                const isMany2one = Array.isArray(rawValue);
                const value = isMany2one ? rawValue[0] : rawValue;
                const name = isMany2one ? rawValue[1] : (filter.selectionLabels?.[rawValue] || rawValue);
                options.push({
                    value,
                    name,
                    count: group[`${filter.field}_count`] || group.__count || 0,
                });
            }
            options.sort((a, b) => a.name.localeCompare(b.name));
            this.state.options[filter.key] = options;
        } catch (error) {
            console.error(`LeadFilterDropdown: failed to load ${filter.field}`, error);
            this.state.options[filter.key] = [];
        }
    }

    async onBeforeOpen(filter) {
        await this._loadOptions(filter);
    }

    onDropdownStateChanged(filter, isOpen) {
        this.state.open[filter.key] = isOpen;
    }

    selectOption(filter, option) {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return;
        }
        this.clearFilter(filter);

        this.state.selectedIds[filter.key] = option.value;
        this.state.labels[filter.key] = option.name;

        const preFilter = {
            description: `${filter.label}: ${option.name}`,
            domain: `[("${filter.field}", "=", ${JSON.stringify(option.value)})]`,
        };
        searchModel.createNewFilters([preFilter]);
        this._currentGroupIds[filter.key] = preFilter.groupId;
    }

    clearFilter(filter) {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return;
        }
        const groupId = this._currentGroupIds[filter.key];
        if (groupId !== undefined && groupId !== null) {
            searchModel.deactivateGroup(groupId);
            this._currentGroupIds[filter.key] = null;
        }
        this.state.selectedIds[filter.key] = false;
        this.state.labels[filter.key] = filter.label;
    }
}

ControlPanel.components = Object.assign({}, ControlPanel.components, {
    CountryDropdown,
});

patch(ControlPanel.prototype, {
    setup() {
        super.setup();
        this.showCountryDropdown = CountryDropdown.supportedModels.includes(this.env.searchModel?.resModel);
    },
});
