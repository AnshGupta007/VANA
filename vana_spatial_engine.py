"""
VANA Spatial & GIS Engine (vana_spatial_engine.py)
Author: Ansh (Spatial / Visualization Lead & Governance Steward)
Collaborators: Rhugved (Data Lead), Mohit (Integration Lead)

Provides WGS84 (EPSG:4326) GeoJSON vector layers, bounding-box spatial indexing,
and location-based environmental representation for Vana / FIN.
"""

import json
from typing import Any, Dict, List, Optional


class VanaSpatialEngine:
    """
    Spatial GIS Engine for Vana / FIN.
    Manages vector boundaries for Thane Creek Sanctuary, Maharashtra Forest Divisions,
    Mangrove density belts, and Nursery / Ropvatika plots.
    """

    def __init__(self):
        self._init_layers()

    def _init_layers(self):
        # 1. Thane Creek Flamingo Sanctuary Boundary Layer
        self.thane_creek_sanctuary = {
            "type": "Feature",
            "id": "GEO-TCFS-SANCTUARY-BOUNDARY",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [72.960, 19.080],
                        [72.990, 19.080],
                        [73.010, 19.140],
                        [73.000, 19.180],
                        [72.970, 19.180],
                        [72.950, 19.130],
                        [72.960, 19.080]
                    ]
                ]
            },
            "properties": {
                "layer_id": "thane_creek_sanctuary",
                "name": "Thane Creek Flamingo Sanctuary (TCFS)",
                "designation": "Ramsar Site #2490 & Wildlife Sanctuary",
                "state": "Maharashtra",
                "district": "Mumbai Suburban / Thane",
                "gazetted_area_sqkm": 16.90,
                "mangrove_cover_sqkm": 8.96,
                "dominant_species": "Avicennia marina / Rhizophora mucronata",
                "center_lat": 19.130,
                "center_lon": 72.980,
                "stroke_color": "#059669",
                "fill_color": "#10b981",
                "fill_opacity": 0.25,
                "source": "Maharashtra Forest Department Mangrove Cell (2020)"
            }
        }

        # 2. Mangrove Density Zones in Thane Creek
        self.mangrove_density_zones = {
            "type": "FeatureCollection",
            "properties": {
                "layer_id": "mangrove_density_zones",
                "title": "Thane Creek Mangrove Density Strata (FSI & Ground Truthed)"
            },
            "features": [
                {
                    "type": "Feature",
                    "id": "ZONE-AIROLI-MDF",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [72.985, 19.140],
                                [73.005, 19.140],
                                [73.008, 19.165],
                                [72.988, 19.165],
                                [72.985, 19.140]
                            ]
                        ]
                    },
                    "properties": {
                        "zone_name": "Airoli Core Mangrove Belt",
                        "density_class": "MODERATELY_DENSE_MANGROVE",
                        "canopy_density_pct": "40% - 70%",
                        "species": "Avicennia marina",
                        "measured_agb_mgha": 84.83,
                        "soil_carbon_mgha": 280.0,
                        "color": "#047857"
                    }
                },
                {
                    "type": "Feature",
                    "id": "ZONE-VIKHROLI-OF",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [72.935, 19.090],
                                [72.955, 19.090],
                                [72.958, 19.115],
                                [72.938, 19.115],
                                [72.935, 19.090]
                            ]
                        ]
                    },
                    "properties": {
                        "zone_name": "Vikhroli Tidal Mudflat Fringe",
                        "density_class": "OPEN_MANGROVE",
                        "canopy_density_pct": "10% - 40%",
                        "species": "Avicennia marina / Acanthus ilicifolius",
                        "measured_agb_mgha": 62.40,
                        "soil_carbon_mgha": 245.0,
                        "color": "#34d399"
                    }
                },
                {
                    "type": "Feature",
                    "id": "ZONE-BHANDUP-BUFFER",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [72.960, 19.120],
                                [72.980, 19.120],
                                [72.982, 19.140],
                                [72.962, 19.140],
                                [72.960, 19.120]
                            ]
                        ]
                    },
                    "properties": {
                        "zone_name": "Bhandup Saltpan Restoration Buffer",
                        "density_class": "RESTORATION_BUFFER",
                        "canopy_density_pct": "20% - 50%",
                        "species": "Rhizophora mucronata plantation",
                        "measured_agb_mgha": 48.50,
                        "soil_carbon_mgha": 210.0,
                        "color": "#6ee7b7"
                    }
                }
            ]
        }

        # 3. Maharashtra Forest Regional Divisions
        self.maharashtra_forest_regions = {
            "type": "FeatureCollection",
            "properties": {
                "layer_id": "maharashtra_forest_regions",
                "title": "Maharashtra State Forest Divisions (ISFR 2023)"
            },
            "features": [
                {
                    "type": "Feature",
                    "id": "DIV-WESTERN-GHATS",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [73.20, 15.80],
                                [74.50, 15.80],
                                [74.20, 19.50],
                                [73.50, 19.50],
                                [73.20, 15.80]
                            ]
                        ]
                    },
                    "properties": {
                        "region_name": "Western Ghats Eco-Division (Sahyadri)",
                        "vdf_area_km2": 4210.50,
                        "mdf_area_km2": 6840.20,
                        "of_area_km2": 3210.10,
                        "total_fc_km2": 14260.80,
                        "canopy_type": "Tropical Semi-Evergreen & Moist Deciduous",
                        "color": "#065f46"
                    }
                },
                {
                    "type": "Feature",
                    "id": "DIV-VIDARBHA",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [77.50, 19.50],
                                [80.50, 19.50],
                                [80.50, 21.80],
                                [77.50, 21.80],
                                [77.50, 19.50]
                            ]
                        ]
                    },
                    "properties": {
                        "region_name": "Vidarbha Tiger Landscape (Tadoba / Melghat)",
                        "vdf_area_km2": 3890.10,
                        "mdf_area_km2": 6120.40,
                        "of_area_km2": 4510.30,
                        "total_fc_km2": 14520.80,
                        "canopy_type": "Dry Deciduous Teak Forests",
                        "color": "#047857"
                    }
                },
                {
                    "type": "Feature",
                    "id": "DIV-KONKAN-COASTAL",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [72.80, 15.80],
                                [73.50, 15.80],
                                [73.20, 19.80],
                                [72.70, 19.80],
                                [72.80, 15.80]
                            ]
                        ]
                    },
                    "properties": {
                        "region_name": "Konkan Coastal & Mangrove Belt",
                        "vdf_area_km2": 412.30,
                        "mdf_area_km2": 1420.50,
                        "of_area_km2": 1180.20,
                        "mangrove_km2": 315.09,
                        "total_fc_km2": 3012.80,
                        "canopy_type": "Mangroves, Littoral & Swamp Forests",
                        "color": "#10b981"
                    }
                }
            ]
        }

        # 4. Coastal Nurseries & Ropvatika Plots
        self.nurseries_ropvatika = {
            "type": "FeatureCollection",
            "properties": {
                "layer_id": "nurseries_ropvatika",
                "title": "Maharashtra Social Forestry Mangrove Nurseries"
            },
            "features": [
                {
                    "type": "Feature",
                    "id": "ROPVATIKA-AIROLI",
                    "geometry": {"type": "Point", "coordinates": [72.9980, 19.1550]},
                    "properties": {
                        "site_name": "Airoli Coastal Marine Nursery",
                        "nursery_type": "MANGROVE_SEEDLING_BANK",
                        "stock_count": 45000,
                        "species_primary": "Avicennia marina",
                        "elevation_m": 4.5,
                        "irrigation": "Tidal Inundation Tidal Gate",
                        "contact": "Forest Ranger - Marine Cell",
                        "marker_symbol": "sprout"
                    }
                },
                {
                    "type": "Feature",
                    "id": "ROPVATIKA-BHANDUP",
                    "geometry": {"type": "Point", "coordinates": [72.9750, 19.1410]},
                    "properties": {
                        "site_name": "Bhandup Pumping Station Nursery",
                        "nursery_type": "SALT_TOLERANT_AFFORESTATION",
                        "stock_count": 28000,
                        "species_primary": "Rhizophora mucronata",
                        "elevation_m": 3.8,
                        "irrigation": "Estuarine Brackish Channel",
                        "contact": "Forest Ranger - Bhandup Zone",
                        "marker_symbol": "sprout"
                    }
                },
                {
                    "type": "Feature",
                    "id": "ROPVATIKA-VIKHROLI",
                    "geometry": {"type": "Point", "coordinates": [72.9360, 19.0980]},
                    "properties": {
                        "site_name": "Vikhroli Godrej Mangrove Research Nursery",
                        "nursery_type": "RESEARCH_AND_GENE_BANK",
                        "stock_count": 35000,
                        "species_primary": "Avicennia officinalis / Ceriops tagal",
                        "elevation_m": 5.2,
                        "irrigation": "Natural Creek High Tide",
                        "contact": "Vikhroli Wetland Conservation Trust",
                        "marker_symbol": "tree"
                    }
                }
            ]
        }

        # 5. Field Drone Transect Flight Lines
        self.drone_survey_transects = {
            "type": "Feature",
            "id": "TRANSECT-TC-Z03-MISSION-F02",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [72.972, 19.125],
                    [72.980, 19.135],
                    [72.988, 19.145],
                    [72.995, 19.155]
                ]
            },
            "properties": {
                "layer_id": "drone_survey_transects",
                "mission_id": "TC-Z03-F02",
                "sensor": "G3-LIDAR-001 (LiDAR Pod)",
                "altitude_m": 65.0,
                "flight_length_km": 4.2,
                "points_captured": 1284500,
                "data_status": "CHM_DERIVED",
                "stroke_color": "#ef4444"
            }
        }

    def list_layers(self) -> List[Dict[str, Any]]:
        """Returns catalog of all available spatial GIS layers."""
        return [
            {
                "layer_id": "thane_creek_sanctuary",
                "title": "Thane Creek Flamingo Sanctuary Boundary",
                "type": "Polygon",
                "crs": "EPSG:4326",
                "feature_count": 1,
                "category": "PROTECTED_AREA"
            },
            {
                "layer_id": "mangrove_density_zones",
                "title": "Thane Creek Mangrove Density Strata",
                "type": "FeatureCollection",
                "crs": "EPSG:4326",
                "feature_count": len(self.mangrove_density_zones["features"]),
                "category": "VEGETATION_STRATA"
            },
            {
                "layer_id": "maharashtra_forest_regions",
                "title": "Maharashtra Forest Divisions (ISFR 2023)",
                "type": "FeatureCollection",
                "crs": "EPSG:4326",
                "feature_count": len(self.maharashtra_forest_regions["features"]),
                "category": "STATUTORY_BOUNDARY"
            },
            {
                "layer_id": "nurseries_ropvatika",
                "title": "Coastal Mangrove Nurseries & Ropvatika Plots",
                "type": "FeatureCollection",
                "crs": "EPSG:4326",
                "feature_count": len(self.nurseries_ropvatika["features"]),
                "category": "AFFORESTATION_PLOTS"
            },
            {
                "layer_id": "drone_survey_transects",
                "title": "Drone LiDAR Survey Transects (Mission F02)",
                "type": "LineString",
                "crs": "EPSG:4326",
                "feature_count": 1,
                "category": "FIELD_MISSION_TRACK"
            }
        ]

    def get_layer(self, layer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves exact GeoJSON for a specified layer."""
        layers = {
            "thane_creek_sanctuary": self.thane_creek_sanctuary,
            "mangrove_density_zones": self.mangrove_density_zones,
            "maharashtra_forest_regions": self.maharashtra_forest_regions,
            "nurseries_ropvatika": self.nurseries_ropvatika,
            "drone_survey_transects": self.drone_survey_transects
        }
        return layers.get(layer_id)

    def get_unified_spatial_envelope(self) -> Dict[str, Any]:
        """Returns unified FeatureCollection of all layers for full map visualization."""
        features = [self.thane_creek_sanctuary]
        features.extend(self.mangrove_density_zones["features"])
        features.extend(self.maharashtra_forest_regions["features"])
        features.extend(self.nurseries_ropvatika["features"])
        features.append(self.drone_survey_transects)
        return {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "features": features
        }


if __name__ == "__main__":
    engine = VanaSpatialEngine()
    print("VANA Spatial GIS Engine Initialized.")
    print(f"Catalog Layers: {len(engine.list_layers())}")
    for layer in engine.list_layers():
        print(f" - {layer['layer_id']}: {layer['title']} ({layer['type']})")
    
    # Test boundary validation
    sanctuary = engine.get_layer("thane_creek_sanctuary")
    coords = sanctuary["geometry"]["coordinates"][0]
    assert coords[0] == coords[-1], "Polygon topological closure check failed!"
    print("Topological Polygon Closure Check: PASSED")
