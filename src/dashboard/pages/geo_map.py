#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(page_title="Carte IPs réseau", layout="wide")
st.title("🗺️ IPs actives (mise à jour en arrière‑plan)")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Roboto, system-ui, sans-serif; }
        body { margin: 0; padding: 0; background: #f4f6fa; }

        #map { height: 600px; width: 100%; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

        #info {
            position: absolute;
            top: 16px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.75);
            color: white;
            padding: 8px 20px;
            border-radius: 30px;
            backdrop-filter: blur(6px);
            z-index: 1000;
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.3px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }

        .legend {
            position: absolute;
            bottom: 30px;
            right: 30px;
            background: rgba(255,255,255,0.92);
            padding: 12px 16px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            backdrop-filter: blur(4px);
            z-index: 1000;
            font-size: 13px;
            font-weight: 500;
            border: 1px solid rgba(255,255,255,0.3);
        }
        .legend-item { display: flex; align-items: center; margin: 5px 0; }
        .legend-color { width: 18px; height: 18px; border-radius: 50%; margin-right: 10px; border: 1px solid rgba(0,0,0,0.1); }

        /* === STATISTIQUES === */
        #stats {
            margin-top: 24px;
            display: flex;
            gap: 18px;
            justify-content: center;
            flex-wrap: wrap;
            padding: 0 20px;
        }
        .stat-card {
            background: white;
            padding: 14px 32px;
            border-radius: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            text-align: center;
            min-width: 140px;
            border: 1px solid #eef2f6;
            transition: transform 0.15s;
        }
        .stat-card:hover { transform: translateY(-2px); }
        .stat-card .value {
            font-size: 28px;
            font-weight: 700;
            color: #1e2a3a;
            line-height: 1.2;
        }
        .stat-card .label {
            font-size: 13px;
            color: #6b7a8f;
            font-weight: 500;
            letter-spacing: 0.3px;
            margin-top: 4px;
        }

        /* === TABLEAU === */
        #table-container {
            margin: 24px 20px 20px 20px;
            background: white;
            border-radius: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
            border: 1px solid #e9edf2;
        }
        #table-container h3 {
            padding: 16px 20px 0 20px;
            margin: 0;
            font-size: 18px;
            font-weight: 600;
            color: #1e2a3a;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        #table-container h3 span {
            background: #eef2f7;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            color: #2c3e50;
        }

        #table-container table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        #table-container thead th {
            background: #1e2a3a;
            color: #ffffff;
            padding: 12px 18px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 0.4px;
            text-transform: uppercase;
            border-bottom: 2px solid #2c3e50;
        }
        #table-container tbody td {
            padding: 10px 18px;
            border-bottom: 1px solid #edf2f7;
            color: #1e2a3a;
            vertical-align: middle;
        }
        #table-container tbody tr:nth-child(even) {
            background-color: #fafbfc;
        }
        #table-container tbody tr:hover {
            background-color: #eef3f9;
            transition: background 0.15s;
        }

        /* Colonnes spécifiques */
        #table-container .col-ip { font-weight: 600; color: #0b1a2a; }
        #table-container .col-count {
            font-weight: 700;
            color: #e74c3c;
            background: #fef0ee;
            padding: 2px 10px;
            border-radius: 20px;
            display: inline-block;
            font-size: 13px;
        }
        #table-container .col-loc {
            color: #3d5a73;
            font-style: italic;
        }
        #table-container .col-time {
            color: #6b7a8f;
            font-size: 13px;
        }

        /* Message vide */
        .empty-row td {
            text-align: center;
            padding: 30px !important;
            color: #8a9aa8;
            font-style: italic;
            background: #fafbfc !important;
        }

        /* Responsive */
        @media (max-width: 768px) {
            #table-container table { font-size: 12px; }
            #table-container th, #table-container td { padding: 6px 10px; }
            .stat-card { min-width: 100px; padding: 10px 16px; }
            .stat-card .value { font-size: 22px; }
        }
    </style>
</head>
<body>

    <div id="info">🔄 Mise à jour toutes les 5 secondes</div>
    <div id="map"></div>

    <div class="legend">
        <div class="legend-item"><span class="legend-color" style="background:#2ECC71;"></span> Faible activité</div>
        <div class="legend-item"><span class="legend-color" style="background:#F39C12;"></span> Activité moyenne</div>
        <div class="legend-item"><span class="legend-color" style="background:#E74C3C;"></span> Activité élevée</div>
    </div>

    <!-- STATISTIQUES -->
    <div id="stats">
        <div class="stat-card"><div class="value" id="stat-ips">0</div><div class="label">IPs actives</div></div>
        <div class="stat-card"><div class="value" id="stat-attacks">0</div><div class="label">Total attaques</div></div>
        <div class="stat-card"><div class="value" id="stat-private">0</div><div class="label">IPs privées</div></div>
    </div>

    <!-- TABLEAU -->
    <div id="table-container">
        <h3>📋 Dernières IPs actives <span id="table-count">0</span></h3>
        <table>
            <thead>
                <tr>
                    <th>Adresse IP</th>
                    <th>Attaques</th>
                    <th>Dernière vue</th>
                    <th>Localisation</th>
                </tr>
            </thead>
            <tbody id="table-body">
                <tr class="empty-row"><td colspan="4">Chargement des données...</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        // --- Initialisation de la carte (UNE SEULE FOIS) ---
        var map = L.map('map').setView([4.0511, 9.7679], 10);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);

        var markerLayer = L.layerGroup().addTo(map);
        var geoCache = {};

        function getColor(count, maxCount) {
            var ratio = count / maxCount;
            if (ratio < 0.33) return '#2ECC71';
            if (ratio < 0.66) return '#F39C12';
            return '#E74C3C';
        }

        function getRadius(count, maxCount) {
            return 8 + (count / maxCount) * 12;
        }

        function isPrivateIP(ip) {
            return ip.startsWith('10.') || ip.startsWith('192.168.') || ip.startsWith('172.16.');
        }

        function geolocateIP(ip) {
            return new Promise(function(resolve) {
                if (geoCache[ip]) {
                    resolve(geoCache[ip]);
                    return;
                }
                if (isPrivateIP(ip)) {
                    var pos = { lat: 4.0511, lon: 9.7679, label: 'Réseau local' };
                    geoCache[ip] = pos;
                    resolve(pos);
                    return;
                }
                var defaultPos = { lat: 4.0511, lon: 9.7679, label: 'Localisation en cours...' };
                geoCache[ip] = defaultPos;
                resolve(defaultPos);

                fetch('https://ipinfo.io/' + ip + '/json')
                    .then(response => response.json())
                    .then(data => {
                        if (data.loc) {
                            var coords = data.loc.split(',');
                            var lat = parseFloat(coords[0]);
                            var lon = parseFloat(coords[1]);
                            var label = data.city + ', ' + data.country;
                            geoCache[ip] = { lat: lat, lon: lon, label: label };
                        } else {
                            fetch('https://ip-api.com/json/' + ip + '?fields=status,country,city,lat,lon')
                                .then(res => res.json())
                                .then(data2 => {
                                    if (data2.status === 'success') {
                                        geoCache[ip] = { lat: data2.lat, lon: data2.lon, label: data2.city + ', ' + data2.country };
                                    } else {
                                        geoCache[ip] = { lat: 4.0511, lon: 9.7679, label: 'Inconnue' };
                                    }
                                })
                                .catch(function() {
                                    geoCache[ip] = { lat: 4.0511, lon: 9.7679, label: 'Erreur' };
                                });
                        }
                    })
                    .catch(function() {
                        geoCache[ip] = { lat: 4.0511, lon: 9.7679, label: 'Erreur' };
                    })
                    .finally(function() {
                        updateMarkers();
                    });
            });
        }

        function updateMarkers() {
            console.log('🔄 Mise à jour des marqueurs...');
            markerLayer.clearLayers();

            fetch('http://localhost:5001/attackers_ips')
                .then(response => response.json())
                .then(async function(data) {
                    console.log('📊 Données reçues:', data);
                    if (!data || data.length === 0) {
                        document.getElementById('stat-ips').textContent = '0';
                        document.getElementById('stat-attacks').textContent = '0';
                        document.getElementById('stat-private').textContent = '0';
                        document.getElementById('table-count').textContent = '0';
                        document.getElementById('table-body').innerHTML = '<tr class="empty-row"><td colspan="4">Aucune IP active</td></tr>';
                        return;
                    }
                    var maxCount = Math.max(...data.map(item => item.count));
                    var totalAttacks = data.reduce((sum, item) => sum + item.count, 0);
                    var privateCount = data.filter(item => isPrivateIP(item.src_ip)).length;

                    document.getElementById('stat-ips').textContent = data.length;
                    document.getElementById('stat-attacks').textContent = totalAttacks;
                    document.getElementById('stat-private').textContent = privateCount;
                    document.getElementById('table-count').textContent = data.length;

                    var tableBody = document.getElementById('table-body');
                    tableBody.innerHTML = '';
                    data.forEach(function(item) {
                        var pos = geoCache[item.src_ip] || { lat: 4.0511, lon: 9.7679, label: 'Inconnue' };
                        var row = document.createElement('tr');
                        row.innerHTML = '<td class="col-ip">' + item.src_ip + '</td>' +
                                        '<td><span class="col-count">' + item.count + '</span></td>' +
                                        '<td class="col-time">' + (item.last_seen ? item.last_seen.slice(11, 16) : 'N/A') + '</td>' +
                                        '<td class="col-loc">' + pos.label + '</td>';
                        tableBody.appendChild(row);
                    });

                    var promises = data.map(function(item) {
                        return geolocateIP(item.src_ip).then(function(pos) {
                            var color = getColor(item.count, maxCount);
                            var radius = getRadius(item.count, maxCount);
                            var marker = L.circleMarker([pos.lat, pos.lon], {
                                radius: radius,
                                color: color,
                                fillColor: color,
                                fillOpacity: 0.7,
                                weight: 1
                            });
                            marker.bindPopup("<b>" + item.src_ip + "</b><br>Attaques: " + item.count + "<br>" + pos.label);
                            markerLayer.addLayer(marker);
                        });
                    });
                    await Promise.all(promises);
                    console.log('✅ Marqueurs mis à jour - ' + new Date().toLocaleTimeString());
                })
                .catch(function(error) {
                    console.error('❌ Erreur API:', error);
                    document.getElementById('table-body').innerHTML = '<tr class="empty-row"><td colspan="4">Erreur de chargement</td></tr>';
                });
        }

        // Première mise à jour
        updateMarkers();

        // Mise à jour toutes les 5 secondes (sans recharger la page)
        setInterval(updateMarkers, 5000);
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=900)
