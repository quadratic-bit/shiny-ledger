const HOST = "http://127.0.0.1:8000"
const CURRENCY = "₽"

const formatLocale = d3.formatLocale({
    thousands: ",",
    grouping: [3],
    decimal: ".",
    currency: [CURRENCY, ""]
})
const formatNumber = formatLocale.format("$,.2f")
const formatPercent = formatLocale.format(".1%")

const date_begin = document.getElementById("whatever-1")
const date_end = document.getElementById("whatever-2")

date_begin.onchange = bruh
date_end.onchange = bruh

let box = document.getElementById("charts")

let chart2_data = []
let chart2 = c3.generate({
    bindto: "#secondary-chart",
    data: {
        columns: [],
        type: "pie",
    },
    size: {
        width: box.clientWidth / 2.0
    },
    pie: {
        label: {
            format: function (value, _ratio, _id) {
                return formatNumber(value);
            }
        }
    },
    tooltip: {
        format: {
            value: function (value, ratio, _id, _index) {
                return formatNumber(value) + " (" + formatPercent(ratio) + ")";
            }
        }
    }
})

let chart = c3.generate({
    bindto: "#chart",
    data: {
        columns: [],
        type: "pie",
        onclick: function (d, _i) {
            let data = []
            for (const [label, number] of Object.entries(chart2_data[d.id])) {
                let record = [label, number]
                data.push(record)
            }
            chart2.load({ unload: true, columns: data })
        }
    },
    size: {
        width: box.clientWidth / 2.0
    },
    pie: {
        label: {
            format: function (value, _ratio, _id) {
                return formatNumber(value);
            }
        }
    },
    tooltip: {
        format: {
            value: function (value, ratio, _id, _index) {
                return formatNumber(value) + " (" + formatPercent(ratio) + ")";
            }
        }
    }
})

function bruh() {
    fetch(HOST + "/expenses?begin=" + date_begin.value + "&end=" + date_end.value)
        .then(async r => {
            let data = await r.json()
            chart2_data = data
            let buffer = []
            for (const [label, categories] of Object.entries(data)) {
                let record = []
                record.push(label)
                record.push(...Object.values(categories))
                buffer.push(record)
            }
            chart.load({ unload: true, columns: buffer })
        })
        .catch(e => {
            console.error(e)
        })
}

bruh()
