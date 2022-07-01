# Glucodash
A Blood Glucose data visualization tool.



## :brain: Features
1. Calculates 16 different metrics for Blood Glucose (BG) historical data
2. Works with Abbott Freestyle Libre and Dexcom, as well as with Nightscout exports
3. Generates beutiful and interactive plots



## :mage: Basic usage
**:file_folder: Clone the repository and open it.**
```bash
git clone https://github.com/solanovisitor/Glucodash.git
cd Glucodash
```
#### Install requirements:
```bash
pip install -r requirements.txt
```
#### Run the app:
```bash
streamlit run app.py
```

#### :whale: Docker support: 
1. Install Docker and Docker Compose plugin (Docker compose does not need to be intalled separatelly anymore)
2. To build:
```bash
# Docker compose now is a plugin, not an external application
docker compose build
```
2. To run:
```bash
docker compose up
```

## Images
<img width="600" alt="Screen Shot 2022-06-28 at 15 27 35" src="https://user-images.githubusercontent.com/60658814/176256423-9f486880-499f-483b-aa1f-750053296733.png">
<img width="750" alt="Screen Shot 2022-06-28 at 16 10 35" src="https://user-images.githubusercontent.com/60658814/176265102-f46fbba2-36ef-4f40-9332-ee0cebf2d860.png">
<img width="750" alt="Screen Shot 2022-06-28 at 16 10 47" src="https://user-images.githubusercontent.com/60658814/176265466-e56c8afa-6cc7-40ac-8546-3311a2db6fcd.png">
<img width="750" alt="Screen Shot 2022-06-28 at 16 10 58" src="https://user-images.githubusercontent.com/60658814/176265527-b0518c48-756c-4c45-9229-8b413af89b7b.png">
