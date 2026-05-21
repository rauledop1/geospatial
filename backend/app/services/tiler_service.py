import numpy as np
import requests
from rio_tiler.io import Reader
from rio_tiler.models import ImageData
from rio_tiler.colormap import cmap
from app.services.index_service import index_service

class TilerService:
    def get_scene_assets(self, scene_id: str) -> dict:
        """
        Queries the STAC catalog to get the direct S3 paths of the scene assets.
        """
        payload = {"ids": [scene_id]}
        try:
            # We query the SciTekno STAC endpoint which registers AWS CBERS COGs
            response = requests.post("https://stac.scitekno.com.br/v100/search", json=payload, timeout=10)
            if response.status_code == 200:
                features = response.json().get("features", [])
                if features:
                    assets = features[0].get("assets", {})
                    # Return mapping from asset keys (e.g. 'B7', 'B5') to S3 paths
                    return {k: v.get("href") for k, v in assets.items()}
        except Exception as e:
            print(f"Error resolving STAC assets for scene {scene_id}: {e}")
        return {}

    def auto_stretch(self, data: np.ndarray) -> np.ndarray:
        """
        Applies linear percentile contrast stretching (2% to 98%) per band 
        to normalize 16-bit sensor data into visual 8-bit RGB range.
        """
        stretched = np.zeros_like(data, dtype=np.uint8)
        for b in range(data.shape[0]):
            band = data[b]
            p2, p98 = np.percentile(band, (2, 98))
            if p98 <= p2:
                p98 = p2 + 1
            scaled = (band - p2) / (p98 - p2) * 255.0
            stretched[b] = np.clip(scaled, 0, 255).astype(np.uint8)
        return stretched

    def render_tile(self, scene_id: str, index: str, colormap: str, x: int, y: int, z: int) -> bytes:
        """
        Dynamically reads, processes, and renders a PNG tile.
        """
        assets = self.get_scene_assets(scene_id)
        if not assets:
            raise ValueError(f"Scene '{scene_id}' has no accessible assets or could not be found.")

        # Determine band mappings based on sensor suffix in scene_id
        # MUX bands: B5=Blue, B6=Green, B7=Red, B8=NIR
        # WFI bands: B13=Blue, B14=Green, B15=Red, B16=NIR
        # WPM bands: B1=Blue, B2=Green, B3=Red, B4=NIR
        if "MUX" in scene_id:
            b_red, b_green, b_blue, b_nir = "B7", "B6", "B5", "B8"
        elif "WFI" in scene_id:
            b_red, b_green, b_blue, b_nir = "B15", "B14", "B13", "B16"
        elif "WPM" in scene_id:
            b_red, b_green, b_blue, b_nir = "B3", "B2", "B1", "B4"
        else:
            # Fallback guessing
            b_red = "B7" if "B7" in assets else "B3"
            b_green = "B6" if "B6" in assets else "B2"
            b_blue = "B5" if "B5" in assets else "B1"
            b_nir = "B8" if "B8" in assets else "B4"

        if index == "ndvi":
            red_url = assets.get(b_red)
            nir_url = assets.get(b_nir)
            if not red_url or not nir_url:
                raise ValueError(f"Scene is missing Red ({b_red}) or NIR ({b_nir}) bands for NDVI.")

            with Reader(red_url) as red_reader:
                red_tile = red_reader.tile(x, y, z)
            with Reader(nir_url) as nir_reader:
                nir_tile = nir_reader.tile(x, y, z)

            ndvi_data = index_service.calculate_ndvi(red_tile.data[0], nir_tile.data[0])
            # Scale NDVI from [-1, 1] to [0, 255] for colormap mapping
            ndvi_scaled = ((ndvi_data + 1) / 2 * 255).astype(np.uint8)
            ndvi_scaled = np.expand_dims(ndvi_scaled, axis=0)
            
            mask = red_tile.mask & nir_tile.mask
            img = ImageData(ndvi_scaled, mask)
            
            cmap_dict = cmap.get(colormap or "rdylgn")
            return img.render(img_format="PNG", colormap=cmap_dict)

        elif index == "ndwi":
            green_url = assets.get(b_green)
            nir_url = assets.get(b_nir)
            if not green_url or not nir_url:
                raise ValueError(f"Scene is missing Green ({b_green}) or NIR ({b_nir}) bands for NDWI.")

            with Reader(green_url) as green_reader:
                green_tile = green_reader.tile(x, y, z)
            with Reader(nir_url) as nir_reader:
                nir_tile = nir_reader.tile(x, y, z)

            ndwi_data = index_service.calculate_ndwi(green_tile.data[0], nir_tile.data[0])
            ndwi_scaled = ((ndwi_data + 1) / 2 * 255).astype(np.uint8)
            ndwi_scaled = np.expand_dims(ndwi_scaled, axis=0)
            
            mask = green_tile.mask & nir_tile.mask
            img = ImageData(ndwi_scaled, mask)
            
            cmap_dict = cmap.get(colormap or "coolwarm")
            return img.render(img_format="PNG", colormap=cmap_dict)

        else:  # "raw" RGB
            r_url = assets.get(b_red)
            g_url = assets.get(b_green)
            b_url = assets.get(b_blue)

            if not r_url or not g_url or not b_url:
                raise ValueError(f"Scene is missing RGB bands ({b_red}, {b_green}, {b_blue}).")

            with Reader(r_url) as r_reader:
                r_tile = r_reader.tile(x, y, z)
            with Reader(g_url) as g_reader:
                g_tile = g_reader.tile(x, y, z)
            with Reader(b_url) as b_reader:
                b_tile = b_reader.tile(x, y, z)

            # Stack into multi-band numpy array
            rgb_raw = np.stack([r_tile.data[0], g_tile.data[0], b_tile.data[0]])
            rgb_stretched = self.auto_stretch(rgb_raw)
            
            mask = r_tile.mask & g_tile.mask & b_tile.mask
            img = ImageData(rgb_stretched, mask)
            
            return img.render(img_format="PNG")

tiler_service = TilerService()
