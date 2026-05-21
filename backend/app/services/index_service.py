import numpy as np

class IndexService:
    def calculate_ndvi(self, red: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """
        Calculates NDVI: (NIR - Red) / (NIR + Red)
        Input bands should be float or scaled numeric arrays.
        """
        # Convert to float for calculation
        red = red.astype(np.float32)
        nir = nir.astype(np.float32)
        
        denominator = nir + red
        # Prevent division by zero
        denominator = np.where(denominator == 0, 0.00001, denominator)
        
        ndvi = (nir - red) / denominator
        # Clip index values to standard [-1.0, 1.0] range
        return np.clip(ndvi, -1.0, 1.0)

    def calculate_ndwi(self, green: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """
        Calculates NDWI: (Green - NIR) / (Green + NIR)
        Useful for identifying water bodies.
        """
        green = green.astype(np.float32)
        nir = nir.astype(np.float32)
        
        denominator = green + nir
        denominator = np.where(denominator == 0, 0.00001, denominator)
        
        ndwi = (green - nir) / denominator
        return np.clip(ndwi, -1.0, 1.0)

index_service = IndexService()
