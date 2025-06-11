from ansys.aedt.core import Hfss

# Launch HFSS using updated PyAEDT syntax
hfss = Hfss(
    project="MyHFSS_Project",
    design="PatchDesign",
    non_graphical=False,
    new_desktop=True
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
    reference_conductors=["Coax"]
)


# Save project
hfss.save_project()

# Wait for user input before closing HFSS
input("\n✅ HFSS is open. Press Enter to close it...")

# Close and release AEDT
hfss.release_desktop(close_projects=True, close_desktop=True)
print("✅ HFSS closed.")
