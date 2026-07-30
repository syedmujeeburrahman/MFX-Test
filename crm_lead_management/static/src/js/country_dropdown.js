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
        field: "x_lead_level",
        label: "Lead Level",
        allLabel: "All Lead Levels",
        icon: "fa-signal",
        optionIcon: "fa-circle",
        supportedModels: ["crm.lead"],
        selectionLabels: {
            "1": "Level 1",
            "2": "Level 2",
            "3": "Level 3",
            "4": "Level 4",
            "5": "Level 5",
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
        optionModel: "x_erp.crm_erp_system",
    },
    {
        key: "contact_type",
        field: "tag_ids",
        label: "Contact Type",
        allLabel: "All Types",
        icon: "fa-tags",
        optionIcon: "fa-tag",
        supportedModels: ["crm.lead"],
        optionModel: "crm.tag",
        multi: true,
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
            this.state.selectedIds[filter.key] = filter.multi ? [] : false;
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
            const counts = {};
            for (const group of groups) {
                const rawValue = group[filter.field];
                if (!rawValue) {
                    continue;
                }
                const isMany2one = Array.isArray(rawValue);
                const value = isMany2one ? rawValue[0] : rawValue;
                counts[value] = group[`${filter.field}_count`] || group.__count || 0;
            }

            let options = [];
            if (filter.optionModel) {
                options = await this._loadConfiguredOptions(filter, counts);
            } else {
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
                        count: counts[value] || 0,
                    });
                }
            }
            options.sort((a, b) => a.name.localeCompare(b.name));
            this.state.options[filter.key] = options;
        } catch (error) {
            console.error(`LeadFilterDropdown: failed to load ${filter.field}`, error);
            this.state.options[filter.key] = [];
        }
    }

    async _loadConfiguredOptions(filter, counts) {
        const fieldsInfo = await this.orm.call(filter.optionModel, "fields_get", [[]]);
        const nameField = fieldsInfo.x_name ? "x_name" : "name";
        const sequenceField = fieldsInfo.x_sequence ? "x_sequence" : (fieldsInfo.sequence ? "sequence" : false);
        const readFields = ["display_name", nameField];
        if (sequenceField) {
            readFields.push(sequenceField);
        }
        const order = sequenceField ? `${sequenceField}, ${nameField}` : nameField;
        const records = await this.orm.searchRead(filter.optionModel, [], readFields, { order });
        return records.map((record) => {
            return {
                value: record.id,
                name: record.display_name || record[nameField],
                count: counts[record.id] || 0,
            };
        });
    }

    _getSelectedValues(filter) {
        const selected = this.state.selectedIds[filter.key];
        return Array.isArray(selected) ? selected : [];
    }

    hasSelection(filter) {
        return filter.multi ? Boolean(this._getSelectedValues(filter).length) : Boolean(this.state.selectedIds[filter.key]);
    }

    isSelected(filter, option) {
        return filter.multi ? this._getSelectedValues(filter).includes(option.value) : this.state.selectedIds[filter.key] === option.value;
    }

    _setMultiSelection(filter, selectedValues) {
        this.state.selectedIds[filter.key] = selectedValues;
        if (!selectedValues.length) {
            this.state.labels[filter.key] = filter.label;
        } else if (selectedValues.length === 1) {
            const selectedOption = this.state.options[filter.key].find((option) => option.value === selectedValues[0]);
            this.state.labels[filter.key] = selectedOption?.name || filter.label;
        } else {
            this.state.labels[filter.key] = `${selectedValues.length} Types`;
        }
    }

    _applyFilter(filter, description, domain) {
        const searchModel = this.env.searchModel;
        if (!searchModel) {
            return;
        }
        const groupId = this._currentGroupIds[filter.key];
        if (groupId !== undefined && groupId !== null) {
            searchModel.deactivateGroup(groupId);
            this._currentGroupIds[filter.key] = null;
        }
        const preFilter = { description, domain };
        searchModel.createNewFilters([preFilter]);
        this._currentGroupIds[filter.key] = preFilter.groupId;
    }

    toggleOption(filter, option) {
        if (!filter.multi) {
            this.selectOption(filter, option);
            return;
        }
        const selected = [...this._getSelectedValues(filter)];
        const existingIndex = selected.indexOf(option.value);
        if (existingIndex >= 0) {
            selected.splice(existingIndex, 1);
        } else {
            selected.push(option.value);
        }
        this._setMultiSelection(filter, selected);
        if (!selected.length) {
            this.clearFilter(filter);
            return;
        }
        this._applyFilter(
            filter,
            `${filter.label}: ${this.state.labels[filter.key]}`,
            `[("${filter.field}", "in", ${JSON.stringify(selected)})]`
        );
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

        this._applyFilter(
            filter,
            `${filter.label}: ${option.name}`,
            `[("${filter.field}", "=", ${JSON.stringify(option.value)})]`
        );
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
        this.state.selectedIds[filter.key] = filter.multi ? [] : false;
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
