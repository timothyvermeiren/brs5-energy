console.log("BRS 5 Energy Monitor");

// The history chart is available in all functions
let historyChartCtx = $("#historyChart");
let historyChart;
const resultaatPositiveColor = "#54babb";
const resultaatNegativeColor = "#e60050";

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function initializeMonitor() {

    console.log("Energy monitor on display. Checking whether there is new data every 1000 ms, refreshing if it's the case. Let's gooo!");

    const productieLabel = $("#productieLabel");
    const afnameLabel = $("#afnameLabel");
    const injectieLabel = $("#injectieLabel");
    const verbruikLabel = $("#verbruikLabel");

    const resultaatLabelValue = $("#resultaatLabelValue");
    const resultaatLabelUnit = $("#resultaatLabelUnit");
    const resultaatLabelLabel = $("#resultaatLabelLabel");
    const resultaatDiv = $("#resultaat");
    const resultaatIndicatorPositive = $("#resultaatIndicatorPositive");
    const resultaatIndicatorNegative = $("#resultaatIndicatorNegative");

    // Get initial values

    let requestMonitorValues = $.ajax({
        url: "/getMonitorValues",
        method: "GET"
    });

    requestMonitorValues.done(function( response ) {
        console.log(response);
        // previousDonationsTotal = response.total_amount;
    });

    requestMonitorValues.fail(function( jqXHR, textStatus ) {
        console.log( "Request failed: " + textStatus );
    });

    while (true) {
        
        await sleep(1000);
        console.log("Checking for new data to display.");

        let requestMonitorValues = $.ajax({
            url: "/getMonitorValues",
            method: "GET"
        });
    
        requestMonitorValues.done(async function( response ) {

            // console.log(response);

            // Update BANs
            productieLabel.text(`${response.productie_current.value} ${response.productie_current.unit}`);
            afnameLabel.text(`${response.afname_current.value} ${response.afname_current.unit}`);
            injectieLabel.text(`${response.injectie_current.value} ${response.injectie_current.unit}`);
            verbruikLabel.text(`${response.verbruik_current.value} ${response.verbruik_current.unit}`);
            
            resultaatLabelValue.text(response.resultaat_current.value);
            resultaatLabelUnit.text(response.resultaat_current.unit);
            resultaatLabelLabel.text(response.resultaat_current.label);

            if (response.resultaat_current.value > 0) {
                resultaatDiv.addClass("resultaatPositive");
                resultaatDiv.removeClass("resultaatNegative");
                resultaatIndicatorPositive.removeClass("d-none");
                resultaatIndicatorNegative.addClass("d-none");
            } else {
                resultaatDiv.removeClass("resultaatPositive");
                resultaatDiv.addClass("resultaatNegative");
                resultaatIndicatorNegative.removeClass("d-none");
                resultaatIndicatorPositive.addClass("d-none");
            }

            // Update Chart
            recordTimestampDate = new Date(Date.parse(response.resultaat_current.record_timestamp)).toLocaleTimeString("nl-BE");
            historyChart.data.labels.push(recordTimestampDate);
            historyChart.data.datasets[0].data.push(response.resultaat_current.value);
            historyChart.data.datasets[0].backgroundColor.push(response.resultaat_current.value > 0 ? resultaatPositiveColor : resultaatNegativeColor);
            if (historyChart.data.datasets[0].data.length >= 2000) {
              historyChart.data.labels.shift();
              historyChart.data.datasets[0].data.shift();
            }
            historyChart.update();
            
        });
    
        requestMonitorValues.fail(function( jqXHR, textStatus ) {
            console.log("Request failed: " + textStatus);
        });
    }

}

async function initializeHistoryChart() {

    console.log("Initializing History Chart");
    // We will have dumped the data through a technique like this: https://stackoverflow.com/questions/44824358/pass-json-to-js-using-django-render
    // In resultaat_history (etc)

    Chart.defaults.backgroundColor = "#666666";
    Chart.defaults.color = "#dddddd";
    Chart.defaults.plugins.legend.display = false;
    
    resultaatHistory = JSON.parse(resultaat_history_data);

    historyChart = new Chart(
      historyChartCtx,
      {
        type: "bar",
        data: {
          labels: resultaatHistory.map(row => new Date(Date.parse(row.record_timestamp)).toLocaleTimeString("nl-BE")),
          datasets: [
            {
              label: "Resultaat",
              data: resultaatHistory.map(row => row.value),
              backgroundColor: resultaatHistory.map(row => row.value > 0 ? resultaatPositiveColor : resultaatNegativeColor)
            }
          ]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      }
    );

}

document.addEventListener("DOMContentLoaded", initializeMonitor);
document.addEventListener("DOMContentLoaded", initializeHistoryChart);