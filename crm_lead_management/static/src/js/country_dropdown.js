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
        });
        onWillStart(() => this._loadCountries());
    }

    async _loadCountries() {
        try {
            const groups = await this.orm.readGroup(
                "crm.lead",
                [["country_id", "!=", false]],
                ["country_id"],
                ["country_id"]
            );
            this.state.countries = groups
                .filter((g) => g.country_id)
                .map((g) => ({
                    id: g.country_id[0],
                    name: g.country_id[1],
                    count: g.country_id_count || g.__count || 0,
                }))
                .sort((a, b) => a.name.localeCompare(b.name));
        } catch (e) {
            console.error("CountryDropdown: failed to load countries", e);
        }
    }

    selectCountry(country) {
        this.state.selectedId = country.id;
        this.state.label = country.name;
        this._applyFilter(country.id, country.name);
    }

    clearFilter() {
        this.state.selectedId = false;
        this.state.label = "Countries";
        this._applyFilter(false, "");
    }

    _applyFilter(countryId, label) {
        const searchModel = this.env.searchModel;
        if (!searchModel || typeof searchModel.setDomainParts !== "function") {
            return;
        }
        searchModel.setDomainParts({
            countryDropdown: {
                domain: countryId ? [["country_id", "=", countryId]] : [],
                facetLabel: label || "",
            },
        });
    }
}

// Register CountryDropdown as a sub-component of ControlPanel
ControlPanel.components = Object.assign({}, ControlPanel.components, {
    CountryDropdown,
});

// Patch ControlPanel to determine visibility of CountryDropdown
patch(ControlPanel.prototype, {
    setup() {
        super.setup();
        this.showCountryDropdown = this.env.searchModel?.resModel === "crm.lead";
    },
});
