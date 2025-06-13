from ansys.aedt.core import Hfss
import os

# Launch HFSS using updated PyAEDT syntax
hfss = Hfss(
    project="MyHFSS_Project",
    design="PatchDesign",
    non_graphical=False,
    new_desktop=True,
    solution_type="DrivenModal"
)

# Create the substrate box
substrate = hfss.modeler.create_box(
    [-50, -45, 0],              # Position
    [100, 90, 3.2],             # Size (x, y, z)
    name="substrate",
    material="Rogers RT/duroid 5870 (tm)"
)

substrate.transparency = 0.2
substrate.color = [143, 175, 175]  # RGB

# Create the ground rectangle
ground = hfss.modeler.create_rectangle(
    orientation="XY",
    origin=[-50, -45],
    sizes=[100, 90],
    name="Ground"
)

ground.color = [0, 255, 128]
ground.transparency = 0.06

# Assign Perfect E boundary condition to the ground
hfss.assign_perfecte_to_sheets(ground.name, "PerfectE1")

# Create circular hole
hole = hfss.modeler.create_circle(
    orientation="XY",
    origin=[-5, 0],
    radius=1.6,
    name="Hole"
)

hole.color = [255, 128, 64]

# Subtract hole from ground
hfss.modeler.subtract("Ground", "Hole")
hfss.modeler.delete("Hole")

# Create the patch rectangle
patch = hfss.modeler.create_rectangle(
    orientation="XY",
    origin=[-20, -15, 3.2],
    sizes=[40, 30],
    name="Patch"
)

patch.color = [255, 0, 0]
patch.transparency = 0.11

# Assign Perfect E boundary condition to the ground
hfss.assign_perfecte_to_sheets(patch.name, "PerfectE2")

# Create the coaxial cable
coax = hfss.modeler.create_cylinder(
    origin=[-5, 0, 0],
    orientation="XY",
    height=-5,
    radius=1.6,
    name="Coax"
)

# create the coaxial cable pin
coax_pin = hfss.modeler.create_cylinder(
    origin=[-5, 0, 0],
    orientation="XY",
    height=-5,
    radius=0.7,
    name="Coax_Pin",
    material="pec"
)

coax_pin.color = [255, 0, 128]

# create the pin going into the substrate
probe = hfss.modeler.create_cylinder(
    origin=[-5, 0, 0],
    orientation="XY",
    height=3.2,
    radius=0.7,
    name="Probe",
    material="pec"
)

probe.color = [255, 0, 128]
probe.transparency = 0.5

# create the radiation box
airbox = hfss.modeler.create_box(
    [-50, -45, 0],             
    [100, 90, 23.2],           
    name="AirBox",
    material="vacuum"
)

airbox.transparency = 0.95
airbox.color = [0, 0, 0]

# Assign radiation boundary to all faces except the bottom (lowest Z-center)
hfss.assign_radiation_boundary_to_faces(
    [f.id for f in airbox.faces if round(f.center[2], 6) > 0],
    name="Rad1"
)

# Create port
port = hfss.modeler.create_circle(
    orientation="XY",
    origin=[-5, 0, -5],
    radius=1.6,
    name="Port"
)

port.color = [255, 128, 255]

# Assign wave port with a simple integration line
hfss.wave_port(
    port.name,
    reference=coax.name,
    name="1"
)

# Create setup
setup = hfss.create_setup("Setup1")
setup.props["Frequency"] = "2.3GHz"
setup.props["MaximumPasses"] = 20
setup.props["DeltaS"] = 0.02
setup.update()

# Now add the sweep
sweep = setup.add_sweep("Sweep")
sweep.props["SweepType"] = "Fast"
sweep.props["RangeType"] = "LinearCount"
sweep.props["RangeStart"] = "2.2GHz"
sweep.props["RangeEnd"] = "2.4GHz"
sweep.props["RangeCount"] = 101
sweep.update()

# Analyze the design
hfss.analyze()

# Create S11 report inside Ansys GUI
hfss.post.create_report(
    expressions=["dB(S(1,1))"],
    primary_sweep_variable="Freq",
    variations={"Freq": ["All"]},
    report_category="S Parameter",
    context="Setup1",
    plot_type="Rectangular Plot",
    # name="S11 Report"
)

# Get solution data from the report
solution_data = hfss.post.get_solution_data(
    expressions=["dB(S(1,1))"],
    primary_sweep_variable="Freq",
    context="Setup1"
)

# Define path to export CSV
csv_path = os.path.join(hfss.working_directory, "S11.csv")

# Export to CSV
solution_data.export_data_to_csv(csv_path)
print(f"S11 data exported to: {csv_path}")

# Wait for user input before closing HFSS
input("\n✅ HFSS is open. Press Enter to close it...")

# Save project
hfss.save_project()

# Close and release AEDT
hfss.release_desktop(close_projects=True, close_desktop=True)
print("✅ HFSS closed.")
