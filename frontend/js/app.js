/**
 * Main application orchestrator for the Geoportal.
 */

import { initMap, zoomToBBox } from './map.js';
import { LayerManager } from './layers.js';
import { checkBackendStatus, searchScenes, getTileUrl } from './api.js';

let mapInstance = null;
let layerManagerInstance = null;
let activeScene = null;

document.addEventListener('DOMContentLoaded', async () => {
  console.log("Initializing Geoportal SPA...");

  // 1. Initialize map with Santiago de Chile as center
  const defaultLocation = { lat: -33.4489, lng: -70.6693, zoom: 8 };
  mapInstance = initMap('map', defaultLocation);

  // 2. Initialize Layer Manager
  layerManagerInstance = new LayerManager(mapInstance);

  // 3. Verify Backend connection at startup
  const isConnected = await checkBackendStatus();
  updateConnectionStatus(isConnected);

  // 4. Setup UI Interaction
  setupUIEventListeners();
});

/**
 * Updates the connection status badge in the header.
 */
function updateConnectionStatus(connected) {
  const dot = document.getElementById('status-dot');
  const text = document.getElementById('status-text');
  
  if (connected) {
    dot.classList.add('connected');
    text.textContent = 'Backend Conectado';
  } else {
    dot.classList.remove('connected');
    text.textContent = 'Backend Desconectado';
  }
}

/**
 * Sets up all UI handlers and events.
 */
function setupUIEventListeners() {
  const searchBtn = document.getElementById('search-btn');
  const indexSelect = document.getElementById('index-select');
  const colormapSelect = document.getElementById('colormap-select');

  // Trigger search on click
  searchBtn.addEventListener('click', async () => {
    const sensor = document.getElementById('sensor-select').value;
    const commune = document.getElementById('commune-select').value;
    const dateStart = document.getElementById('date-start').value;
    const dateEnd = document.getElementById('date-end').value;

    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = `
      <div style="text-align: center; padding: 1.5rem; color: var(--text-secondary);">
        <p>Buscando escenas en el catálogo...</p>
      </div>
    `;

    try {
      const data = await searchScenes({ sensor, commune, dateStart, dateEnd });
      
      if (data.status === 'success' && data.count > 0) {
        renderSearchResults(data.results);
      } else {
        resultsContainer.innerHTML = `
          <p style="font-size: 0.8rem; color: var(--text-secondary); text-align: center; margin-top: 1rem;">
            No se encontraron escenas para el criterio seleccionado.
          </p>
        `;
      }
    } catch (error) {
      resultsContainer.innerHTML = `
        <p style="font-size: 0.8rem; color: var(--error-color); text-align: center; margin-top: 1rem;">
          Error al buscar escenas. Verifique la conexión con el servidor.
        </p>
      `;
    }
  });

  // Handle spectral index selection change
  indexSelect.addEventListener('change', (e) => {
    const selectedIndex = e.target.value;
    
    if (selectedIndex === 'raw') {
      colormapSelect.disabled = true;
    } else {
      colormapSelect.disabled = false;
      colormapSelect.value = selectedIndex === 'ndvi' ? 'rdylgn' : 'coolwarm';
    }

    // If there is an active scene on the map, update it on the fly!
    if (activeScene) {
      updateActiveLayer();
    }
  });

  // Handle colormap change
  colormapSelect.addEventListener('change', () => {
    if (activeScene) {
      updateActiveLayer();
    }
  });
}

/**
 * Renders the search results in the sidebar list.
 */
function renderSearchResults(scenes) {
  const resultsContainer = document.getElementById('results-container');
  resultsContainer.innerHTML = ''; // Clear container

  scenes.forEach(scene => {
    const date = new Date(scene.datetime).toLocaleDateString('es-CL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });

    const item = document.createElement('div');
    item.className = 'result-item';
    item.innerHTML = `
      <h4>${scene.id}</h4>
      <p>Fecha: ${date}</p>
      <p style="font-size: 0.7rem; color: var(--accent-color); margin-top: 0.25rem;">Haga clic para cargar en el mapa</p>
    `;

    item.addEventListener('click', () => {
      // Highlight selection
      document.querySelectorAll('.result-item').forEach(el => el.classList.remove('selected'));
      item.classList.add('selected');

      // Set active scene
      activeScene = scene;

      // Zoom to scene
      zoomToBBox(mapInstance, scene.bbox);

      // Load raster overlay
      updateActiveLayer();
    });

    resultsContainer.appendChild(item);
  });
}

/**
 * Updates the active satellite raster overlay based on current selections.
 */
function updateActiveLayer() {
  if (!activeScene) return;

  const index = document.getElementById('index-select').value;
  const colormap = document.getElementById('colormap-select').value;

  const tileUrl = getTileUrl(activeScene.id, index, colormap);
  console.log("Loading tile layer:", tileUrl);
  
  layerManagerInstance.updateRasterOverlay(tileUrl);
}
