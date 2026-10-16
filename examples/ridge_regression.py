from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import train_test_split

from mllogs import MLLogs


# ====================
# ----- Dataset -----
# ====================

X, y = load_diabetes(return_X_y=True)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# ======================
# ----- Experiment -----
# ======================

mll = MLLogs()
mll.create_experiment("ridge-regression")

for alpha in [0.01, 0.1, 1.0, 10.0]:
    with mll.run("ridge-regression"):
        model = Ridge(alpha=alpha)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        rmse = root_mean_squared_error(y_test, predictions)

        mll.log_param("alpha", alpha)
        mll.log_metric("rmse", rmse)
        mll.save_model(model)


# ===================
# ----- Results -----
# ===================

results = (
    mll.runs("ridge-regression")
    .filter("status", "COMPLETE")
    .order_by("rmse", descending=False)
    .to_df()
)

print(results)

best_run_id = results.iloc[0]["id"]
best_model = mll.load_model(best_run_id)

mll.close()
