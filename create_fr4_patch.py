from ansys.aedt.core import Hfss
import os
import math

# Launch HFSS using updated PyAEDT syntax
hfss = Hfss(
    project="MyHFSS_Project_SinglePatch",
    design="FR4PatchDesign",
    non_graphical=False,
    new_desktop=True,
    solution_type="Modal"
)

# Specify the material name (must exist in your material library)
material_name = "FR4_epoxy"
mat_obj = hfss.materials.exists_material(material_name)

# Check if material exists
if mat_obj:
    material = hfss.materials[material_name]
    
    # Extract relevant properties
    eps_r = material.permittivity.value                  # Dielectric constant
    tan_d = material.dielectric_loss_tangent.value       # Loss tangent
    mu_r = material.permeability.value                   # Magnetic permeability
    sigma = material.conductivity.value                  # Conductivity (for conductors)

    # Assign other important variables
    f0 = 1.575e9   # Center frequency in GHz
    h = 1.6        # meters # Substrate thickness in millimeters

    print("\n================ Antenna Substrate and Design Parameters ================\n")
    print(f"Center Design Frequency: {f0 / 1e9} GHz")
    print(f"Substrate Material: {material_name}")
    print(f"  Substrate Thickness (h): {h} mm")
    print(f"  Relative Permittivity (εr): {eps_r}")
    print(f"  Loss Tangent (tanδ): {tan_d}")
    print(f"  Relative Permeability (μr): {mu_r}")
    print(f"  Conductivity (σ): {sigma}")
    print("\n=========================================================================\n")
else:
    print(f"Material {material_name} not found in the material library.")


# Constants
c = 3e11  # Speed of light in mm/s (converted to mm/s from m/s)
eps_r = float(material.permittivity.value)                  # Dielectric constant

# Patch Width (W)
W = (c / (2 * f0)) * (math.sqrt(2 / (eps_r + 1))) 

# Effective dielectric constant (εeff)
eps_eff = ((eps_r + 1) / 2) + ( ((eps_r - 1) / 2) * ((1 + (12 * h / W)) ** -0.5) )

# Effective Length (Leff)
Leff = c / (2 * f0 * math.sqrt(eps_eff))

# Length extension due to fringing (ΔL)
delta_L = (0.412 * h) * (((eps_eff + 0.3) * ((W / h) + 0.264)) / ((eps_eff - 0.258) * ((W / h) + 0.8)))

# Actual Patch Length (L)
L = (Leff - 2 * delta_L)

# Substrate size (based on patch size plus 6 times the substrate thickness)
W_sub = W + 6 * h
L_sub = L + 6 * h

# Corner truncation (for RHCP)
truncation = round(L * (math.sqrt((4 * f0 * h) / (2 * c * math.sqrt(eps_r)))), 2)

# Feed point location (for coax-fed)
xf = round(W / 2, 3)
# Estimate y-offset using approximate equation
yf = round(L / (2 * math.sqrt(eps_eff)), 3)

W = round(W, 3)
L = round(L, 3)
W_sub = round(W_sub, 3)
L_sub = round(L_sub, 3)

W_half = round(W / 2, 3)
L_half = round(L / 2, 3)
W_sub_half = round(W_sub / 2, 3)
L_sub_half = round(L_sub / 2, 3)

xf_from_origin = round(xf - W_half, 3)   
yf_from_origin = round(yf - L_half, 3)

# Output
print("\n================== Computed Patch Antenna Parameters ==================\n")
print(f"Patch Width (W): {W} mm")
print(f"Patch Length (L): {L} mm")
print(f"Substrate Width (W_sub): {W_sub} mm")
print(f"Substrate Length (L_sub): {L_sub} mm")
print(f"Feed Point wrt Origin (x, y): ({xf_from_origin} mm, {yf_from_origin} mm)")
print(f"Corner Truncation Size: {truncation} mm")
print(f"Effective Dielectric Constant (εeff): {eps_eff:.2f}")
print("\n=======================================================================\n")

# Create the substrate box
substrate = hfss.modeler.create_box(
    [(-1*(W_sub_half)), (-1*(L_sub_half)), 0],              # Position
    [W_sub, L_sub, h],                                # Size (x, y, z)
    name="Substrate",
    material=material_name
)

substrate.transparency = 0.4
substrate.color = [143, 175, 175]  # RGB

# Create the ground rectangle
ground = hfss.modeler.create_rectangle(
    orientation="XY",
    origin=[(-1*(W_sub_half)), (-1*(L_sub_half))],
    sizes=[W_sub, L_sub],
    name="Ground"
)

ground.color = [0, 255, 128]
ground.transparency = 0.06

# Assign Perfect E boundary condition to the ground
hfss.assign_perfecte_to_sheets(ground.name, "PerfectE1")

# Create circular hole
hole = hfss.modeler.create_circle(
    orientation="XY",
    origin=[xf_from_origin, yf_from_origin],
    radius=1.6,
    name="Hole"
)

hole.color = [255, 128, 64]

# Subtract hole from ground
hfss.modeler.subtract("Ground", "Hole", keep_originals=False)

# Create the patch rectangle
patch = hfss.modeler.create_rectangle(
    orientation="XY",
    origin=[-1*(W_half), -1*(L_half), h],
    sizes=[W, L],
    name="Patch"
)

patch.color = [255, 0, 0]
patch.transparency = 0.11

# Assign Perfect E boundary condition to the patch
hfss.assign_perfecte_to_sheets(patch.name, "PerfectE2")


# --- Top-Left Corner (XY) ---
tl_base = [-W_half, L_half, h]  # corner point
tl_pt2 = [round(-W_half + truncation, 3), L_half, h]  # right
tl_pt3 = [-W_half, round(L_half - truncation, 3), h]  # down

trunc_tl = hfss.modeler.create_polyline(
    [tl_base, tl_pt2, tl_pt3, tl_base],
    cover_surface=True,
    name="TruncTopLeft"
)

# --- Bottom-Right Corner (XY) ---
br_base = [W_half, -L_half, h]  # corner point
br_pt2 = [round(W_half - truncation, 3), -L_half, h]  # left
br_pt3 = [W_half, round(-L_half + truncation, 3), h]  # up

trunc_br = hfss.modeler.create_polyline(
    [br_base, br_pt2, br_pt3, br_base],
    cover_surface=True,
    name="TruncBottomRight"
)

# --- Subtract triangular cuts from the patch ---
hfss.modeler.subtract("Patch", ["TruncTopLeft", "TruncBottomRight"], keep_originals=False)

# Create the coaxial cable
coax = hfss.modeler.create_cylinder(
    origin=[xf_from_origin, yf_from_origin, 0],
    orientation="XY",
    height=-1.6,
    radius=1.6,
    name="Coax",
    material="glass_PTFEreinf"
)

# create the coaxial cable pin
coax_pin = hfss.modeler.create_cylinder(
    origin=[xf_from_origin, yf_from_origin, 0],
    orientation="XY",
    height=-1.6,
    radius=0.8,
    name="Coax_Pin",
    material="pec"
)

coax_pin.color = [255, 0, 128]

# create the pin going into the substrate
probe = hfss.modeler.create_cylinder(
    origin=[xf_from_origin, yf_from_origin, 0],
    orientation="XY",
    height=h,
    radius=0.8,
    name="Probe",
    material="pec"
)

probe.color = [255, 0, 128]
probe.transparency = 0.5

# create the radiation box
airbox = hfss.modeler.create_box(
    [(-1*(W_sub_half)), (-1*(L_sub_half)), 0],
    [W_sub, L_sub, 10],           
    name="AirBox",
    material="air"
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
    origin=[xf_from_origin, yf_from_origin, -1.6],
    radius=1.6,
    name="Port"
)

port.color = [255, 128, 255]

# Assign wave port with a simple integration line
hfss.wave_port(
    port.name,
    reference=coax.name,
    name="1",
    renormalize=False
)

# Create setup
setup = hfss.create_setup("Setup1")
setup.props["Frequency"] = "1.575GHz"
setup.props["MaximumPasses"] = 20
setup.props["DeltaS"] = 0.02
setup.update()

# Now add the sweep
sweep = setup.add_sweep(
    name="Sweep",
    sweep_type="Fast",
    RangeType="LinearCount",
    RangeStart="1.5GHz",
    RangeEnd="1.6GHz",
    RangeCount=2001
    # SaveFields=True,
    # SaveRadFields=False
)
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
print(f"✅ CSV saved to: {csv_path}")

# Define path for TXT file in same directory
txt_path = os.path.join(hfss.working_directory, "params.txt")

# Save the TXT file
try:
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Frequency (GHz): {f0 / 1e9:.3f}\n")
        f.write(f"Substrate thickness (h): {h} mm\n")
        f.write(f"Relative Permittivity (εr): {eps_r}\n")
        f.write(f"Patch Width (W): {W} mm\n")
        f.write(f"Patch Length (L): {L} mm\n")
        f.write(f"Substrate Width (W_sub): {W_sub} mm\n")
        f.write(f"Substrate Length (L_sub): {L_sub} mm\n")
        f.write(f"Feed Point wrt Origin (x, y): ({xf_from_origin}, {yf_from_origin}) mm\n")
        f.write(f"Corner Truncation Size: {truncation} mm\n")
        f.write(f"Effective Dielectric Constant (εeff): {eps_eff:.3f}\n")
        f.write(f"Material: {material_name}\n")
        f.write(f"Loss Tangent: {tan_d}\n")
        f.write(f"Relative Permeability (μr): {mu_r}\n")
        f.write(f"Conductivity (σ): {sigma}\n")
    print(f"✅ TXT saved to: {txt_path}")
except Exception as e:
    print(f"❌ Failed to write TXT file: {e}")



# Wait for user input before closing HFSS
input("\n✅ HFSS is open. Press Enter to close it...")

# Save project
hfss.save_project()

# Close and release AEDT
hfss.release_desktop(close_projects=True, close_desktop=True)
print("✅ HFSS closed.")
