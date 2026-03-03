"""Tests for configuration orientation support."""

import json
import os
import pytest
import tempfile

from src.config import AppConfig, AppSettings, WeatherStation, load_config, save_config


class TestOrientationConfig:
    """Tests for orientation configuration support."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data with orientation."""
        return {
            "version": 1,
            "stations": [
                {
                    "id": "home",
                    "name": "Home",
                    "latitude": 39.7456,
                    "longitude": -97.0892
                }
            ],
            "settings": {
                "refresh_interval_minutes": 15,
                "cycle_interval_seconds": 30,
                "temperature_unit": "F",
                "display_brightness": 100,
                "orientation": "portrait"
            }
        }


class TestPortraitConfig:
    """Tests for portrait orientation configuration (User Story 1)."""
    
    def test_portrait_config_parsing(self, temp_config_dir, sample_config_data):
        """Test that portrait orientation is correctly parsed from config."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        sample_config_data["settings"]["orientation"] = "portrait"
        
        with open(config_path, "w") as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_path)
        assert config.settings.orientation == "portrait"
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data."""
        return {
            "version": 1,
            "stations": [
                {
                    "id": "home",
                    "name": "Home",
                    "latitude": 39.7456,
                    "longitude": -97.0892
                }
            ],
            "settings": {
                "refresh_interval_minutes": 15,
                "cycle_interval_seconds": 30,
                "temperature_unit": "F",
                "display_brightness": 100
            }
        }


class TestLandscapeConfig:
    """Tests for landscape orientation configuration (User Story 2)."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data."""
        return {
            "version": 1,
            "stations": [
                {
                    "id": "home",
                    "name": "Home",
                    "latitude": 39.7456,
                    "longitude": -97.0892
                }
            ],
            "settings": {
                "refresh_interval_minutes": 15,
                "cycle_interval_seconds": 30,
                "temperature_unit": "F",
                "display_brightness": 100
            }
        }
    
    def test_landscape_config_parsing(self, temp_config_dir, sample_config_data):
        """Test that landscape orientation is correctly parsed from config."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        sample_config_data["settings"]["orientation"] = "landscape"
        
        with open(config_path, "w") as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_path)
        assert config.settings.orientation == "landscape"


class TestDefaultOrientation:
    """Tests for default orientation behavior (User Story 3)."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data without orientation."""
        return {
            "version": 1,
            "stations": [
                {
                    "id": "home",
                    "name": "Home",
                    "latitude": 39.7456,
                    "longitude": -97.0892
                }
            ],
            "settings": {
                "refresh_interval_minutes": 15,
                "cycle_interval_seconds": 30,
                "temperature_unit": "F",
                "display_brightness": 100
            }
        }
    
    def test_default_orientation_when_not_specified(self, temp_config_dir, sample_config_data):
        """Test that orientation defaults to 'portrait' when not specified."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        # Ensure orientation is NOT in config
        if "orientation" in sample_config_data["settings"]:
            del sample_config_data["settings"]["orientation"]
        
        with open(config_path, "w") as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_path)
        assert config.settings.orientation == "portrait"
    
    def test_invalid_orientation_fallback(self, temp_config_dir, sample_config_data):
        """Test that invalid orientation falls back to 'portrait' with warning."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        sample_config_data["settings"]["orientation"] = "invalid_value"
        
        with open(config_path, "w") as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_path)
        assert config.settings.orientation == "portrait"
    
    def test_case_insensitive_orientation(self, temp_config_dir, sample_config_data):
        """Test that orientation comparison is case-insensitive."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        sample_config_data["settings"]["orientation"] = "LANDSCAPE"
        
        with open(config_path, "w") as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_path)
        assert config.settings.orientation == "landscape"


class TestSaveConfigOrientation:
    """Tests for saving orientation to config file."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_save_config_includes_orientation(self, temp_config_dir):
        """Test that save_config includes orientation field."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        
        config = AppConfig(
            version=1,
            stations=[
                WeatherStation(
                    id="home",
                    name="Home",
                    latitude=39.7456,
                    longitude=-97.0892
                )
            ],
            settings=AppSettings(orientation="landscape")
        )
        
        save_config(config, config_path)
        
        with open(config_path, "r") as f:
            saved_data = json.load(f)
        
        assert saved_data["settings"]["orientation"] == "landscape"


class TestDisplayRotationConfig:
    """Tests for display_rotation configuration setting."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data with display_rotation."""
        return {
            "version": 1,
            "stations": [
                {
                    "id": "home",
                    "name": "Home",
                    "latitude": 39.7456,
                    "longitude": -97.0892
                }
            ],
            "settings": {
                "refresh_interval_minutes": 15,
                "cycle_interval_seconds": 30,
                "temperature_unit": "F",
                "display_brightness": 100,
                "orientation": "landscape"
            }
        }
    
    def test_display_rotation_parsing(self, temp_config_dir, sample_config_data):
        """Test that display_rotation is correctly parsed from config."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        sample_config_data["settings"]["display_rotation"] = 180
        
        with open(config_path, "w") as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_path)
        assert config.settings.display_rotation == 180
    
    def test_display_rotation_all_valid_values(self, temp_config_dir, sample_config_data):
        """Test that all valid rotation values (0, 90, 180, 270) are accepted."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        
        for rotation in [0, 90, 180, 270]:
            sample_config_data["settings"]["display_rotation"] = rotation
            
            with open(config_path, "w") as f:
                json.dump(sample_config_data, f)
            
            config = load_config(config_path)
            assert config.settings.display_rotation == rotation
    
    def test_display_rotation_default_value(self, temp_config_dir, sample_config_data):
        """Test that display_rotation defaults to 0 when not specified."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        # Ensure display_rotation is NOT in config
        if "display_rotation" in sample_config_data["settings"]:
            del sample_config_data["settings"]["display_rotation"]
        
        with open(config_path, "w") as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_path)
        assert config.settings.display_rotation == 0
    
    def test_display_rotation_invalid_value_fallback(self, temp_config_dir, sample_config_data):
        """Test that invalid display_rotation falls back to 0 with warning."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        sample_config_data["settings"]["display_rotation"] = 45  # Invalid value
        
        with open(config_path, "w") as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_path)
        assert config.settings.display_rotation == 0
    
    def test_save_config_includes_display_rotation(self, temp_config_dir):
        """Test that save_config includes display_rotation field."""
        config_path = os.path.join(temp_config_dir, "stations.json")
        
        config = AppConfig(
            version=1,
            stations=[
                WeatherStation(
                    id="home",
                    name="Home",
                    latitude=39.7456,
                    longitude=-97.0892
                )
            ],
            settings=AppSettings(orientation="landscape", display_rotation=180)
        )
        
        save_config(config, config_path)
        
        with open(config_path, "r") as f:
            saved_data = json.load(f)
        
        assert saved_data["settings"]["display_rotation"] == 180
