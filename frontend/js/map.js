/**
 * Map Initialization Module using Leaflet.js
 */

/**
 * Initializes the Leaflet map inside the target container.
 * @param {string} containerId - The ID of the HTML element container.
 * @param {Object} options - Center coordinates and zoom level.
 * @returns {L.Map} - The Leaflet map instance.
 */
export function initMap(containerId, { lat, lng, zoom } = { lat: -33.4489, lng: -70.6693, zoom: 8 }) {
  const map = L.map(containerId, {
    zoomControl: false // Custom controls placement is nicer
  });

  // Add zoom control at bottom-right for clean sidebar layout
  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // Load a sleek, dark-themed base map (CartoDB Dark Matter)
  const baseLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  });

  baseLayer.addTo(map);

  return map;
}

/**
 * Centers the map on a given bounding box.
 * @param {L.Map} map - Leaflet map instance.
 * @param {Array<number>} bbox - Bounding box [min_lng, min_lat, max_lng, max_lat]
 */
export function zoomToBBox(map, bbox) {
  if (!bbox || bbox.length !== 4) return;
  const bounds = L.latLngBounds([
    [bbox[1], bbox[0]],
    [bbox[3], bbox[2]]
  ]);
  map.fitBounds(bounds, { padding: [50, 50] });
}
