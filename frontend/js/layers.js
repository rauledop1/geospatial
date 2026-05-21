/**
 * Layer Management Module
 */

export class LayerManager {
  /**
   * @param {L.Map} map - Leaflet map instance
   */
  constructor(map) {
    this.map = map;
    this.communeLayer = null;
    this.rasterTileLayer = null;
  }

  /**
   * Adds or updates the vector layer containing Chile's communes.
   * @param {Object} geojsonData - GeoJSON features
   * @param {Function} onEachFeature - Click/hover handlers per commune
   */
  updateCommunesLayer(geojsonData, onEachFeature) {
    if (this.communeLayer) {
      this.map.removeLayer(this.communeLayer);
    }

    this.communeLayer = L.geoJSON(geojsonData, {
      style: {
        color: 'rgba(99, 102, 241, 0.6)',
        weight: 1.5,
        fillColor: 'rgba(99, 102, 241, 0.1)',
        fillOpacity: 0.2,
      },
      onEachFeature: (feature, layer) => {
        // Highlighting styles on hover
        layer.on({
          mouseover: (e) => {
            const l = e.target;
            l.setStyle({
              weight: 3,
              color: '#a855f7',
              fillOpacity: 0.4
            });
            l.bringToFront();
          },
          mouseout: (e) => {
            this.communeLayer.resetStyle(e.target);
          }
        });

        if (onEachFeature) onEachFeature(feature, layer);
      }
    }).addTo(this.map);
  }

  /**
   * Updates the satellite mosaic raster overlay using the dynamic backend tile endpoint.
   * @param {string} tileUrlTemplate - Leaflet XYZ URL template with {x}, {y}, {z}
   */
  updateRasterOverlay(tileUrlTemplate) {
    if (this.rasterTileLayer) {
      this.map.removeLayer(this.rasterTileLayer);
    }

    this.rasterTileLayer = L.tileLayer(tileUrlTemplate, {
      maxZoom: 20,
      opacity: 0.85,
      attribution: 'INPE / CBERS-4A'
    });

    this.rasterTileLayer.addTo(this.map);
  }

  /**
   * Clears the current active raster overlay.
   */
  clearRasterOverlay() {
    if (this.rasterTileLayer) {
      this.map.removeLayer(this.rasterTileLayer);
      this.rasterTileLayer = null;
    }
  }
}
