/**
 * API Service for communicating with the FastAPI backend.
 * The BACKEND_URL is derived from window.location so it works whether the
 * frontend is served by FastAPI itself or opened via a separate dev server.
 */

const BACKEND_URL =
  window.location.origin.startsWith('http')
    ? window.location.origin   // served by FastAPI at port 8001
    : 'http://localhost:8001'; // fallback for file:// access

const API_BASE_URL = `${BACKEND_URL}/api/v1`;

/**
 * Checks backend health — calls the dedicated /api/health JSON endpoint.
 * Returns true if the API responds with status "active".
 */
export async function checkBackendStatus() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) return false;
    const data = await response.json();
    return data.status === 'active';
  } catch {
    return false;
  }
}

/**
 * Queries the STAC catalog via the backend.
 * @param {string} sensor - Sensor name (MUX, WPM, WFI)
 * @param {string} commune - Selected commune
 * @param {string} dateStart - Search start date (YYYY-MM-DD)
 * @param {string} dateEnd   - Search end date   (YYYY-MM-DD)
 */
export async function searchScenes({ sensor, commune, dateStart, dateEnd }) {
  const queryParams = new URLSearchParams({
    sensor,
    commune,
    start_date: dateStart,
    end_date: dateEnd
  });
  const response = await fetch(`${API_BASE_URL}/catalog/search?${queryParams}`);
  if (!response.ok) {
    throw new Error(`El catálogo respondió con estado ${response.status}`);
  }
  return response.json();
}

/**
 * Constructs the Leaflet XYZ tile URL template for a given scene and index.
 * Leaflet replaces {x}, {y}, {z} automatically when the layer is rendered.
 */
export function getTileUrl(sceneId, index, colormap) {
  const params = new URLSearchParams({
    scene_id: sceneId,
    index: index || 'raw',
    ...(colormap && { colormap })
  });
  return `${API_BASE_URL}/tiler/tiles/{z}/{x}/{y}?${params}`;
}
