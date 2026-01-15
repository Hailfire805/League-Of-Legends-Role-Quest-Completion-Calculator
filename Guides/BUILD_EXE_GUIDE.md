# Creating Standalone .EXE Files

## Why Build an EXE?

**Advantages:**
- ✅ Users don't need Python installed
- ✅ Single file distribution (easier to share)
- ✅ More professional appearance
- ✅ Simpler installation (just run the .exe)

**Disadvantages:**
- ⚠️ Larger file size (~50-100 MB vs. ~200 KB for Python scripts)
- ⚠️ Windows-only (for .exe files)
- ⚠️ Takes time to build
- ⚠️ Antivirus might flag it initially (false positive)

## Quick Start

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Run the Build Script
```bash
python build_exe.py
```

This will:
- Build `LoL_Quest_Calculator.exe` (launcher with all calculators)
- Optionally build individual calculator .exe files
- Clean up temporary build files
- Put the final .exe in the `dist/` folder

### Step 3: Test the EXE
```bash
cd dist
LoL_Quest_Calculator.exe
```

### Step 4: Distribute
Just share the .exe file! No Python or dependencies needed.

---

## Manual Building (Advanced)

If you want more control over the build process:

### Build Single Launcher EXE (Recommended)
```bash
pyinstaller --onefile --console --name LoL_Quest_Calculator launcher.py
```

### Build Individual Calculator EXEs
```bash
# Top Lane
pyinstaller --onefile --windowed --name LoL_Quest_Calculator_Top quest_timer_calculator_top.py

# Mid Lane
pyinstaller --onefile --windowed --name LoL_Quest_Calculator_Mid quest_timer_calculator.py

# Bot Lane
pyinstaller --onefile --windowed --name LoL_Quest_Calculator_Bot quest_timer_calculator_bot.py
```

### Build Options Explained
- `--onefile` - Creates single .exe instead of folder with dependencies
- `--windowed` - No console window (for GUI apps)
- `--console` - Show console window (for launcher menu)
- `--name` - Name of the output .exe
- `--icon` - Add custom icon (use .ico file)
- `--clean` - Clean build cache before building

---

## Adding a Custom Icon (Optional)

1. Create or download a .ico file (32x32 or 64x64 pixels)
2. Name it `icon.ico` and place it in the same folder
3. Build with icon:
   ```bash
   pyinstaller --onefile --console --icon=icon.ico --name LoL_Quest_Calculator launcher.py
   ```

---

## File Sizes

Approximate sizes for built executables:

- **Launcher EXE**: ~50-70 MB (includes all calculators)
- **Individual Calculator EXE**: ~40-50 MB each
- **Total for all 4 EXEs**: ~180-220 MB

The large size is because each .exe bundles Python and all libraries (matplotlib, numpy, tkinter).

**Recommendation:** Build only the launcher .exe, not the individual ones.

---

## Distribution Package

When distributing .exe files, include:

```
dist/
  LoL_Quest_Calculator.exe  (Main executable)
README.md                    (User guide)
```

Users just need:
1. Download the .exe
2. Double-click to run
3. Done!

No Python, no pip install, no command line needed.

---

## Troubleshooting

### "Windows protected your PC" Warning
This is normal for unsigned .exe files. Users can click "More info" → "Run anyway"

To avoid this warning:
- Sign the .exe with a code signing certificate (costs money)
- Build reputation over time (users trust the file after downloads)
- Distribute through known platforms (GitHub releases)

### Antivirus False Positives
Some antivirus software flags PyInstaller .exe files as suspicious.

Solutions:
- Submit the .exe to antivirus companies for whitelisting
- Use VirusTotal to scan and share the results
- Provide the Python source code as an alternative

### Build Fails with Import Errors
If PyInstaller misses some imports, add them manually:
```bash
pyinstaller --onefile --hidden-import=matplotlib --hidden-import=numpy launcher.py
```

### EXE is Too Large
The large size is unavoidable with PyInstaller's `--onefile` mode.

Alternatives:
- Use `--onedir` instead (creates folder with dependencies, smaller main .exe)
- Use Nuitka (compiles Python to C, smaller but more complex)
- Stick with Python scripts (smallest, but requires Python)

---

## macOS/Linux Executables

For macOS:
```bash
pyinstaller --onefile --windowed --name LoL_Quest_Calculator launcher.py
```
Creates: `LoL_Quest_Calculator` (Unix executable)

For Linux:
```bash
pyinstaller --onefile --console --name LoL_Quest_Calculator launcher.py
```
Creates: `LoL_Quest_Calculator` (ELF executable)

**Note:** You must build on the target platform (build Windows .exe on Windows, macOS app on macOS, etc.)

---

## Recommended Distribution Strategy

**For General Audience (Non-technical):**
- Build and distribute the .exe
- Simpler, just "download and run"

**For Technical Audience (Developers):**
- Distribute Python scripts
- Smaller download, easier to modify/verify

**Best of Both:**
- Provide both options in your release
- Let users choose what works for them

---

## Build Checklist

Before distributing your .exe:

- [ ] Test the .exe on a clean Windows machine (no Python installed)
- [ ] Verify all calculators launch correctly
- [ ] Check that graphs display properly
- [ ] Test comparison features
- [ ] Scan with antivirus (VirusTotal.com)
- [ ] Create a release README mentioning the .exe option
- [ ] Update forum posts with .exe download link

---

## Updating the EXE

When you make code changes:

1. Update the Python source files
2. Run `python build_exe.py` again
3. Test the new .exe
4. Increment version number
5. Release as v1.1, v1.2, etc.

---

For more information on PyInstaller, see: https://pyinstaller.org/
