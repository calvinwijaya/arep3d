<img width="350" height="350" alt="logo" src="https://github.com/user-attachments/assets/2148276a-cd64-450d-b2a1-e61759996ff8" />

# AREP 3D City
AREP 3D City (Aplikasi Rekonstruksi Praktis 3D City) is personal made GUI to reconstruct 3D City model automatically. Algorithm used in the 3D city reconstruction is credited to [geoflow](https://github.com/geoflow3d/geoflow-bundle) by Ravi Peters and now Balazs Dukai from [3D Geoinformation Research Group](https://3d.bk.tudelft.nl/). For more details on how the algorithm works, please check [geoflow repo](https://github.com/geoflow3d/geoflow-bundle) and refer to their [paper](https://arxiv.org/abs/2201.01191). This is just a personal made GUI for the algorithm used for research and have fun in 3D city modeling.

## Prerequisites & Instalations
The GUI was built in Windows environment, using PyQt5 library. To use AREP 3D ensure you have a [Miniconda](https://www.anaconda.com/download) installed. To build the application, please follow steps below:
1. Install [geoflow](https://github.com/geoflow3d/geoflow-bundle/releases/download/2024.03.08/Geoflow-2024.03.08-win64.exe)
2. Clone or download this repo.
3. Open Miniconda prompt. Find the conda path:
   ```
   where conda
   ```
4. Copy the path to conda.bat to **arep3d.bat** at
   ```
   "CONDA_PATH=...\conda.bat".
   ```
5. Close the bat, then click twice on **arep3d.bat**, it will automatically create a venv called arep3d.
6. After venv created, close the prompt, then run the **arep3d.bat** again to install all requirements needed.
7. Next, just click twice **arep3d.bat** to open AREP 3D. It will skip the venv creation and library needed if previously has been installed

## How to use
AREP 3D is a simple, user friendly, and very easy to use. It is GUI based where user can load and process data by pressing button. AREP 3D takes same as Geoflow where user needs to determine:
1. Building footprint (in Shapefile/ Shp or Geopackage/ gpkg). Ensure it has fid attribute
2. Classified point cloud (in las or laz format). Ensure it has classified minimum to class 2 (ground) and 6 (building).
3. Output directory. The place where the result will be stored.
User only need to browse the location of the data. The output directory can be custom based on user. The result is 3D city model reconstructed in CityJSON format.

<img width="1920" height="1008" alt="image" src="https://github.com/user-attachments/assets/4d33139e-d200-470d-95bf-18afe2628acd" />

The 3D reconstruction result will automatically displayed in the right panel. User can navigate (pan, zoom, orbit) interactively inside to check the 3D city model reconstructed.
   
<img width="1920" height="1008" alt="image" src="https://github.com/user-attachments/assets/3140dc5f-f12b-49bb-b0c0-13991c9f930c" />
