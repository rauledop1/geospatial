/**
 * API Service for communicating with the FastAPI backend.
 */

const BACKEND_URL = window.location.origin.startsWith('http') ? window.location.origin : 'http://localhost:8001';
const API_BASE_URL = `${BACKEND_URL}/api/v1`;

/**
 * Checks the status of the FastAPI backend.
 */
export async function checkBackendStatus() {
  try {
    const response = await fetch(`${BACKEND_URL}/`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) return false;
    const data = await response.json();
    return data.status === 'active';
  } catch (error) {
    console.warn("Backend connectivity check failed:", error);
    return false;
  }
}

/**
 * Queries the STAC catalog via the backend.
 * @param {string} sensor - Sensor name (MUX, WPM, WFI)
 * @param {string} commune - Selected commune
 * @param {string} dateStart - Search start date
 * @param {string} dateEnd - Search end date
 */
export async function searchScenes({ sensor, commune, dateStart, dateEnd }) {
  try {
    const queryParams = new URLSearchParams({
      sensor,
      commune,
      start_date: dateStart,
      end_date: dateEnd
    });
    const response = await fetch(`${API_BASE_URL}/catalog/search?${queryParams}`);
    if (!response.ok) {
      throw new Error(`Search endpoint responded with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error searching scenes:", error);
    throw error;
  }
}

/**
 * Constructs the URL for the dynamically rendered COG tiles.
 */
export function getTileUrl(sceneId, index, colormap) {
  const params = new URLSearchParams({
    scene_id: sceneId,
    index: index || 'raw',
    ...(colormap && { colormap })
  });
  return `${API_BASE_URL}/tiler/tiles/{z}/{x}/{y}?${params}`;
}
