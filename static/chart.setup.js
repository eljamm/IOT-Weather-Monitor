$(document).ready(function () {
  // ----------------- //
  // Set Chart Options //
  // ----------------- //
  const config = {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          // Define Temperature dataset
          label: "Temperature",
          backgroundColor: "rgb(255, 99, 132)",
          borderColor: "rgb(255, 99, 132)",
          data: [],
          fill: false,
        },
        {
          // Define Humidity dataset
          label: "Humidity",
          backgroundColor: "rgb(62,149,205)",
          borderColor: "rgb(62,149,205)",
          data: [],
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      title: {
        display: true,
        text: "Real-Time Home Monitoring With Flask",
      },
      tooltips: {
        mode: "index",
        intersect: true,
      },
      hover: {
        mode: "nearest",
        intersect: true,
      },
      scales: {
        xAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: "Time",
            },
          },
        ],
        yAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: "Value",
            },
          },
        ],
      },
    },
  };

  // ------------ //
  // Create Chart //
  // ------------ //
  const context = document.getElementById("chart").getContext("2d");
  const lineChart = new Chart(context, config);

  // ------------ //
  // Process Data //
  // ------------ //
  // You can enter the "/chart-data" route to see the json data being sent
  const source = new EventSource("/chart-data");
  source.onmessage = function (event) {
    // Get data from the streamed json
    const data = JSON.parse(event.data);

    // ------------ //
    // Update Chart //
    // ------------ //
    // Shift chart after 20 items to have a sliding effect
    if (config.data.labels.length === 20) {
      config.data.labels.shift(); // Labels
      config.data.datasets[0].data.shift(); // Temperature
      config.data.datasets[1].data.shift(); // Humidity
    }
    // Continuously add items
    config.data.labels.push(data.time);
    config.data.datasets[0].data.push(data.temperature);
    config.data.datasets[1].data.push(data.humidity);
    lineChart.update();

    // ----------- //
    // Update LEDs //
    // ----------- //
    var redLED = document.getElementById("led-red");
    var yellowLED = document.getElementById("led-yellow");
    var blueLED = document.getElementById("led-blue");

    if (data.state_action == 1) {
      // Heater ON
      LED_ON(redLED, "red");
      LED_OFF(blueLED, "blue");
    } else if (data.state_action == 2) {
      // Cooler ON
      LED_OFF(redLED, "red");
      LED_ON(blueLED, "blue");
    } else {
      // Normal Conditions
      LED_OFF(redLED, "red");
      LED_OFF(blueLED, "blue");
    }

    if (data.state_gaz == 1) {
      // Danger !
      LED_ON(yellowLED, "yellow");
    } else {
      // Safe
      LED_OFF(yellowLED, "yellow");
    }

    // ------------- //
    // Update Gauges //
    // ------------- //
    gauge_temp.set(data.temperature);
    gauge_hum.set(data.humidity);
  };
});

// ------------- //
// LED Functions //
// ------------- //
function LED_ON(LED, color) {
  LED.classList.remove("led-" + color + "-inactive");
  LED.classList.add("led-" + color + "-active");
}

function LED_OFF(LED, color) {
  LED.classList.remove("led-" + color + "-active");
  LED.classList.add("led-" + color + "-inactive");
}

// ----------------- //
// Set Gauge Options //
// ----------------- //
var opts = {
  angle: 0.3, // The span of the gauge arc
  lineWidth: 0.14, // The line thickness
  radiusScale: 0.9, // Relative radius
  pointer: {
    length: 0.6, // // Relative to gauge radius
    strokeWidth: 0.035, // The thickness
    color: "#000000", // Fill color
  },
  limitMax: false, // If false, max value increases automatically if value > maxValue
  limitMin: false, // If true, the min value of the gauge will be fixed
  // Colors are red for Temperature
  colorStart: "#A01B1B", // Colors
  colorStop: "#DB1818", // just experiment with them
  strokeColor: "#D1D1D1", // to see which ones work best for you
  generateGradient: true,
  highDpiSupport: true, // High resolution support
};

// ------------------------ //
// Create Temperature Gauge //
// ------------------------ //
var target = document.getElementById("temp");
var gauge_temp = new Donut(target).setOptions(opts);
// Temperature goes from -60°C to 100°C
gauge_temp.maxValue = 100;
gauge_temp.setMinValue(-60);
gauge_temp.animationSpeed = 32;
gauge_temp.set(80); // set start value
gauge_temp.setTextField(document.getElementById("preview-temp"));

// --------------------- //
// Create Humidity Gauge //
// --------------------- //
var target = document.getElementById("hum");
// Modify colors for humidity
opts.colorStart = "#120DB5";
opts.colorStop = "#6081DB";
var gauge_hum = new Donut(target).setOptions(opts);
// Humidity goes from 0% to 100%
gauge_hum.maxValue = 100;
gauge_hum.setMinValue(0);
gauge_hum.animationSpeed = 32;
gauge_hum.set(50); // set start value
gauge_hum.setTextField(document.getElementById("preview-humid"));
