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
        this._currentGroupId = null;
        onWillStart(() => this._loadCountries());
    }

    async _loadCountries() {
        try {
            // Use searchRead to fetch all leads with a country, then
            // deduplicate client-side.  This is more reliable across
            // Odoo versions than readGroup (field-name differences).
            const leads = await this.orm.searchRead(
                "crm.lead",
                [["country_id", "!=", false]],
                ["country_id"],
                { limit: false }
            );
            const countryMap = {};
            for (const lead of leads) {
                if (lead.country_id) {
                    const [id, name] = lead.country_id;
                    if (!countryMap[id]) {
                        countryMap[id] = { id, name, count: 0 };
                    }
                    countryMap[id].count++;
                }
            }
            this.state.countries = Object.values(countryMap).sort((a, b) =>
                a.name.localeCompare(b.name)
            );
        } catch (e) {
            console.error("CountryDropdown: failed to load countries", e);
        }
    }

    /**
     * Reload countries every time the dropdown is opened so that
     * newly added / manually set countries on leads are reflected.
     */
    async onBeforeOpen() {
        await this._loadCountries();
    }

    selectCountry(country) {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return;
        }
        // Remove previous country filter if active
        if (this._currentGroupId !== null) {
            searchModel.deactivateGroup(this._currentGroupId);
            this._currentGroupId = null;
        }

        this.state.selectedId = country.id;
        this.state.label = country.name;

        // Create a new dynamic filter for the selected country.
        // createNewFilters mutates the preFilter object, adding groupId & id.
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
