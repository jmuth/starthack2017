'use strict';

// Status constants
const OK_STATUS = "OK";
const PENDING_STATUS = "Pending";
const NOT_EXISTING_STATUS = "Not existing";

// Web constants
const HOST = "http://localhost";
const SERVER_PORT = "8080";
const SERVER = HOST + ":" + SERVER_PORT;

// Color/style constants
const BASE_OPACITY = 0.3;
const MIN_OPACITY = 0.1;

// Map constants
const LONGITUDE = 7.0595531;
const LATITUDE = 45.011663;
const ZOOM = 8;

let colorLayerGroup = L.featureGroup();
let pathGroup = L.featureGroup();
let isochroneId = -1;

let map = L.map('map').setView([LATITUDE, LONGITUDE], ZOOM);

// Thanks http://stackoverflow.com/questions/32554624/casting-a-number-to-a-string-in-typescript
function toHHMMSS(time) {
    var hours   = Math.floor(time / 3600).toString();
    var minutes = Math.floor((time - (parseInt(hours) * 3600)) / 60).toString();
    var seconds = (time - (parseInt(hours) * 3600) - (parseInt(minutes) * 60)).toString();

    if (parseInt(hours)   < 10) {hours   = "0"+hours;}
    if (parseInt(minutes) < 10) {minutes = "0"+minutes;}
    if (parseInt(seconds) < 10) {seconds = "0"+seconds;}
    return hours+':'+minutes+':'+seconds;
}

// Thanks http://stackoverflow.com/questions/979975/how-to-get-the-value-from-the-get-parameters
function getQueryParams(qs) {
    qs = qs.split('+').join(' ');

    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }

    return params;
}

function httpGetAsync(theUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            callback(xmlHttp.responseText);
        }
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

function ajaxPost(url, jsonData, callback) {
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: jsonData,
        processData: false,
        contentType: "application/json"
    })
    .done(callback);
}

function waitUntilDisplayingFeatures(data) {
    isochroneId = data['id'];
    console.log("Got id: " + isochroneId);
    getFeaturesFromServer(displayFeatures);
}

function setTimeoutForGettingFeatures() {
    setTimeout(function() {getFeaturesFromServer(displayFeatures);}, 4000);
}

function getFeaturesFromServer(successCallback) {
    $.get(SERVER + "/isochrones/" + isochroneId, function(responseText) {
        var status = responseText['status'];
        console.log("Status for isochrone: " + status);
        switch (status) {
            case OK_STATUS:
                successCallback(responseText['geoJSON'], responseText['totalLayers']);
                break;
            case PENDING_STATUS:
                setTimeoutForGettingFeatures();
                break;
            case NOT_EXISTING_STATUS:
                alert("You are trying to get an unexisting isochrone. Please try again.");
                break;
            default:
                break;
        }
    });
}

function displayFeatures(features, totalLayers) {
    colorLayerGroup.eachLayer((layer) => {
        map.removeLayer(layer);
    });

    features.forEach((f) => {
        let geoJsonLayer = L.geoJSON(f, {
            style: function(feature) {
                // If only 1 layer, display in red
                let col = "#FF0000";

                let layerNb = feature.properties.layerNb;

                if (totalLayers > 1) {
                    let b = (0).toString(16);

                    if (layerNb >= totalLayers / 2) {
                        let x = (layerNb - totalLayers/2) / (totalLayers - totalLayers/2);
                        if (layerNb - 1 < totalLayers / 2 && x != 0) {
                            x = 0;
                        }

                        // Compute color depending on the layerNb and the totalLayers
                        var r = Math.min(255, Math.round((1 - x) * 2.0 * 255)).toString(16);
                        var g = Math.min(255, Math.round(x * 2.0 * 255)).toString(16);

                    }
                    else {
                        let x = (layerNb - 1.0) / (totalLayers/2 - 1.0);

                        var r = Math.round(x * 255).toString(16);
                        var g = (0).toString(16);

                    }

                    r = r.length == 1 ? '0' + r : r;
                    g = g.length == 1 ? '0' + g : g;
                    b = b.length == 1 ? '0' + b : b;

                    col = "#" + r.toString(16) + g.toString(16) + b.toString(16);
                }

                //let opacity = layerNb / totalLayers * (BASE_OPACITY - MIN_OPACITY) + MIN_OPACITY;                
                let opacity = 1;

                return {
                    weight: 0,
                    fillRule: 'nonzero',
                    fillOpacity: opacity,
                    color: col
                }
            }
        });

        colorLayerGroup.addLayer(geoJsonLayer).addTo(map);

    });

    
}

function askForCreatingPathFromPoint(e) {
    $.get(SERVER + "/isochrones/" + isochroneId + "/commuter?lat=" + e.latlng.lat + "&lng=" + e.latlng.lng, function(responseText) {
        let status = responseText['status'];
        console.log("Status for creating path: " + status);
        switch (status) {
            case OK_STATUS:
                createPathFromPoint(responseText['geoJSON'], responseText['destination'], responseText['timeFromInit'], responseText['nbTransfers'],
                    responseText['nbWalkingTransfers'], responseText['totalWaitingTime'], responseText['reverse']);
                break;
            case NOT_EXISTING_STATUS:
                alert("You are trying to get an unexisting isochrone. Please try again.");
                break;
            default:
                break;
        }
    });
}

function createPathFromPoint(polylineFeature, destination, timeFromInit, nbTransfers, nbWalkingTransfers, totalWaitingTime, reverse) {
    // Add polyline to map here
    let polylineLayer = L.geoJSON(polylineFeature, {
        style: {
            weight: 6,
            color: "#0000ff"
        }
    }).addTo(map);

    pathGroup.addLayer(polylineLayer);

    // Open popup with info about the trip
    let destOrDep = (reverse ? "Departure" : "Destination");

    polylineLayer.bindPopup(
        "<p>" + destOrDep + ": <b>" + destination + "</b><br />\
        Time: " + toHHMMSS(timeFromInit) + "<br />\
        Number of transfers: " + nbTransfers + "<br />\
        Number of walking tranfers: " + nbWalkingTransfers + "<br />\
        Total waiting time: " + toHHMMSS(totalWaitingTime) + "</p>"
        ).openPopup();
}

function cleanPaths() {
    pathGroup.eachLayer((layer) => {
        map.removeLayer(layer);
    });
}

function generateIsochrone() {
    let query = getQueryParams(document.location.search);

    let longitude = query.longitude;
    let latitude = query.latitude;
    let maxTimeFromInit = query.maxTimeFromInit;
    let maxWalkingTime = query.maxWalkingTime;
    let maxNbTransfers = query.maxNbTransfers;
    let maxNbWalkingTransfers = query.maxNbWalkingTransfers;
    let startTime = query.startTime;
    let endTime = query.endTime;
    let totalLayers = query.totalLayers;
    let reverse = query.reverse;

    // Build JSON to send
    let dataToSend = new Object();
    dataToSend['longitude'] = longitude;
    dataToSend['latitude'] = latitude;
    dataToSend['maxTimeFromInit'] = maxTimeFromInit;
    dataToSend['maxWalkingTime'] = maxWalkingTime;
    dataToSend['maxNbTransfers'] = maxNbTransfers;
    dataToSend['maxNbWalkingTransfers'] = maxNbWalkingTransfers;
    dataToSend['startTime'] = startTime;
    dataToSend['endTime'] = endTime;
    dataToSend['totalLayers'] = totalLayers;
    dataToSend['reverse'] = reverse;

    let url = SERVER + "/isochrones";

    ajaxPost(url, JSON.stringify(dataToSend), waitUntilDisplayingFeatures);
}

/*
let mapLayer = L.tileLayer.wms("https://tiles.osm.routerank.com/mapcache/", {
        transparent: true,
        format: 'image/png',
        layers: 'mirror',
        attribution: 'Map data © <a href="www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        });

mapLayer.addTo(map);
*/

let mapLayer = L.mapboxGL({
    layers: 'mirror',
    style: 'http://tiles-v2.osm.routerank.com/styles/bright-v9.json',
    accessToken: 'test',
    attribution: 'Map data © <a href="www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, style: Mapbox, tiles: OSM2VectorTiles'
});

mapLayer.addTo(map);

// Add onClickListener for when user clicks on isochrone -> will print the path
colorLayerGroup.on("click", askForCreatingPathFromPoint);

