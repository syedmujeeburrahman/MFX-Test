/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { ControlPanel } from "@web/search/control_panel/control_panel";

export class CountryDropdown extends Component {
    static template = "crm_lead_management.CountryDropdown";
    static components = { Dropdown, DropdownItem };
    static supportedModels = ["crm.lead", "x_erp.prospect"];

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            countries: [],
            selectedId: false,
            label: "Countries",
            isOpen: false,
        });
        this._currentGroupId = null;

        // Subscribe to searchModel notifications so country counts
        // update automatically when stage or other filters change.
        const searchModel = this.env.searchModel;
        if (searchModel) {
            searchModel.addEventListener("update", () => this._loadCountries());
        }

        onWillStart(() => this._loadCountries());
    }

    /**
     * Build the active search domain from the searchModel,
     * excluding any country_id filter that this dropdown itself created.
     */
    _getActiveDomain() {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return [];
        }
        // Get the full domain from the search model (includes searchpanel
        // selections like stage_id, lead_type, plus any search bar filters).
        let domain = [];
        try {
            domain = searchModel.domain || [];
        } catch {
            return [];
        }
        // Remove any country_id conditions that our own dropdown created,
        // so we don't filter countries by themselves.
        const filtered = [];
        for (let i = 0; i < domain.length; i++) {
            const clause = domain[i];
            if (Array.isArray(clause) && clause.length === 3 && clause[0] === "country_id") {
                continue;
            }
            filtered.push(clause);
        }
        return filtered;
    }

    async _loadCountries() {
        try {
            // Combine the active search domain (stage, lead type, etc.)
            // with the base country_id filter. This ensures counts are
            // scoped to whatever filters the user has selected.
            const resModel = this.env.searchModel?.resModel;
            if (!CountryDropdown.supportedModels.includes(resModel)) {
                this.state.countries = [];
                return;
            }
            const activeDomain = this._getActiveDomain();
            const baseDomain = [["country_id", "!=", false]];
            const combinedDomain = [...activeDomain, ...baseDomain];

            const groups = await this.orm.call(
                resModel,
                "read_group",
                [combinedDomain, ["country_id"], ["country_id"]]
            );
            const countries = [];
            for (const g of groups) {
                if (g.country_id) {
                    countries.push({
                        id: g.country_id[0],
                        name: g.country_id[1],
                        count: g.country_id_count || g.__count || 0,
                    });
                }
            }
            countries.sort((a, b) => a.name.localeCompare(b.name));
            this.state.countries = countries;
        } catch (e) {
            console.error("CountryDropdown: failed to load countries", e);
            this.state.countries = [];
        }
    }

    /**
     * Reload countries every time the dropdown opens so that
     * newly added countries on leads are immediately visible.
     */
    async onBeforeOpen() {
        await this._loadCountries();
    }

    /**
     * Track dropdown open/close state for arrow rotation.
     * @param {boolean} isOpen
     */
    onDropdownStateChanged(isOpen) {
        this.state.isOpen = isOpen;
    }

    selectCountry(country) {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return;
        }
        if (this._currentGroupId !== null) {
            searchModel.deactivateGroup(this._currentGroupId);
            this._currentGroupId = null;
        }
        this.state.selectedId = country.id;
        this.state.label = country.name;

        const preFilter = {
            description: country.name,
            domain: `[("country_id", "=", ${country.id})]`,
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
        this.state.selectedId = false;
        this.state.label = "Countries";
    }
}

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
ControlPanel.components = Object.assign({}, ControlPanel.components, {
    CountryDropdown,
    LeadLevelDropdown,
});

// Patch ControlPanel to determine when to show the dropdown
patch(ControlPanel.prototype, {
    setup() {
        super.setup();
        this.showCountryDropdown = CountryDropdown.supportedModels.includes(this.env.searchModel?.resModel);
        this.showLeadLevelDropdown = LeadLevelDropdown.supportedModels.includes(this.env.searchModel?.resModel);
    },
});
