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

<<<<<<< HEAD
=======
export class LeadLevelDropdown extends Component {
    static template = "crm_lead_management.LeadLevelDropdown";
    static components = { Dropdown, DropdownItem };
    static supportedModels = ["crm.lead"];
    static leadLevels = [
        {
            value: "1",
            name: "Level 1",
            description: "Highest Priority / Serious Lead",
            iconClass: "fa-exclamation-circle text-danger",
        },
        {
            value: "2",
            name: "Level 2",
            description: "High Priority",
            iconClass: "fa-arrow-up text-warning",
        },
        {
            value: "3",
            name: "Level 3",
            description: "Medium Priority",
            iconClass: "fa-minus text-info",
        },
        {
            value: "4",
            name: "Level 4",
            description: "Low Priority",
            iconClass: "fa-arrow-down text-muted",
        },
        {
            value: "5",
            name: "Level 5",
            description: "Very Low Priority",
            iconClass: "fa-angle-double-down text-muted",
        },
    ];

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            levels: LeadLevelDropdown.leadLevels.map((level) => ({ ...level, count: 0 })),
            selectedValue: false,
            label: "Lead Levels",
            isOpen: false,
        });
        this._currentGroupId = null;

        const searchModel = this.env.searchModel;
        if (searchModel) {
            searchModel.addEventListener("update", () => this._loadLevels());
        }

        onWillStart(() => this._loadLevels());
    }

    _getActiveDomain() {
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
        const filtered = [];
        for (let i = 0; i < domain.length; i++) {
            const clause = domain[i];
            if (Array.isArray(clause) && clause.length === 3 && clause[0] === "x_lead_level") {
                continue;
            }
            filtered.push(clause);
        }
        return filtered;
    }

    async _loadLevels() {
        const resModel = this.env.searchModel?.resModel;
        if (!LeadLevelDropdown.supportedModels.includes(resModel)) {
            this.state.levels = [];
            return;
        }
        try {
            const combinedDomain = [
                ...this._getActiveDomain(),
                ["x_lead_level", "!=", false],
            ];
            const groups = await this.orm.call(
                resModel,
                "read_group",
                [combinedDomain, ["x_lead_level"], ["x_lead_level"]]
            );
            const counts = {};
            for (const group of groups) {
                if (group.x_lead_level) {
                    counts[group.x_lead_level] = group.x_lead_level_count || group.__count || 0;
                }
            }
            this.state.levels = LeadLevelDropdown.leadLevels.map((level) => ({
                ...level,
                count: counts[level.value] || 0,
            }));
        } catch (e) {
            console.error("LeadLevelDropdown: failed to load lead levels", e);
            this.state.levels = LeadLevelDropdown.leadLevels.map((level) => ({
                ...level,
                count: 0,
            }));
        }
    }

    async onBeforeOpen() {
        await this._loadLevels();
    }

    onDropdownStateChanged(isOpen) {
        this.state.isOpen = isOpen;
    }

    selectLevel(level) {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return;
        }
        if (this._currentGroupId !== null) {
            searchModel.deactivateGroup(this._currentGroupId);
            this._currentGroupId = null;
        }
        this.state.selectedValue = level.value;
        this.state.label = level.name;

        const preFilter = {
            description: level.name,
            domain: `[("x_lead_level", "=", "${level.value}")]`,
        };
        searchModel.createNewFilters([preFilter]);
        this._currentGroupId = preFilter.groupId;
    }

    clearFilter() {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return;
        }
        if (this._currentGroupId !== null) {
            searchModel.deactivateGroup(this._currentGroupId);
            this._currentGroupId = null;
        }
        this.state.selectedValue = false;
        this.state.label = "Lead Levels";
    }
}

// Register CountryDropdown as a sub-component of ControlPanel
>>>>>>> b16288161f1e74aedca0f3c3df96e232163bed62
ControlPanel.components = Object.assign({}, ControlPanel.components, {
    CountryDropdown,
    LeadLevelDropdown,
});

patch(ControlPanel.prototype, {
    setup() {
        super.setup();
        this.showCountryDropdown = CountryDropdown.supportedModels.includes(this.env.searchModel?.resModel);
        this.showLeadLevelDropdown = LeadLevelDropdown.supportedModels.includes(this.env.searchModel?.resModel);
    },
});
