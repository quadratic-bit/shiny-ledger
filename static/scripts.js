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

const date_begin = document.getElementById("date-begin")
const date_end = document.getElementById("date-end")

const categories_sel = document.getElementById("top-category")

date_begin.onchange = update
date_end.onchange = update

let box = document.getElementById("charts")

let chart2_data = []
let chart2 = c3.generate({
    bindto: "#secondary-chart",
    data: {
        columns: [],
        type: "pie",
    },
    size: {
        width: box.clientWidth * 0.5 * 0.8
    },
    pie: {
        label: {
            format: function (value, _ratio, _id) {
                return formatNumber(value)
            }
        }
    },
    tooltip: {
        format: {
            value: function (value, ratio, _id, _index) {
                return formatNumber(value) + " (" + formatPercent(ratio) + ")"
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
                return formatNumber(value)
            }
        }
    },
    tooltip: {
        format: {
            value: function (value, ratio, _id, _index) {
                return formatNumber(value) + " (" + formatPercent(ratio) + ")"
            }
        }
    }
})

function setup() {
    fetch(HOST + "/categories")
        .then(async r => {
            let data = await r.json()
            for (const category of data) {
                const opt = document.createElement("option")
                opt.textContent = opt.value = category
                categories_sel.appendChild(opt)
            }
            update()
        })
        .catch(e => {
            console.error(e)
        })
}

function update() {
    const category = categories_sel.value
    fetch(HOST + "/stat?category=" + category + "&begin=" + date_begin.value + "&end=" + date_end.value)
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

categories_sel.addEventListener("change", () => {
    update()
})

setup()
