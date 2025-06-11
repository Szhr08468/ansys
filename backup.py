from ansys.aedt.core import Hfss

# Launch HFSS using updated PyAEDT syntax
hfss = Hfss(
    project="MyHFSS_Project",
    design="PatchDesign",
    non_graphical=False,
    new_desktop=True
)

# Create a copper box
box = hfss.modeler.create_box([0, 0, 0], [10, 20, 1], name="MyBox", material="copper")

# Customize box appearance
box.color = "Green"
box.transparency = 0.6

# Save project
hfss.save_project()

# Wait for user input before closing HFSS
input("\n✅ HFSS is open. Press Enter to close it...")

# Close and release AEDT
hfss.release_desktop(close_projects=True, close_desktop=True)
print("✅ HFSS closed.")
