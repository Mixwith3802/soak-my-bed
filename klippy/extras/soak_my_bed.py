# Soak My Bed - Klipper Plugin for Thermal Stability Analysis
# 
# Copyright (C) 2024-2026 Marco Failli
# Released under the MIT License
#
# This plugin automates the heat-soaking process by running continuous 
# bed meshes and logging Z-deformation data to visualize thermal drift.

import time
import math
import os
import sys
import json
import subprocess
from datetime import datetime

class SoakMyBed:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        
        # --- COMMAND REGISTRATION ---
        # User-facing commands for starting and stopping the analysis
        self.gcode.register_command('SOAK_MY_BED', self.cmd_SOAK_MY_BED)
        self.gcode.register_command('ABORT_SOAK', self.cmd_ABORT_SOAK)
        
        # Internal workflow commands (used for state machine transitions)
        self.gcode.register_command('_SOAK_AFTER_FIRST', self.cmd__SOAK_AFTER_FIRST)
        self.gcode.register_command('_SOAK_LOOP_EVAL', self.cmd__SOAK_LOOP_EVAL)
        self.gcode.register_command('_SOAK_LOOP_WAIT', self.cmd__SOAK_LOOP_WAIT)
        
        # --- STATE VARIABLES ---
        self.temp = 0.0
        self.duration_sec = 0.0
        self.heater = ""
        self.sensor_name = ""
        self.mesh_cmd = ""
        self.script_start_time = 0.0
        self.mesh_start_time = 0.0
        self.soak_start_time = None
        self.is_heating = False
        self.is_running = False
        
        # --- DYNAMIC ENVIRONMENT DETECTION ---
        # Automatically detects the home directory (e.g., /home/pi, /home/sovol, /home/biqu)
        # to ensure compatibility across different manufacturers and OS distributions.
        home_dir = os.path.expanduser("~")
        
        # Default file paths assuming a standard Klipper data structure
        default_save_dir = os.path.join(home_dir, "printer_data", "config", "soak_data")
        default_plot_script = os.path.join(home_dir, "soak-my-bed", "scripts", "plotter.py")
        
        # Configuration overrides from [soak_my_bed] section in printer.cfg
        self.save_dir = config.get('save_dir', default_save_dir)
        self.plot_script_path = config.get('plot_script_path', default_plot_script)
        
        # The 'sys.executable' trick: Finds the exact path of the current Python binary 
        # running Klipper (usually within the klippy-env virtual environment).
        # This eliminates the need for hardcoded paths to the Python interpreter.
        self.klipper_python = sys.executable 
        
        # Default mesh command to support various probes (standard vs. high-speed scanning)
        self.default_mesh_cmd = config.get('mesh_command', 'BED_MESH_CALIBRATE')
        
        self.json_path = ""
        
        # Startup notification in the Klipper console for debugging and version tracking
        self.gcode.respond_info(
            f"SoakMyBed v1.0.2 initialized!\n"
            f"Storage: {self.save_dir}\n"
            f"Python Env: {self.klipper_python}"
        )

    def cmd_SOAK_MY_BED(self, gcmd):
        """Entry point for the SOAK_MY_BED command."""
        if self.is_running:
            self.gcode.respond_info("A soak is already in progress. Use ABORT_SOAK to stop.")
            return

        # Fetch parameters from G-code command (with safe defaults)
        self.temp = gcmd.get_float('TEMPERATURE', 60.0)
        self.duration_sec = gcmd.get_float('DURATION', 10.0) * 60.0
        self.heater = gcmd.get('HEATER', 'heater_bed')
        
        # Construct the mesh command (priority: command parameter > config setting > default)
        raw_mesh_cmd = gcmd.get('MESH_COMMAND', self.default_mesh_cmd).strip('"\'')
        
        # Safety check: Force PROFILE=soak if not specified to prevent 
        # overwriting the user's default calibrated mesh.
        if "PROFILE=" not in raw_mesh_cmd.upper():
            self.mesh_cmd = f"{raw_mesh_cmd} PROFILE=soak"
        else:
            self.mesh_cmd = raw_mesh_cmd

        # Determine the correct sensor name for temperature tracking
        if self.heater in ['heater_bed', 'extruder']:
            self.sensor_name = self.heater
        else:
            self.sensor_name = f"heater_generic {self.heater}"

        # Initialize data logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_path = os.path.join(self.save_dir, f"soak_{timestamp}.json")

        try:
            os.makedirs(self.save_dir, exist_ok=True)
            with open(self.json_path, "w") as f:
                json.dump([], f) 
            self.gcode.respond_info(f"Session started. Data logged to: soak_{timestamp}.json")
        except Exception as e:
            self.gcode.respond_info(f"Storage Error: {e}. Check folder permissions.")
            return

        # Initialize timing and state
        self.script_start_time = time.time()
        self.soak_start_time = None
        self.is_heating = True
        self.is_running = True

        # Phase 1: Capture the "Cold" state before heating begins
        self.gcode.respond_info("Phase 1/2: Capturing baseline cold mesh...")
        self.mesh_start_time = time.time()
        self.gcode.run_script_from_command(f"{self.mesh_cmd}\n_SOAK_AFTER_FIRST")

    def cmd_ABORT_SOAK(self, gcmd):
        """Emergency stop command to halt the process and turn off heaters."""
        if not self.is_running:
            return
        
        self.is_running = False
        self.is_heating = False
        self.gcode.respond_info("SOAK ABORTED: Shutting down heater.")
        self.gcode.run_script_from_command(f"SET_HEATER_TEMPERATURE HEATER={self.heater} TARGET=0")

    def cmd__SOAK_AFTER_FIRST(self, gcmd):
        """Callback after the baseline mesh to trigger the heating phase."""
        if not self.is_running: return
        self.gcode.respond_info(f"Phase 2/2: Heating {self.heater} to {self.temp}C...")
        self.gcode.run_script_from_command(
            f"SET_HEATER_TEMPERATURE HEATER={self.heater} TARGET={self.temp}\n_SOAK_LOOP_EVAL"
        )

    def cmd__SOAK_LOOP_EVAL(self, gcmd):
        """The core logic engine. Decides if we are still heating or in the soaking phase."""
        if not self.is_running: return
        
        try:
            # Query the current temperature of the specified heater/sensor
            sensor_obj = self.printer.lookup_object(self.sensor_name)
            status = sensor_obj.get_status(self.printer.get_reactor().monotonic())
            current_temp = status.get('temperature', 0.0)
        except: 
            self.gcode.respond_info(f"Critical Error: Sensor '{self.sensor_name}' not found.")
            self.is_running = False
            return

        # State transition: Heating -> Soaking
        if self.is_heating:
            if current_temp >= (self.temp - 0.5): # Use a small epsilon for target detection
                self.is_heating = False
                self.soak_start_time = time.time()
                self.gcode.respond_info(f"Target temperature reached. Starting {int(self.duration_sec/60.0)} min timer.")
        else:
            # Check if the soak duration has elapsed
            elapsed = time.time() - self.soak_start_time
            if elapsed >= self.duration_sec:
                self.is_running = False
                self.gcode.respond_info("SOAK COMPLETE: Generating visualization...")
                self.run_plotter()
                self.gcode.run_script_from_command(f"SET_HEATER_TEMPERATURE HEATER={self.heater} TARGET=0")
                return 
            self.gcode.respond_info(f"Stabilizing... {int(self.duration_sec - elapsed)}s remaining.")

        # Trigger the next measurement cycle
        self.mesh_start_time = time.time()
        self.gcode.run_script_from_command(f"{self.mesh_cmd}\n_SOAK_LOOP_WAIT")

    def run_plotter(self):
        """Launches the plotting script in the background using the Klipper Python environment."""
        try:
            subprocess.Popen([self.klipper_python, self.plot_script_path, self.json_path])
        except Exception as e:
            self.gcode.respond_info(f"Plotting Error: {e}. Check if dependencies are installed.")

    def cmd__SOAK_LOOP_WAIT(self, gcmd):
        """Extracts mesh data from Klipper's state and calculates smart wait intervals."""
        if not self.is_running: return
        
        reactor = self.printer.get_reactor()
        eventtime = reactor.monotonic()
        
        try:
            bed_mesh = self.printer.lookup_object('bed_mesh', None)
            sensor_obj = self.printer.lookup_object(self.sensor_name)
            current_temp = sensor_obj.get_status(eventtime).get('temperature', 0.0)

            if bed_mesh is not None:
                mesh_status = bed_mesh.get_status(eventtime)
                # Matrix keys can vary depending on Klipper versions/configurations
                matrix = mesh_status.get('probed_matrix') or mesh_status.get('mesh_matrix', [[]])
                mesh_min = mesh_status.get('mesh_min', [0.0, 0.0])
                mesh_max = mesh_status.get('mesh_max', [300.0, 300.0])

                # Persistence: Append current snapshot to JSON log
                with open(self.json_path, "r") as f: data = json.load(f)
                data.append({
                    "time": time.time() - self.script_start_time, 
                    "temp": current_temp, 
                    "matrix": matrix,
                    "mesh_min": mesh_min,
                    "mesh_max": mesh_max
                })
                with open(self.json_path, "w") as f: json.dump(data, f)
        except Exception as e:
            pass

        # SMART TIMING LOGIC:
        # Calculates how long the mesh took and rounds up to the nearest 5-second interval.
        # This ensures consistent spacing between data points in the final graph.
        mesh_duration = time.time() - self.mesh_start_time
        wait_interval = max(1.0, (math.ceil((mesh_duration + 3.0) / 5.0) * 5.0) - mesh_duration)
        
        # Schedule the next evaluation step
        reactor.register_timer(self._trigger_next_eval, eventtime + wait_interval)

    def _trigger_next_eval(self, eventtime):
        if self.is_running:
            self.gcode.run_script_from_command("_SOAK_LOOP_EVAL")
        return self.printer.get_reactor().NEVER

def load_config(config):
    return SoakMyBed(config)
