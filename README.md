# 🛏️ soak-my-bed - Stable bed meshes on every print

[![Download soak-my-bed](https://img.shields.io/badge/Download%20soak--my--bed-Visit%20Releases-blue?style=for-the-badge)](https://github.com/Mixwith3802/soak-my-bed/releases)

## 🧭 What this does

soak-my-bed is a Klipper plugin that helps you check how your bed and frame change shape as they heat up. It runs bed mesh checks after the printer has had time to soak at temperature, then turns the results into clear 3D stability animations.

This helps you:

- See how the bed changes as it warms up
- Compare mesh results over time
- Catch movement in the frame or bed before a print starts
- Keep first layers more consistent
- Save time on repeated bed mesh checks

## 💻 What you need

Before you install it, make sure you have:

- A Windows PC
- A working Klipper setup
- Access to your printer host through a browser
- A browser such as Chrome, Edge, or Firefox
- Enough free space to save mesh data and animation files

This tool works with printers that already use Klipper macros and bed mesh calibration.

## 📥 Download

Visit this page to download the latest release for Windows and support files:

[![Download soak-my-bed](https://img.shields.io/badge/Get%20the%20Latest%20Release-Visit%20Releases-grey?style=for-the-badge)](https://github.com/Mixwith3802/soak-my-bed/releases)

Open the releases page, then download the file that matches the release notes. If the release includes a Windows package or archive, save it to your computer first.

## 🪟 Install on Windows

Follow these steps:

1. Open the release page in your browser.
2. Download the latest release file.
3. Save the file to a folder you can find again, such as Downloads or Desktop.
4. If the file is a ZIP archive, right-click it and choose Extract All.
5. Open the extracted folder.
6. Read any included README or setup file.
7. Copy the plugin files into the Klipper or host folder named in the release notes.
8. Restart the Klipper host software if the package asks for it.
9. Open your printer interface in the browser and check that soak-my-bed appears where the plugin is listed.

If the release uses an installer, run the installer and follow the on-screen prompts. If it uses a simple folder install, copy the files into the required location and restart the service.

## 🔧 Set up the plugin

After install, you need to connect it to your printer config.

Use the plugin with these common parts:

- Bed mesh calibration
- Klipper macros
- Printer heat soak steps
- Temperature targets for bed and frame checks

Typical setup flow:

1. Open your Klipper config files.
2. Add the plugin settings shown in the release notes.
3. Set your bed temperature target.
4. Set your soak time.
5. Set how many mesh points you want to sample.
6. Save the changes.
7. Restart Klipper.
8. Run a test mesh to check that the plugin can read your printer data.

If your release includes sample macros, start with those first. They are usually set up for common printer workflows and are easier to adjust.

## 🖥️ How to use it

Once installed, use soak-my-bed in your regular print prep flow:

1. Heat the bed to your target temperature.
2. Let the bed soak for the set time.
3. Run the mesh check.
4. Repeat the process if you want a time-based comparison.
5. Open the results view to review the mesh and animation.

You can use the output to see:

- High and low spots on the bed
- Shape changes caused by heat
- Frame movement during soak
- How stable the bed stays across repeated runs

This helps you decide if the printer is ready for a print or if it needs more time at temperature.

## 🎛️ Features

- Heat soak bed mesh automation
- 3D thermal deformation view
- Stability animation output
- Repeated mesh capture for comparison
- Klipper macro support
- Easy review in a browser
- Clear view of bed and frame movement
- Built for 3D printing workflows

## 📊 What the animation shows

The 3D animation shows how the bed surface changes while the printer heats up. It can help you spot:

- Bowing in the center
- Raised corners
- Tilt across the bed
- Changes from cold to hot
- Movement that comes from the frame, not the bed alone

Use it as a visual check before you start a print that needs good first-layer control.

## 🧰 Basic workflow example

A simple session might look like this:

1. Start with a cold printer.
2. Heat the bed to 60°C.
3. Wait for the soak timer to finish.
4. Run a mesh scan.
5. Let the bed rest.
6. Run another scan at the same temperature.
7. Compare the results in the animation view.

This gives you a better picture of how your printer behaves when it is close to real print conditions.

## 🗂️ Files and output

The plugin may create or use these items:

- Mesh data files
- Heat soak logs
- Comparison charts
- 3D animation files
- Config entries for saved profiles

Keep these files in a folder you can find later. They are useful when you want to compare different bed temperatures or print surfaces.

## 🛠️ Troubleshooting

If the plugin does not work right away, check these items:

- Make sure Klipper is running
- Make sure your printer host is online
- Check that the plugin files are in the right folder
- Confirm that your macro names match the config
- Make sure the bed target temperature is set
- Restart the host after each config change
- Try a simple mesh run before using a full soak sequence

If the browser does not show the plugin, refresh the page and restart the host service.

If the mesh data looks wrong, check your probe settings and bed mesh config. Small setup errors can change the result.

## 🔍 Common questions

### Can I use this with any Klipper printer?

You can use it with a printer that already runs Klipper and supports bed mesh calibration.

### Do I need coding knowledge?

No. You only need to download the release, copy the files, and follow the setup steps.

### Does it work only on Windows?

The main setup guide here is for Windows users. If you run your Klipper host on another system, the same plugin logic still follows the Klipper config and macro setup.

### Why heat soak first?

A cold bed can look different from a hot bed. Heat soak gives the printer time to settle, so the mesh reflects real print conditions.

### What is the main benefit?

It helps you see thermal movement before a print starts, so you can tune your bed mesh with more confidence.

## 🧩 Release notes to check

When you visit the releases page, look for:

- Latest version number
- Windows package or archive
- Setup file or included instructions
- Macro examples
- Config changes
- Any sample output files

Use the newest stable release unless the release notes tell you to use a specific version for your printer setup.

## 🧪 Best results

For a cleaner bed analysis:

- Use the same bed temperature each time
- Wait for the full soak time
- Keep the room temperature steady
- Use the same probe settings
- Run tests on a level table
- Compare scans from the same print surface

These habits make the mesh results easier to read.

## 📚 Related topics

- 3D printing
- Bed mesh calibration
- Klipper
- Klipper macros
- Thermal analysis