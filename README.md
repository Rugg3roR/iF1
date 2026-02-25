# F1 Podium Prediction Model

Predicts F1 podium finishers using XGBoost.

## Setup

1. Clone the repo
2. Install dependencies:
```bash
   pip install pandas xgboost scikit-learn supabase python-dotenv
```
3. Create a `.env` file with your Supabase credentials:
```
   SUPABASE_URL=your-url-here
   SUPABASE_KEY=your-key-here
```
4. Run the model:
```bash
   python your_script.py
```

## Features

- Downloads F1 race results from Supabase (2010-2025)
- Trains XGBoost classifier
- Achieves ~0.80 ROC-AUC score
