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

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            countries: [],
            selectedId: false,
            label: "Countries",
            isOpen: false,
        });
        this._currentGroupId = null;
        onWillStart(() => this._loadCountries());
    }

    async _loadCountries() {
        try {
            // Use orm.call with positional args for maximum reliability.
            // read_group(domain, fields, groupby) returns countries that
            // have at least one lead associated with them.
            const groups = await this.orm.call(
                "crm.lead",
                "read_group",
                [[["country_id", "!=", false]], ["country_id"], ["country_id"]]
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

// Register CountryDropdown as a sub-component of ControlPanel
ControlPanel.components = Object.assign({}, ControlPanel.components, {
    CountryDropdown,
});

// Patch ControlPanel to determine when to show the dropdown
patch(ControlPanel.prototype, {
    setup() {
        super.setup();
        this.showCountryDropdown = this.env.searchModel?.resModel === "crm.lead";
    },
});
