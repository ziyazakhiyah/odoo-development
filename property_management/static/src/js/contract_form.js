/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ContractForm = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        'click .add-line': '_onAddLine',
        'click .remove-line': '_onRemoveLine',
        'change .property-select': '_onPropertyChange',
        'change #start_date': '_recalculateAll',
        'change #end_date': '_recalculateAll',
        'change #contract_type': '_recalculateAll',
    },

    start() {
        this._super(...arguments);
        const $tableBody = $('tbody#property_lines_body');
        const $rows = $tableBody.find('tr');
        this.lineIndex = $rows.length || 1;
        this._recalculateAll();
    },

    _onAddLine(ev) {
        ev.preventDefault();
        const $tableBody = $('tbody#property_lines_body');
        const $firstRow = $tableBody.find('tr.property-line:first');
        const $newRow = $firstRow.clone();

        const $select = $newRow.find('select.property-select');
        const $qty = $newRow.find('input.quantity');
        const $price = $newRow.find('input.price');
        const $amount = $newRow.find('input.amount');

        $select.val('');
        $qty.val('');
        $price.val('');
        $amount.val('');

        $select.attr('name', `property_id_${this.lineIndex}`);
        $qty.attr('name', `qty_${this.lineIndex}`);
        $price.attr('name', `price_${this.lineIndex}`);
        $amount.attr('name', `amount_${this.lineIndex}`);

        $tableBody.append($newRow);
        this.lineIndex++;
        this._recalculateAll();
    },

    _onRemoveLine(ev) {
        ev.preventDefault();
        const $rows = $('tbody#property_lines_body tr.property-line');
        if ($rows.length > 1) {
            $(ev.currentTarget).closest('tr').remove();
            this._recalculateAll();
        } else {
            alert('You must have at least one property line.');
        }
    },

    _onPropertyChange(ev) {
        this._recalculateAll();
    },

    _recalculateAll() {
        const $startDateInput = $('#start_date');
        const $endDateInput = $('#end_date');
        const $contractType = $('#contract_type');
        const $totalAmount = $('#total_amount');
        const $propertyRows = $('tbody#property_lines_body tr.property-line');

        const startDate = new Date($startDateInput.val());
        const endDate = new Date($endDateInput.val());
        const contractTypeValue = $contractType.val();

        let daysDiff = 0;
        if (!isNaN(startDate) && !isNaN(endDate) && endDate >= startDate) {
            daysDiff = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24));
        }

        const selectedPropertyIds = [];
        $propertyRows.each((index, row) => {
            const $row = $(row);
            const $select = $row.find('select.property-select');
            const selectedValue = $select.val();
            if (selectedValue) {
                selectedPropertyIds.push(selectedValue);
            }
        });

        let total = 0;
        $propertyRows.each((index, row) => {
            const $row = $(row);
            const $propertySelect = $row.find('select.property-select');
            const $qtyInput = $row.find('input.quantity');
            const $priceInput = $row.find('input.price');
            const $amountInput = $row.find('input.amount');

            const currentValue = $propertySelect.val();

            const $options = $propertySelect.find('option');
            $options.each(function () {
                const $option = $(this);
                const val = $option.val();
                if (val === currentValue || val === "") {
                    $option.show();
                } else if (selectedPropertyIds.includes(val)) {
                    $option.hide();
                } else {
                    $option.show();
                }
            });

            const $selectedOption = $propertySelect.find('option:selected');
            const rent = parseFloat($selectedOption.data('rent')) || 0;
            const legal = parseFloat($selectedOption.data('legal')) || 0;

            $qtyInput.val(daysDiff);

            let price = 0;
            if (contractTypeValue === 'rent') {
                $priceInput.val(rent);
                price = rent;
            } else if (contractTypeValue === 'lease') {
                $priceInput.val(legal);
                price = legal;
            } else {
                $priceInput.val(0);
                $amountInput.val(0);
            }

            const subtotal = price * daysDiff;
            $amountInput.val(subtotal);
            total += subtotal;
        });

        $totalAmount.val(total);
    }
});
