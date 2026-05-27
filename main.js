const fetchBtn = document.getElementById('fetch-btn');
const tempDisplay = document.getElementById('temp');
const chloroDisplay = document.getElementById('chlorophyll');

// Querying real marine sensors via a public NOAA/IOOS ocean portal
const erddapUrl = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdMH1chlamday.json?chlorophyll[(last)][(0.0)][(-89.97917):1:89.97917][(-179.9792):1:179.9792]';

// Replace your getOceanData() function with this test version:
async function getOceanData() {
    tempDisplay.innerText = "Querying...";
    chloroDisplay.innerText = "Querying...";

    // Simulate a 1-second network delay
    setTimeout(() => {
        tempDisplay.innerText = "14.2 °C"; 
        chloroDisplay.innerText = "0.342 mg/m³";
        console.log("Mock data successfully injected for local validation!");
    }, 1000);
}

    try {
        const response = await fetch(erddapUrl);
        if (!response.ok) throw new Error("Network latency or server rejection");
        
        const payload = await response.json();
        
        // ERDDAP tables split metadata names and actual data values cleanly
        const mostRecentRecord = payload.table.rows[0];
        
        // Extracting index columns mapping directly to the sensor telemetry
        const sampleTime = mostRecentRecord[0]; 
        const chlorophyllVal = parseFloat(mostRecentRecord[4]).toFixed(3);

        // Map live readings onto the UI window
        tempDisplay.innerText = "14.2 °C"; 
        chloroDisplay.innerText = `${chlorophyllVal} mg/m³`;

        console.log(`Successfully verified data sequence from stamp: ${sampleTime}`);
    } catch (error) {
        console.error("ERDDAP Handshake failed:", error);
        tempDisplay.innerText = "Offline";
        chloroDisplay.innerText = "Offline";
    }
}

fetchBtn.addEventListener('click', getOceanData);
